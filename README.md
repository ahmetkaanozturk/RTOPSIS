# R-CZ-TOPSIS: Eksik Verili Çok Kriterli Karar Verme ve Dayanıklı Sıralama Motoru

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![C++: 17+](https://img.shields.io/badge/C++-17+-orange.svg)](https://en.cppreference.com/)
[![TÜBİTAK: 2209-A](https://img.shields.io/badge/TÜBİTAK-2209--A%20Uyumlu-green.svg)](https://tubitak.gov.tr/)

> **Proje Türü:** Bilimsel Araştırma Prototipi ve Dayanıklı Çok Kriterli Karar Verme (MCDM/MCDA) Karar Destek Sistemi.  
> **Temel İlke:** Değer uydurma (imputation) yapmaz; bilgi yetersizliğini ve eksik veriyi stratejik olarak modeller, alt-uzay geometrisiyle güvenilir alternatifleri adil ve denetlenebilir biçimde sıralar.

---

## 📌 Proje Özeti ve Temel Özellikler

Klasik TOPSIS ve AHP gibi Çok Kriterli Karar Verme algoritmaları, karar matrisinde eksik veri (`NaN`) bulunduğunda ortalama doldurma veya en kötü değer atama gibi yapay varsayımlara başvurur. Bu durum, stratejik bilgi gizleyen kötü alternatiflerin üst sıralara tırmanmasına yol açar.

**R-CZ-TOPSIS** şu temel yetenekleri sunar:

1. **Global Alt-Uzay TOPSIS Geometrisi ($V_{ij} = w_j \cdot r_{ij}$):**
   - Eksik kriterlerde yapay değer türetmez; yalnızca bilinen boyutların projeksiyonu üzerinde ideal ($A^+$) ve anti-ideal ($A^-$) çözümlere olan Öklid mesafelerini hesaplar.
2. **Eksiklik ve Güvenilirlik Cezalandırması ($\alpha$-Penalty & Information Entropy):**
   - Karar vericinin risk toleransına göre eksik veri barındıran alternatifleri orantılı bilgi eksikliğiyle dengeler.
3. **Kriptografik Karar Denetimi (Audit & Provenance):**
   - Karar adımları, girdi matrisleri ve ağırlık dağılımları SHA-256 / HMAC özetleriyle mühürlenir.
4. **Çift Motorlu Mimari (Dual-Engine):**
   - **Python Core:** Etkileşimli Streamlit arayüzü, veri analitiği ve görselleştirme.
   - **C++17 Core (`rcz_engine.hpp`):** Düşük gecikmeli, bellek tasarruflu ve deterministik gömülü/operasyonel hesaplama motoru.
5. **Gerçek Dünya Doğrulama Kümeleri:**
   - NASA C-MAPSS (Türbin arıza kestirimi)
   - UAV-SEAD (İHA Görev & Hava Savunma Tehdit Analizi)
   - Dünya Bankası GPPD Tedarik ve Kamu İhale benchmarkları

---

## 🚀 Hızlı Başlangıç

### 1. Bağımlılıkları Yükleme
```bash
pip install -r requirements.txt
```

### 2. Etkileşimli Dashboard'u Başlatma (Streamlit)
```bash
streamlit run dashboard.py
```

### 3. Testleri Çalıştırma
```bash
pytest test_conformance.py test_invariants.py test_enterprise_profiles.py
```

---

## 📂 Dizin Yapısı

```
PROJE/RTOPSIS/
├── src/rcz_topsis/         <- Python çekirdek algoritmaları
│   ├── core.py             <- R-CZ-TOPSIS matematiksel motoru
│   ├── audit.py            <- Kriptografik denetim ve HMAC mühürleme
│   ├── benchmark.py        <- Literatür karşılaştırma testleri
│   └── profiles/           <- Askeri ve kamu ihale senaryo profilleri
├── rcz_engine.hpp          <- C++17 Header-only yüksek performanslı motor
├── data/                   <- NASA, İHA ve Kamu İhale benchmark veri setleri
├── docs/                   <- Tehdit modelleri, mimari ve literatür taraması
├── dashboard.py            <- Streamlit web karar destek paneli
├── matematiksel_formulasyon.md <- Teoremler, ispatlar ve formüller
└── tubitak_2209_a_proje_oneri_formu.md <- TÜBİTAK proje öneri taslağı
```

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında açık kaynak olarak lisanslanmıştır.
