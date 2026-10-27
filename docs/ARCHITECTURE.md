# R-CZ-TOPSIS Yüksek Güvenceli Sistem Mimarisi (High-Assurance Architecture)

Bu doküman, R-CZ-TOPSIS çok kriterli karar destek platformunun kurumsal ihale denetimi ve askeri taktik karar destek alanlarına yönelik **ortak çekirdek + kurumsal karar destek ürün profilleri** mimarisini tanımlar.

---

## 1. Mimari Katmanlar ve Bileşen Şeması

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KULLANICI VE GÖSTERİM KATMANI                            │
│           (Streamlit Web UI / CLI / Harici C2-ERP Adaptörleri)              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Doğrulanmış Girdi / İstek
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 KURUMSAL KARAR DESTEK ÜRÜN PROFİLLERİ                       │
│  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐  │
│  │    RESMİ İHALE PROFİLİ          │   │  ASKERİ TAKTİK DANIŞMAN PROFİLİ │  │
│  │  - İki Kişili Komisyon Onayı    │   │  - Kesin Otonomi Yasağı (Advisory)│
│  │  - Fiyat Gizleme Savunma Bayrağı│   │  - Telemetri Tazeliği & Bayatlık│  │
│  │  - Yakın Skor İnceleme Tutanağı │   │  - Jammer Karartmasında Graceful │  │
│  │  - 4734 Süreç Kontrol Listesi   │   │  - Fail-Closed Güvenli Duruş     │  │
│  └─────────────────────────────────┘   └─────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Sözleşme Şeması (DecisionDataset)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ORTAK ÇEKİRDEK KARAR MOTORU (CANONICAL CORE)                │
│                           (src/rcz_topsis/core.py)                          │
│  - Katı Girdi Doğrulama (NaN/inf reddi, m>=2, n>=1, Sigma='A'/'I')          │
│  - Sütun Normu S_j (Aktif Gözlemler)                                         │
│  - Global Ağırlıklandırma V_ij = w_j * (x_ij / S_j)                         │
│  - Alt-Uzay İdeal Noktaları (v+, v-) & Mesafeler (D+, D-)                   │
│  - Hard Gatekeeper Barajı (W_i >= 0.50, m_i* >= 2)                           │
│  - Asimetrik Maliyet/Risk Cezası: Gamma_i = W_i^(alpha * kappa_i)            │
│  - Deterministik Sıralama & Bounded Skor C* in [0.0, 1.0]                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Kriptografik Olaylar & Makbuz
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 GÜVENLİK VE DEĞİŞTİRİLEMEZ DENETİM KATMANI                   │
│                         (src/rcz_topsis/audit.py)                           │
│  - Kriptografik SHA-256 Hash Zinciri (AuditHashChain)                       │
│  - Girdi, Konfigürasyon ve Çıktı Bütünlük Mührü (IntegrityReceipt)          │
│  - Kurum İçi İnceleme İçin Dışa Aktarılabilir JSON İzi (sertifika değil)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Temel İlkeler ve Güvence Kısıtları

### 2.1. İnsan Karar Verici Üstünlüğü (Human-in-the-Loop)
* **İhale:** Sistem yüklenici seçmez veya ihaleyi sonuçlandırmaz. Yalnızca komisyon üyelerine gerekçeli karşılaştırma ve inceleme önerisi sunar.
* **Savunma/C2:** Sistem hiçbir koşulda otonom angajman, silah tahsisi veya ateşleme kararı vermez (`AUTONOMOUS_ENGAGEMENT_ALLOWED = False`). Operatöre tehdit seviyesi ve sensör güvenilirliği danışmanlığı verir.

### 2.2. Veri Bütünlüğü ve Denetim İzi (Tamper-Evidence)
* Her hesaplama öncesinde `DecisionDataset.compute_sha256()` ile veri dondurulur.
* Her hesaplama sonucunda `IntegrityReceipt` oluşturularak girdinin, motor parametrelerinin ve sıralamanın birleşik SHA-256 özeti üretilir.
* Operatör kimliği ve oturum kayıtları tek yönlü hash zincirine eklenir.

### 2.3. Sayısal Kararlılık ve Taşınabilirlik
* Motor tamamen **yerel (on-premise / air-gapped)** çalışmaya uygundur; harici internet veya bulut API bağımlılığı yoktur.
* $O(N \times M)$ deterministik zaman karmaşıklığı ile bellek ve işlemci üzerinde öngörülebilir kaynak tüketir.
