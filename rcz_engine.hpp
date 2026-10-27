// ==============================================================================
// R-CZ-TOPSIS v1.1 — DENEYSEL C++20 PORTU (EXPERIMENTAL EMBEDDED PROTOTYPE)
// ==============================================================================
// Kanonik Referans: src/rcz_topsis/core.py
// 
// ÖNEMLİ METODOLOJİK SINIRLAMA & UYARI:
// 1. Bu başlık dosyası gömülü sistemler için dinamik bellek tahsisi yapmayan (allocation-free)
//    kavramsal bir prototiptir.
// 2. Python referans çekirdeğindeki (src/rcz_topsis/core.py) katı girdi doğrulamaları (NaN/inf denetimi,
//    negatif ağırlık istisnası, threshold_tol aralık doğrulaması vb.) noexcept kısıtları nedeniyle
//    bu C++ portunda birebir uygulanmamıştır; ağırlık toplamı yetersizse eşit ağırlık fallback'i uygular.
// 3. Geliştirme ortamında C++ derleyicisi bulunmadığından henüz derlenip Python sürümüyle
//    sayısal/istatistiksel denkliği doğrulanmamıştır.
// 4. Kritik karar destek süreçlerinde resmi kanonik Python çekirdeği kullanılmalıdır.
// ==============================================================================
#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>

namespace rcz {

enum class Context : uint8_t { ACTION = 0, INACTION = 1 };
enum class CritType : uint8_t { BENEFIT = 0, COST = 1 };
enum class AlternativeStatus : uint8_t { EVALUATED = 0, INSUFFICIENT_DATA = 1 };

struct AlternativeResult {
    size_t index{0};
    double score{0.0};          // C*
    double base_score{0.0};     // C_base
    double support_weight{0.0}; // W_i
    double penalty_gamma{0.0};  // Gamma_i
    uint32_t active_count{0};   // m_i*
    AlternativeStatus status{AlternativeStatus::INSUFFICIENT_DATA};
    uint32_t rank{0};
};

struct RCZConfig {
    double w_threshold{0.50};
    uint32_t min_active_criteria{2};
    double alpha{0.50};
    double eps{1e-12};
    bool local_reweighting{false};  // v1.0 davranışı, yalnızca karşılaştırma için
    double threshold_tol{1e-9};
};

template <size_t N, size_t M>
class RCZTOPSIS {
    static_assert(N > 0, "Alternatif sayisi en az 1 olmalidir.");
    static_assert(M >= 2, "Kriter sayisi en az 2 olmalidir.");

public:
    constexpr explicit RCZTOPSIS(RCZConfig config = {}) : config_(config) {}

    [[nodiscard]] std::array<AlternativeResult, N> fit_predict(
        const std::array<std::array<double, M>, N>& X,
        const std::array<std::array<Context, M>, N>& Sigma,
        const std::array<double, M>& weights_raw,
        const std::array<CritType, M>& crit_types) const noexcept {
        std::array<AlternativeResult, N> res{};

        // 0. Ağırlık normalizasyonu
        double w_total = 0.0;
        for (size_t j = 0; j < M; ++j) w_total += weights_raw[j];
        std::array<double, M> w{};
        for (size_t j = 0; j < M; ++j) w[j] = (w_total > config_.eps) ? weights_raw[j] / w_total : 1.0 / M;

        // 1. Sütun norm paydaları (yalnızca ACTION)
        std::array<double, M> S{};
        for (size_t j = 0; j < M; ++j) {
            double ss = 0.0;
            for (size_t i = 0; i < N; ++i)
                if (Sigma[i][j] == Context::ACTION) ss += X[i][j] * X[i][j];
            S[j] = (ss > 0.0) ? std::sqrt(ss) : 1.0;
        }

        // 2. Kapsama ve Hard Gatekeeper
        std::array<bool, N> valid{};
        for (size_t i = 0; i < N; ++i) {
            double cov = 0.0;
            uint32_t cnt = 0;
            for (size_t j = 0; j < M; ++j)
                if (Sigma[i][j] == Context::ACTION) { cov += w[j]; ++cnt; }
            res[i].index = i;
            res[i].support_weight = cov;
            res[i].active_count = cnt;
            valid[i] = (cov >= config_.w_threshold - config_.threshold_tol) && (cnt >= config_.min_active_criteria);
            res[i].status = valid[i] ? AlternativeStatus::EVALUATED : AlternativeStatus::INSUFFICIENT_DATA;
        }

        // 3. V matrisi (global ağırlık; isteğe bağlı yerel ağırlık)
        std::array<std::array<double, M>, N> V{};
        for (size_t i = 0; i < N; ++i) {
            if (!valid[i]) continue;
            const double scale = (config_.local_reweighting && res[i].support_weight > config_.eps)
                                     ? 1.0 / res[i].support_weight : 1.0;
            for (size_t j = 0; j < M; ++j)
                if (Sigma[i][j] == Context::ACTION) V[i][j] = w[j] * scale * X[i][j] / S[j];
        }

        // 4. İdeal ve anti-ideal noktalar
        std::array<double, M> vp{}, vm{};
        for (size_t j = 0; j < M; ++j) {
            bool found = false;
            double mx = 0.0, mn = 0.0;
            for (size_t i = 0; i < N; ++i) {
                if (!valid[i] || Sigma[i][j] != Context::ACTION) continue;
                if (!found) { mx = mn = V[i][j]; found = true; }
                mx = std::max(mx, V[i][j]);
                mn = std::min(mn, V[i][j]);
            }
            if (crit_types[j] == CritType::BENEFIT) { vp[j] = mx; vm[j] = mn; }
            else { vp[j] = mn; vm[j] = mx; }
        }

        // 5. Alt-uzay mesafeleri, asimetrik ceza, skor
        for (size_t i = 0; i < N; ++i) {
            if (!valid[i]) continue;
            double dp2 = 0.0, dm2 = 0.0, missing_cost = 0.0;
            for (size_t j = 0; j < M; ++j) {
                if (Sigma[i][j] == Context::ACTION) {
                    dp2 += (V[i][j] - vp[j]) * (V[i][j] - vp[j]);
                    dm2 += (V[i][j] - vm[j]) * (V[i][j] - vm[j]);
                } else if (crit_types[j] == CritType::COST) {
                    missing_cost += w[j];
                }
            }
            const double dp = std::sqrt(dp2), dm = std::sqrt(dm2);
            const double c_base = (dp + dm < config_.eps) ? 0.5 : dm / (dp + dm);
            const double gamma = std::pow(res[i].support_weight, config_.alpha * (1.0 + missing_cost));
            res[i].base_score = c_base;
            res[i].penalty_gamma = gamma;
            res[i].score = c_base * gamma;
        }

        // 6. Sıralama (geçerliler önce, skora göre; eşitlikte kapsama)
        std::array<size_t, N> order{};
        for (size_t i = 0; i < N; ++i) order[i] = i;
        std::stable_sort(order.begin(), order.end(), [&](size_t a, size_t b) {
            if (res[a].status != res[b].status) return res[a].status < res[b].status;
            if (res[a].score != res[b].score) return res[a].score > res[b].score;
            return res[a].support_weight > res[b].support_weight;
        });
        for (size_t r = 0; r < N; ++r) res[order[r]].rank = static_cast<uint32_t>(r + 1);
        return res;
    }

private:
    RCZConfig config_;
};

}  // namespace rcz

