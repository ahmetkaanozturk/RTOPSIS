# R-CZ-TOPSIS Tehdit Modeli ve Güvenlik Analizi (Threat Model)

Bu doküman, R-CZ-TOPSIS platformunun kurumsal ihale denetimi ve askeri karar destek operasyonlarında karşılaşabileceği siber, algoritmik ve operasyonel tehditleri analiz eder.

---

## 1. Korunan Varlıklar (Assets)
1. **Karar Girdileri:** Firma teklif fiyatları, teknik spekler, taktik radar izleri ve sensör telemetrisi.
2. **Kriter Ağırlıkları & Parametreler:** Önceden belirlenmiş şartname ağırlıkları ($w_j$) ve asgari bilgi eşiği ($W_{\text{threshold}}$).
3. **Çıktı Bütünlüğü:** Nihai sıralama skoru ($C^*$), podyum dereceleri ve komisyon tavsiye raporu.
4. **Denetim İzi (Audit Log):** Kimin, ne zaman, hangi yetkiyle ve hangi veriyle hesaplama yaptığına dair tarihsel kanıtlar.

---

## 2. Tehdit Aktörleri ve Saldırı Senaryoları

### Tehdit 1: Maliyet/Fiyat Gizleyerek Avantaj Elde Etme (Cost-Hiding Attack)
* **Senaryo:** Kötü niyetli bir tedarikçi, aşırı yüksek fiyatını veya arıza oranını gizleyerek ($0_I$) Klasik TOPSIS'te bedava kabul edilip 1. sıraya yerleşmeyi hedefler.
* **Uygulanan Savunma:**
  - Asimetrik ceza üssü ($\kappa_i = 1.0 + \sum_{\text{Cost}} w_j$) adayın $\Gamma_i$ güvenilirlik çarpanını düşürür.
  - İhale profili, eksik maliyet kriteri olan teklifleri otomatik olarak `KOMISYON_SAVUNMA_TALEBI_GEREKLI` statüsüne alır; otomatik ihale alımı idari olarak engellenir.

### Tehdit 2: Karar Matrisi veya Ağırlıkların Tahrif Edilmesi (Data Tampering)
* **Senaryo:** Yetkisiz bir personel veya kötü niyetli operatör, hesaplama sonrasında Excel/CSV veya ağırlık değerlerini değiştirip farklı bir adayı kazandırmaya çalışır.
* **Uygulanan Savunma:**
  - `DecisionDataset.compute_sha256()` hesaplama anında matrisin ve ağırlıkların SHA-256 özetini çıkarır.
  - `IntegrityReceipt` oluşturulup rapor içine mühürlenir. Girdideki tek bir basamak dahi değişse hash uyuşmazlığı tespit edilir.
  - `AuditHashChain` tek yönlü hash zinciriyle kayıt tutar; geriye dönük log silinmesi veya değiştirilmesi anında `verify_integrity() == False` verir.

### Tehdit 3: Elektronik Harp ve Sensör Karartması (Denial of Measurement / Jamming)
* **Senaryo:** Düşman elektronik taarruz ile taktik radar veya ESM sensörlerini körleştirerek sistemin çökmesini veya körlemesine yanlış angajman yapmasını amaçlar.
* **Uygulanan Savunma:**
  - Alt-uzay izdüşümü: Sistem aktif kalan optik/termal sensörlerin alt-uzayında çalışmayı sürdürür.
  - Hard Gatekeeper: Bilgi kapsama oranı %50'nin altına düşen temaslar `BILGI_YETERSIZ_KARARTMA` statüsüne alınarak fail-closed duruş sağlanır; körlemesine otomatik angajman engellenir.

### Tehdit 4: Tek Kişinin İhale Manipülasyonu (Insider Threat)
* **Senaryo:** Tek bir kullanıcının kendi inisiyatifiyle ağırlıkları kaydırarak rapor üretmesi.
* **Uygulanan Savunma:**
  - İhale profilinde **İki Kişili Onay Kuralı (Two-Person Commission Rule)** zorunludur. Komisyon başkanı ve mali denetçi farklı kimliklerle oturum onaylamadan resmi çıktı üretilmez.

### Tehdit 5: Ağ İçi Veri Sızıntısı ve Dış İletişim (Exfiltration Risk)
* **Senaryo:** Hassas teklif veya radar verisinin internete sızması.
* **Uygulanan Savunma:**
  - Sistem harici hiçbir telemetri, bulut veya analitik servisi çağırmaz.
  - Taşınabilir on-premise ve air-gapped ortamlarda ağ izolasyonu altında çalışır.

