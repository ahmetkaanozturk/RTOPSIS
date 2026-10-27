# R-CZ-TOPSIS Sistematik Literatür Taraması

**Faz:** 1 — protokol ve ön tarama  
**Tarih:** 2026-10-14  
**Kapsam:** TOPSIS/MCDM'de eksik, kısmi, belirsiz veya güvenilmez veri; imputasyonsuz sıralama; alternatif-spesifik kriter altuzayı; bilgi kapsamı eşikleri; eksikliği yön/kriter türüne göre cezalandırma.

## 1. Tarama protokolü

### Araştırma soruları

1. Eksik veri içeren MCDM/TOPSIS problemleri literatürde hangi yöntemlerle ele alınmıştır?
2. R-CZ-TOPSIS'in şu bileşenleri daha önce ayrı ayrı veya birlikte önerilmiş midir?
   - ölçülmüş gerçek sıfır ile eksik/ölçülmemiş durumun ayrılması (`0_A` / `0_I`);
   - alternatifin gözlenen kriter altuzayında TOPSIS mesafesi;
   - global kriter ağırlıklarının altuzayda kullanılması;
   - minimum bilgi kapsamı için sert geçerlilik kapısı;
   - fayda ve maliyet kriterlerinin eksikliğine farklı/asimetrik ceza.
3. `R-CZ-TOPSIS` ve `Contextual Zero Algebra` adları için bağımsız ve doğrulanabilir bir yayın kaydı var mıdır?

### Arama yaklaşımı

Faz 1'de 2010–2026 dönemi önceliklendirildi; TOPSIS'in temel kaynakları ve ilgili istatistik/karar teorisi kaynakları karşılaştırma tabanı olarak eklendi. Arama ifadeleri şunları kapsadı:

- `TOPSIS missing values multi-criteria decision making`
- `incomplete information TOPSIS`
- `imputation-free multi-criteria decision making`
- `subspace TOPSIS missing data`
- `alternative-specific criteria TOPSIS`
- `asymmetric missingness penalty MCDM`
- `Contextual Zero Algebra`
- `R-CZ-TOPSIS`

Kaynak, DOI veya kalıcı URL ile doğrulanamadığında yöntemsel kanıt olarak kabul edilmedi. Review makaleleri literatür haritası olarak tutuldu; özgün yöntem iddiaları için birincil yayın aranması kuralı uygulandı.

### Dahil etme ölçütleri

- TOPSIS veya MCDM karar matrisiyle doğrudan ilişkili olması,
- eksik/kısmi/belirsiz/güvenilmez bilgi işleme yöntemi sunması veya temel TOPSIS formülasyonunu tanımlaması,
- DOI, Springer/Elsevier/IEEE kaydı veya güvenilir kalıcı bibliyografik kayıtla doğrulanabilmesi.

### Dışlama ölçütleri

- yalnızca standart TOPSIS uygulaması olup eksikliği yöntemsel olarak ele almayan çalışmalar,
- eksikliği yalnızca ön işleme olarak silen veya dolduran uygulamalar,
- yalnızca bulanık belirsizlik içeren, gerçek eksik hücreyi ayrı modellemeyen çalışmalar,
- doğrulanabilir bibliyografik kaydı olmayan iddialar.

## 2. Faz 1 dahil edilen kaynaklar

| Kaynak | Eksik/belirsiz veri yaklaşımı | R-CZ ile ilişki |
|---|---|---|
| Hwang & Yoon (1981), *Methods for Multiple Attribute Decision Making*. Springer. [doi:10.1007/978-3-642-48318-9_3](https://doi.org/10.1007/978-3-642-48318-9_3) | Klasik TOPSIS; tam karar matrisi, ideal/anti-ideal ve ağırlıklı uzaklık temeli. | Global ağırlıklı uzaklığın temelidir; eksik veri bileşeni yoktur. |
| Lai, Liu & Hwang (1994), “TOPSIS for MODM,” *European Journal of Operational Research*, 76(3), 486–500. [doi:10.1016/0377-2217(94)90282-8](https://doi.org/10.1016/0377-2217(94)90282-8) | Çok amaçlı TOPSIS formülasyonu. | Ağırlıklı ideal/anti-ideal uzaklık temeli; eksik veri modeli yoktur. |
| Chen (2000), “Extensions of the TOPSIS for Group Decision-Making under Fuzzy Environment,” *Fuzzy Sets and Systems*, 114(1), 1–9. [doi:10.1016/S0165-0114(97)00377-1](https://doi.org/10.1016/S0165-0114(97)00377-1) | Belirsizliği bulanık sayılarla temsil eder. | Belirsizlik temsiline komşudur; `0_A/0_I`, altuzay ve asimetrik ceza yoktur. |
| Ben Othman & Ben Yahia (2018), “A Multiple Criteria Evaluation Technique for Missing Values Imputation,” IEEE RCIS. [doi:10.1109/RCIS.2018.8406659](https://doi.org/10.1109/RCIS.2018.8406659) | İmputasyon yöntemlerini MCDM/TOPSIS ile değerlendirir. | Eksik veri ve ağırlıklandırma bağlantısı vardır; imputasyonsuz sıralama yapmaz. |
| Mahmoudi, Deng, Javed & Yuan (2021; online 2020), “Large-Scale Multiple Criteria Decision-Making with Missing Values: Project Selection through TOPSIS-OPA,” *Journal of Ambient Intelligence and Humanized Computing*, 12, 9341–9362. [doi:10.1007/s12652-020-02649-w](https://doi.org/10.1007/s12652-020-02649-w) | PCA/k-means, Fuzzy TOPSIS ve OPA ile eksik bilgili büyük ölçekli proje seçimi. | Eksikliği tolere eder; R-CZ altuzay mesafesi ve asimetrik ceza yoktur. |
| De Tré, De Mol & Bronselaer (2018), “Handling Veracity in Multi-Criteria Decision-Making: A Multi-Dimensional Approach,” *Information Sciences*, 460–461, 541–554. [doi:10.1016/j.ins.2017.09.008](https://doi.org/10.1016/j.ins.2017.09.008) | Bilginin doğruluk/veracity boyutunu karar modeline ekler. | `0_A/0_I` ve bilgi kalitesi ayrımına kavramsal olarak en yakın kaynaklardan biridir; R-CZ formülünü kullanmaz. |
| Taherdoost & Madanchian (2024), “A Comprehensive Survey and Literature Review on TOPSIS,” *International Journal of Service Science, Management, Engineering, and Technology*, 15(1). [doi:10.4018/IJSSMET.347947](https://doi.org/10.4018/IJSSMET.347947) | TOPSIS uygulama ve uzantılarını derler. | Literatür haritasıdır; yeni eksik veri algoritması değildir. |
| “A Review on TOPSIS Method and Its Extensions for Different Applications with Recent Development” (2023), *Soft Computing*, 27, 18011–18039. [doi:10.1007/s00500-023-09011-0](https://doi.org/10.1007/s00500-023-09011-0) | TOPSIS uzantılarını ve belirsizlik modellerini derler. | R-CZ bileşenlerinin literatürdeki komşu alanlarını belirlemek için kullanılır. |

## 3. Faz 1 sentezi

| R-CZ bileşeni | En yakın doğrulanabilir karşılık | Faz 1 sonucu |
|---|---|---|
| `0_A` / `0_I` durum ayrımı | De Tré vd. bilgi doğruluğu/veracity boyutu; bulanık/interval TOPSIS | Kavramsal komşuluk bulundu; aynı durum modeli doğrulanmadı. |
| Gözlenen kriter altuzayında TOPSIS | Klasik TOPSIS uzaklık yapısı; Mahmoudi vd. eksik bilgi bağlamı | Aynı bileşim ve formül doğrulanmadı. |
| Global ağırlıklar | Klasik TOPSIS ve tüm ana uzantılar | Yeni değildir; R-CZ'nin özgünlüğü bu bileşen olamaz. |
| Coverage gate | Eksikliği tolere eden MCDM ve kalite ölçütleri | TOPSIS'e aynı sert eşik formunda doğrudan eşleşme bulunmadı. |
| Asimetrik fayda/maliyet eksikliği cezası | Veracity ve asimetrik bilgi kavramları | Aynı `W_i`, `kappa_i`, `Gamma_i` formu doğrulanmadı. |

### Geçici sonuç

Faz 1 taramasında, `0_A/0_I` ayrımı + imputasyonsuz gözlenen altuzay TOPSIS'i + global ağırlık kullanımı + coverage gate + fayda/maliyet yönüne duyarlı asimetrik ceza bileşimini aynı doğrulanabilir TOPSIS yöntemi olarak sunan bağımsız bir kaynak bulunmadı.

Bu sonuç “dünyada kesinlikle yoktur” anlamına gelmez. Tarama; Scopus/Web of Science/Dimensions gibi abonelikli indekslerde tam sorgu dışa aktarımı, tezler, preprint depoları ve tüm referans zincirlerinin ikinci faz doğrulamasını henüz içermemektedir. Bu nedenle mevcut ifade **“Faz 1 taramasında saptanmadı”** olmalıdır.

`Contextual Zero Algebra` ve `R-CZ-TOPSIS` için bu fazda bağımsız DOI, hakemli makale, kitap bölümü veya konferans bildirisi bulunmadı. Bu adlar proje içi çalışma adlarıdır; yerleşik teori olarak yazılmamalıdır.

## 4. Faz 2 planı ve Bileşen Matrisi

### 4.1. Veritabanı Sorguları ve Çift Kayıt Birleştirme (Deduplication)

Faz 2'de Scopus, Web of Science, Dimensions ve OpenAlex API/exportları üzerinde aşağıdaki standartlaştırılmış boolean sorgu protokolü yürütülür:

```text
TITLE-ABS-KEY ( ("TOPSIS" OR "MCDM" OR "multi-criteria") AND ("missing data" OR "incomplete information" OR "unobserved criteria") AND ("subspace" OR "imputation-free" OR "penalty" OR "veracity") )
```

**Deduplication (Tekilleştirme) Adımları:**
1. DOI bazlı kesin eşleştirme (`exact DOI match`).
2. DOI bulunmayan kayıtlarda küçük harfe indirgenmiş ve noktalama işaretleri temizlenmiş `title` + ilk yazar soyadı + yayın yılı üzerinden Levenshtein mesafesi ($< 0.05$) denetimi.
3. Hakemli dergi makaleleri, konferans tam metinleri ve saygın preprint arşivleri (arXiv, SSRN) ayrı kategorilerde etiketlenir.

### 4.2. Sistematik Literatür Bileşen Matrisi (Component Matrix)

R-CZ-TOPSIS modelinin dört temel yapıtaşı ile literatürdeki başlıca yaklaşımların karşılaştırması:
- **OS (Observed Subspace):** Alternatifin yalnızca gözlemlenen kriter altuzayında yapay değer uydurmadan (imputation-free) izdüşüm mesafesi.
- **CG (Coverage Gate):** Bilgi kapsamı $W_i$ veya aktif kriter sayısı $m_i^*$ için sert düzenleyici asgari eşik (Hard Gatekeeper).
- **AP (Asymmetric Penalty):** Fayda ve maliyet eksikliğini bilgi asimetrisi (Akerlof Limon etkisi) uyarınca asimetrik çarpanla ($\Gamma_i = W_i^{\alpha \cdot \kappa_i}$) cezalandırma.
- **0_A / 0_I:** Ölçülmüş gerçek sıfır ($0_A$) ile ölçülmemiş/eksik bilgi ($0_I$) durumlarının cebirsel ayrımı.

| Çalışma / Yaklaşım | OS | CG | AP | 0_A / 0_I | Açıklama ve Metodolojik Sınır |
|---|:---:|:---:|:---:|:---:|---|
| Hwang & Yoon (1981) | ❌ | ❌ | ❌ | ❌ | Klasik TOPSIS; matrisin tam olmasını şart koşar, eksik hücrede çöker veya naif sıfır kabul eder. |
| Chen (2000) Fuzzy TOPSIS | ❌ | ❌ | ❌ | ❌ | Belirsizliği bulanık üyelik fonksiyonu ile modeller; yapısal eksik veriyi doğrudan altuzayda çözmez. |
| Little & Rubin (2019) / Imputation | ❌ | ❌ | ❌ | ❌ | Eksik hücrelere yapay değer atar (Mean, MICE, kNN). Matris varyansını yapay olarak bozar, manipülasyonu ödüllendirebilir. |
| Ben Othman & Ben Yahia (2018) | ❌ | ❌ | ❌ | ❌ | İmputasyon yöntemlerinin kalitesini TOPSIS ile değerlendirir; kararı imputasyonsuz çözmez. |
| Mahmoudi vd. (2021) TOPSIS-OPA | 🟡 | ❌ | ❌ | ❌ | Büyük ölçekte eksikliği tolere eder (kümeleme/bulanık); sert baraj kapısı veya asimetrik maliyet cezası içermez. |
| De Tré vd. (2018) Veracity MCDM | ❌ | 🟡 | 🟡 | 🟡 | Bilgi güvenilirliğini ve kalitesini çok boyutlu olarak modele katar. Kavramsal olarak en yakın çalışmadır; ancak TOPSIS altuzay ve $\Gamma_i$ formülü yoktur. |
| **R-CZ-TOPSIS v1.1 (Bu Çalışma)** | ✅ | ✅ | ✅ | ✅ | Dört bileşeni kanonik global ağırlıklandırma ($V_{ij} = w_j \cdot r_{ij}$) altında birleştiren ilk doğrulanabilir implementasyon (Faz 1 taramasında eşleniği saptanmadı). |

*Not:* Tablodaki "Faz 1 taramasında saptanmadı" ifadesi temkinli bilimsel metodoloji gereğidir; Faz 2 sistematik taraması tamamlanana kadar mutlak iddia yerine temkinli sentez korunur.

## 6. Gerçek kurumsal veri doğrulama hatları

Proje iki ayrı gerçek-veri hattı için kaynak sözleşmesi ve provenance adaptörü içerir:

1. **Kamu ihale hattı:** TED Open Data birincil kaynak, World Bank GPPD sistem düzeyi yardımcı kaynak.
2. **Mühendislik/risk hattı:** NASA Prognostics Data Repository birincil kaynak, NREL/DOE EV filo verisi yardımcı kaynak.

Kaynak kayıtları [EXTERNAL_DATA_SOURCES.json](../data/EXTERNAL_DATA_SOURCES.json) içindedir.
Kod adaptörü [external_data.py](../src/rcz_topsis/external_data.py) ile:

- yerel indirilen CSV'nin SHA-256 özeti,
- yayıncı, URL ve lisans,
- satır/sütun sayısı,
- eksik hücre sayısı,
- eksikliğin gözlenen mi yoksa enjekte mi olduğu,
- sonuç/etiket tanımı

provenance kaydına alınır.

Bu hatlar veri indirilmiş gibi davranmaz ve kaynak veriyi “kurumsal karar etiketi”
olarak uydurmaz. TED'de award/contract kaydı yoksa geçmiş karar sonucu yoktur;
NASA veri setinde doğal eksiklik belgelenmemişse maske yalnızca `injected` olarak
etiketlenebilir. Ham indirme, lisans ve erişim tarihi ayrıca kayıt altına alınmalıdır.

## 5. Kodlanmış karşılaştırma kapsamı

Benchmark'a doğrudan ve şeffaf biçimde yeniden üretilebilen iki eksik-veri
karşılaştırıcısı eklenmiştir:

- `klasik_en_kotu`: eksik fayda hücresini gözlenen minimum, eksik maliyet
  hücresini gözlenen maksimum ile dolduran ihtiyatlı stres baseline'ı.
- `topsis_yerel`: her alternatifin gözlenen kriterlerinde ağırlıkları yeniden
  normalize eden observed-subspace TOPSIS baseline'ı; coverage gate ve
  epistemik ceza içermez.

Bu iki baseline belirli bir makalenin birebir kodu olarak sunulmaz. Literatürdeki
yakın fikirleri kontrollü karşılaştırmak için açık formüllü deney referanslarıdır.
Mahmoudi ve arkadaşlarının Fuzzy TOPSIS-OPA yöntemi ile Ben Othman–Ben Yahia'nın
imputasyon değerlendirme yöntemi henüz bu prototipte birebir uygulanmış değildir;
bunlar uygulanmış sonuç tablosuna yöntem adı olarak eklenmemelidir.

Benchmark sonuçları artık yöntemleri aynı tekrar içindeki gözlemlerle eşleştirerek
R-CZ'ye göre paired farkları da raporlar: ortalama `rho`/`tau` farkı, yüzde 2.5–97.5
bootstrap güven aralığının alt/üst sınırları ve iki taraflı paired sign-flip randomization
p-değeri. Bu istatistikler
sentetik missingness protokolündeki yöntem farkını ölçer; gerçek veri genellemesi veya
nedensel üstünlük kanıtı değildir. Aynı missingness mekanizması içindeki yöntem ve kayıp
oranı karşılaştırmalarında p-değerleri Holm step-down yöntemiyle düzeltilir; düzeltme
istatistiksel anlamlılığı garanti etmez ve pratik etki büyüklüğünün ayrıca incelenmesi gerekir.
