# Dış Veri Edinimi, Provenance ve Doğrulama Protokolü

**Tarih:** 2026-10-14  
**Standart:** Sıfır Uydurma İlkesi (Zero Fabrication Policy) & Kriptografik Provenance Takibi (SHA-256)

---

## 1. Veri Edinimi Durumu Özeti

Projede kullanılan ve hedeflenen 4 kurumsal açık veri hattının güncel erişim ve doğrulama durumu [`data/EXTERNAL_ACQUISITION_STATUS.json`](../data/EXTERNAL_ACQUISITION_STATUS.json) dosyasında kayıtlıdır:

| Veri Kaynağı | Yayıncı Kuruluş | Edinme Durumu | Yerel Dosyalar | Provenance & Doğrulama Durumu |
|---|---|:---:|---|---|
| **TED Open Data** | Publications Office of the European Union | ✅ Aktarıldı | `data/ted_sample.csv` | 100 resmi ihale duyurusu; SPARQL API üzerinden çekildi. Prosedür ve bildirim kapsamı özeti. Tedarikçi award sonucu içermez. |
| **NASA C-MAPSS FD001** | NASA PCoE (Prognostics Center of Excellence) | ✅ Aktarıldı (Ayna) | `data/nasa_cmapss_fd001_decision_matrix.csv`<br>`data/nasa_cmapss_fd001.csv` | NASA'nın resmi portalı geçici olarak erişime kapalı olduğundan, commit'i sabitlenmiş açık ayna kullanıldı. 100 test motoru, 6 doğrulanmış kriter ve bağımsız `rul` etiketi mevcuttur. |
| **World Bank GPPD** | Dünya Bankası | ⚠️ Bağlantı Kapalı | — | Katalog kaydı mevcuttur; ancak daha önce belgelenmiş XLSX doğrudan indirme bağlantısı `Azure BlobNotFound` hatası vermektedir. Yerine yapay veri uydurulmamıştır. |
| **NREL EV Fleet** | NREL / U.S. Dept. of Energy | ⚠️ İndirme Yok | — | Tarihsel OpenEI sayfası (8311) "no data" vermekte; yeni katalogda doğrudan indirilebilir stabil dosya bulunamamıştır. Yapay veri üretilmemiştir. |

---

## 2. Kriptografik Provenance ve Doğrulama Sözleşmesi

Sisteme dahil edilen her dış veri dosyası, [`src/rcz_topsis/external_data.py`](../src/rcz_topsis/external_data.py) modülü tarafından aşağıdaki sözleşmeye bağlanır:

```python
@dataclass(frozen=True)
class ProvenanceRecord:
    source_id: str                          # Kaynak benzersiz kimliği (ted_open_data, nasa_phm, vb.)
    local_path: str                         # Yerel dosya konumu
    source_url: str                         # İndirildiği kesin URL veya endpoint
    publisher: str                          # Resmi yayıncı kurum
    license: str                            # Açık veri lisansı ve kullanım şartları
    accessed_at_utc: str                    # UTC zaman damgası
    sha256: str                             # Kriptografik SHA-256 dosya özeti
    row_count: int                          # Satır sayısı
    column_count: int                       # Sütun sayısı
    missing_cells: int                      # Boş / NaN hücre sayısı
    missingness_observed_or_injected: str   # 'observed', 'injected', 'mixed'
    outcome_definition: str                 # Sonuç / etiket tanımı (RUL, award, yok)
```

### Sıfır Uydurma İlkesi (Zero Fabrication Pledge)
Resmi kaynaktan doğrudan indirilemeyen veya erişimi kesilen hiçbir veri seti için:
1. Yapay / sentetik rastgele veri üretilip "resmi veri" olarak sunulmaz.
2. Karar vericiye veya hakemlere eksik bir dış veri tam gibi gösterilmez.
3. İhale verisinde award (kazanan) bilgisi yoksa "kazananı doğru bildi" şeklinde yapay bir doğrulama iddiası kurulmaz.

---

## 3. Harici Veri Manuel İçe Aktarma Rehberi (Manual Ingest)

Eğer bir hakem, denetçi veya araştırmacı elinde bulunan Dünya Bankası GPPD veya NREL EV veri setini sisteme aktarmak isterse, aşağıdaki script ile otomatik hash'leme ve provenance oluşturabilir:

```python
from pathlib import Path
from src.rcz_topsis.external_data import build_provenance, save_provenance

# Örnek: Yerel GPPD CSV dosyasını aktarma
csv_path = Path("data/world_bank_gppd_custom.csv")
record = build_provenance(
    source_id="world_bank_gppd",
    local_path=csv_path,
    missingness_observed_or_injected="observed",
    outcome_definition="Ulusal ihale sistemi performans göstergeleri (tedarikçi award etiketi içermez)",
    acquisition_url="https://datacatalog.worldbank.org/search/dataset/0038958/global-public-procurement-database",
)

# Provenance dosyasını kaydet
save_provenance(record, Path("data/world_bank_gppd_custom.provenance.json"))
print(f"Başarıyla kaydedildi. SHA-256: {record.sha256}")
```

---

## 4. Karar Matrisi Dönüşümü ve Domain Doğrulaması

İçe aktarılan her dış tablo [`to_decision_matrix`](../src/rcz_topsis/external_data.py) fonksiyonundan geçirilir:
- Sayısal olmayan, eksik veya geçersiz hücreler Contextual Zero cebirinin `0_I` (Inaction) bağlamına atanır.
- Gerçek ölçülmüş sıfırlar `0_A` (Action) olarak korunur.
- Kriter yönleri (Fayda / Maliyet) rastgele değil, alan mühendisliği kurallarına göre (örn. turbofan gaz sıcaklıkları = Maliyet) tanımlanır.

