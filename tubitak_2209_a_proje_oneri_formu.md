# TÜBİTAK 2209-A BİLİMSEL VE TEKNOLOJİK ARAŞTIRMA PROJELERİ DESTEKLEME PROGRAMI
## PROJE ÖNERİ FORMU

---

### PROJE BİLGİLERİ

* **Proje Başlığı:** Eksik ve Belirsiz Veri Koşullarında Karar Destek Sistemleri İçin Bağlamsal Sıfır Cebiri (CZ-Algebra) Tabanlı TOPSIS Algoritmasının Geliştirilmesi, Simülasyonu ve Karşılaştırmalı Analizi
* **Proje Yürütücüsü:** [Adınız Soyadınız]
* **Akademik Danışman:** [Danışman Hocanızın Unvanı, Adı Soyadı]
* **Proje Süresi:** 6 Ay
* **Tematik Alan:** Bilişim ve İletişim Teknolojileri / Yöneylem Araştırması ve Karar Destek Sistemleri

---

## 1. PROJENİN AMACI VE HEDEFLERİ

### 1.1. Projenin Amacı
Bu projenin temel amacı; Çok Kriterli Karar Verme (ÇKKV) süreçlerinde karar matrislerinde karşılaşılan "eksik/ölçülemeyen veri" problemini çözmek amacıyla, yeni bir cebirsel yaklaşım olan **Bağlamsal Sıfır Cebiri (Contextual Zero Algebra - CZ-Algebra)** kurallarını TOPSIS yöntemine entegre etmek; geliştirilen **CZ-TOPSIS** algoritmasını simülasyon ortamında test ederek doğrulamak ve açık kaynaklı bir karar destek kütüphanesi olarak literatüre kazandırmaktır.

### 1.2. Somut ve Ölçülebilir Hedefler
1. **Algoritmik Modelleme:** Ölçülen kesin sıfır ($0_A$) ile ölçülemeyen/bilinmeyen veri ($0_I$) ayrımını yapan ve global alt-uzay Öklid uzaklığı kullanan R-CZ-TOPSIS algoritmasına aşırı veri eksikliğini dengeleyen bir *Epistemik Güvenilirlik Cezalandırma Katsayısı ($\Gamma_i$)* entegre etmek.
2. **Kütüphane Geliştirme:** Algoritmayı Python ortamında modüler, birim testleri tamamlanmış ve nesne yönelimli bir açık kaynak kütüphane (`cz-mcdm`) haline getirmek.
3. **Simülasyon ve Doğrulama:** Rastgele kayıp veri oranları (%10, %25, %40, %60) içeren önceden belirlenmiş Monte Carlo tekrarlarıyla CZ-TOPSIS'in performansını; Klasik TOPSIS ve mevcut prototipte uygulanan Ortalama Doldurma TOPSIS yöntemiyle Spearman ve Kendall ölçütleri üzerinden kıyaslamak. k-NN doldurma, ayrı bir sonraki deney olarak eklenmeden mevcut sonuçlar arasında gösterilmeyecektir.
4. **Kullanıcı Arayüzü (PoC):** Karar vericilerin CSV formatında veri yükleyip klasik ve CZ yöntemlerini karşılaştırmalı grafiklerle analiz edebileceği bir gösterge paneli (Streamlit) geliştirmek.

---

## 2. LİTERATÜR ÖZETİ VE ÖZGÜN DEĞER

### 2.1. Literatür Özeti
Çok Kriterli Karar Verme (MCDM/ÇKKV) literatüründe TOPSIS (Hwang ve Yoon, 1981), pozitif ideale en yakın ve negatif idealden en uzak alternatifi belirleme mantığıyla en yaygın kullanılan yöntemlerden biridir. Ancak gerçek hayat veri setlerinde (savunma, finans, insan kaynakları, tedarik zinciri) karar matrislerinde eksik gözlemler kaçınılmazdır.

Bu özet kapsamlı sistematik tarama değildir. Literatürde eksik bilgi için imputation,
bulanık/olasılıksal modeller, kısmi bilgi ve özel TOPSIS uzantıları dahil birden fazla
yaklaşım bulunmaktadır:
1. **Veri Çıkarma/İhmal Etme:** Eksik verisi olan alternatif doğrudan elenmektedir. Bu durum, veri eksikliği yaşayan potansiyel olarak üstün alternatiflerin haksızca kaybedilmesine yol açar.
2. **Yapay Doldurma (Imputation):** Eksik hücreler sütun ortalaması, medyan veya makine öğrenmesi modelleriyle (k-NN, MICE) tahmin edilerek doldurulur. Ancak bu yaklaşım veri kümesine yapay varyans ve tahminleme sapması (bias) ekler.

Carlström (2004) tarafından geliştirilen Wheel Cebiri ve Bergstra ve Tucker (2009) tarafından ortaya konan Meadow Teorisi, sıfır ve bölme işlemlerinin cebirsel davranışlarını genişletmiştir. Bu projede kullanılan CZ-Algebra adı ise bağımsız hakemli bir teori olarak doğrulanmış değildir; proje içi bir modelleme adıdır. Bu nedenle yaklaşımın literatürdeki boşluğu doldurduğu henüz söylenemez; yalnızca test edilebilir bir araştırma hipotezi olarak sunulmalıdır.

### 2.2. Özgün Değer
* **Yapay Doldurmasız (Imputation-Free) Çözüm:** Proje, veriyi yapay olarak üretmeden, gözlemlenmiş veri alt kümesi üzerinden global ağırlıklı alt-uzay izdüşümü ($V_{ij} = w_j \cdot r_{ij}$) ve asimetrik epistemik ceza ($\Gamma_i$) uygular. Bunun mevcut yöntemlere göre üstünlüğü henüz kanıtlanmış değildir; karşılaştırmalı benchmark konusu yapılmıştır. *(İlk kavramsal taslakta düşünülen $\sqrt{m / m_i^*}$ boyutsal çarpanı ile yerel ağırlıklandırma, kanonik v1.1 modelinde koordinat şişmesini önleyen global alt-uzay formülasyonuna dönüştürülmüştür).*
* **Semantik Sıfır Ayrımı:** Karar matrisinde "kriter değerlendirildi ve başarısız oldu ($0_A$)" ile "kriter henüz ölçülemedi/veri mevcut değil ($0_I$)" durumları iki ayrı veri durumu olarak modellenir. Bu uygulama kararı, tek başına “ilk” veya yeni cebir kanıtı değildir.
* **Geriye Dönük Uyumluluk:** Karar matrisinde eksik veri bulunmadığı durumlarda ($m_i^* = m$), algoritma otomatik olarak klasik TOPSIS'e indirgenir; bu da klasik teorinin tüm kazanımlarının korunduğunu gösterir.

---

## 3. YÖNTEM

### 3.1. Matematiksel Formülasyon (v1.1 Global Ağırlıklandırma Mimarisi)
Karar matrisi $X = [x_{ij}]_{n \times m}$ olarak tanımlanır. Her bir eleman $x_{ij} = (v_{ij}, \sigma_{ij})$ şeklinde bir değer-bağlam çiftidir; burada $v_{ij} \in \mathbb{R}$ ve $\sigma_{ij} \in \{A, I\}$'dır ($0_A \neq 0_I$).

1. **İzdüşümsel Vektör Normalizasyonu:** Yalnızca aktif gözlemler üzerinden norm paydası $S_j = \sqrt{\sum_{k \in \mathcal{A}_j} x_{kj}^2}$ hesaplanır; $r_{ij} = x_{ij} / S_j$.
2. **Global Ağırlıklandırma ve İdeal Noktalar:** Boyutsal şişirmeyi engellemek için doğrudan global ağırlıklar tatbik edilir: $V_{ij} = w_j \cdot r_{ij}$. İdeal ($v_j^+$) ve anti-ideal ($v_j^-$) noktalar aktif alternatiflerin $V_{kj}$ değerleri üzerinden belirlenir.
3. **Alt-Uzay Öklid Mesafeleri ve Temel Skor:** $i$. alternatifin yalnızca bildiği kriterler kümesi ($J_i^*$) üzerinde alt-uzay mesafeleri hesaplanır:
   $$D_i^+ = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^+)^2}, \quad D_i^- = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^-)^2}, \quad C_{\text{base}, i} = \frac{D_i^-}{D_i^+ + D_i^-}$$
4. **Hard Gatekeeper ve Asimetrik Temkin Cezası:** Asgari bilgi barajını ($W_i = \sum_{j \in J_i^*} w_j \ge W_{\text{threshold}}$, $m_i^* \ge 2$) geçemeyen adaylar elenir. Geçen adaylara ise eksik maliyet kriterlerini dikkate alan asimetrik ceza ($\kappa_i = 1.0 + \sum_{j \notin J_i^*, \text{Cost}} w_j$) ile epistemik temkin çarpanı uygulanır:
   $$\Gamma_i = (W_i)^{\alpha \cdot \kappa_i}, \quad C_i^* = C_{\text{base}, i} \cdot \Gamma_i \quad (0 < \alpha \le 1)$$

*(Metodolojik Not: İlk kavramsal taslaktaki $\sqrt{m/m_i^*}$ boyutsal çarpanının göreceli yakınlık oranında analitik olarak sadeleştiği ve yerel ağırlıklandırmanın ($w_j/W_i$) eksik verili adayı yapay olarak ödüllendirdiği matematiksel denetimde kanıtlanmış; proje prototipi v1.1 global ağırlıklandırma ve $W_i$ tabanlı $\Gamma_i$ standardına olgunlaştırılmıştır).*

### 3.2. Yazılım Mimarisi ve Simülasyon Kurgusu
* **Platform:** Python 3.11+, NumPy, Pandas, SciPy, Streamlit.
* **Doğrulama Protokolü:** 
  1. Sentetik ve gerçek (UCI Automobile vb.) karar matrisleri kullanılacaktır.
  2. Matrislere kontrollü oranlarda Missing Completely at Random (MCAR) ve Missing Not at Random (MNAR) mekanizmalarıyla $0_I$ atanacaktır.
  3. Tam veri sıralaması (Ground Truth) baz alınarak; Klasik TOPSIS ($0.0$ atama), Mean-Imputation TOPSIS ve R-CZ-TOPSIS algoritmalarının ürettiği sıralamalar Spearman sıra korelasyonu ($\rho$) ve Kendall tau ($\tau$) ile test edilecektir. Proje prototipinde benchmark kapsamı hedef protokolün temel fazını gerçekleştirmiştir.

---

## 4. PROJE YÖNETİMİ, RİSKLER VE ÇALIŞMA TAKVİMİ

### 4.1. İş-Zaman Çizelgesi (6 Aylık)

| İş Paketi | İş Paketinin Adı | Başlangıç / Bitiş | Çıktı / Başarı Kriteri |
| :--- | :--- | :--- | :--- |
| **İP 1** | Ayrıntılı Literatür Taraması ve Ceza Katsayısının Matematiksel Formülasyonu | 1. Ay | Matematiksel Model Tasarım Raporu |
| **İP 2** | `cz-mcdm` Python Çekirdek Kütüphanesinin Kodlanması ve Birim Testleri | 2. Ay | GitHub Reposu, Test Senaryoları |
| **İP 3** | Monte Carlo Simülasyon Altyapısının Kurulması ve Veri Kaybı Deneyleri | 3. - 4. Ay | Karşılaştırmalı Analiz Grafikleri ve Tabloları |
| **İP 4** | Web Tabanlı Karar Destek Arayüzünün (Streamlit) Geliştirilmesi | 5. Ay | Çalışır Durumda Etkileşimli Web Uygulaması |
| **İP 5** | Sonuçların Değerlendirilmesi, Proje Sonuç Raporu ve Akademik Bildiri Hazırlığı | 6. Ay | TÜBİTAK Sonuç Raporu, Bildiri Taslağı |

### 4.2. Risk Yönetimi ve B Planı

| Karşılaşılabilecek Risk | Olasılık / Etki | B Planı (Önlem) |
| :--- | :--- | :--- |
| **R1: Yüksek veri eksikliğinde aşırı sıra sapmaları oluşması** | Orta / Yüksek | Formüldeki ceza üssü $\alpha$ için duyarlılık analizi (sensitivity analysis) yapılarak parametre optimize edilecektir. |
| **R2: Sentetik veri setlerinin gerçek hayat dinamiklerini tam yansıtamaması** | Düşük / Orta | UCI Machine Learning Repository'den kamuya açık gerçek tedarikçi ve personel veri setleri projeye dahil edilecektir. |
| **R3: Zaman kısıtı nedeniyle arayüz geliştirmede gecikme yaşanması** | Düşük / Düşük | Arayüz karmaşık web çatıları yerine doğrudan Python tabanlı hazır bileşenler sunan Streamlit ile hızlıca ayağa kaldırılacaktır. |

---

## 5. YAYGIN ETKİ

1. **Bilimsel/Akademik Çıktılar:**
   * Geliştirilen `cz-mcdm` kütüphanesi açık kaynaklı (MIT Lisansı) olarak araştırmacıların erişimine açılacaktır.
   * Proje sonuçları Yöneylem Araştırması ve Endüstri Mühendisliği (YA/EM) veya Savunma Teknolojileri (SAVTEK) kongrelerinde bildiri olarak sunulacaktır.
2. **Toplumsal ve Sektörel Fayda:**
   * Kriz anlarında (sensör arızaları, afet koordinasyonu, acil durum lojistiği) eksik telemetri verilerine rağmen güvenilir ve adil önceliklendirme yapabilecek bir karar destek altyapısı sunulacaktır.

---

## 6. PROJE BÜTÇESİ TALEP ÇİZELGESİ

| Sıra | Harcama Kalemi | Gerekçe | Yaklaşık Tutar (TL) |
| :--- | :--- | :--- | :--- |
| 1 | Bulut Sunucu / Hesaplama Kaynağı | Çoklu Monte Carlo simülasyonlarının kesintisiz koşturulması | 3.500 TL |
| 2 | Teknik Literatür ve Kitap Alımı | ÇKKV ve Karar Teorisi referans kaynakları | 2.500 TL |
| 3 | Kırtasiye ve Raporlama Masrafları | Rapor baskıları, proje posteri ve sunum materyalleri | 1.500 TL |
| 4 | Kongre Katılım / Kayıt Desteği | Proje çıktılarının ulusal kongrede sunulması | 4.500 TL |
| **TOPLAM** | | | **12.000 TL** |