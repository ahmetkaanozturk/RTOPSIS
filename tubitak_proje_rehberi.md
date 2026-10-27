# TÜBİTAK 2209 Proje Rehberi: CZ-TOPSIS ile Karar Destek Sistemlerinde Eksik Veri Yönetimi

> **Not:** Bu doküman, matematik ve yazılım altyapısı olmadan dahi projenin mantığını tam olarak kavrayabilmeniz, öğretim üyenizle teknik detayları rahatça konuşabilmeniz ve TÜBİTAK panellerinde projeyi eksiksiz savunabilmeniz amacıyla hazırlanmıştır.

---

## 1. Konunun Özü (Hiç Bilmeyenler İçin Sade Anlatım)

### "Sıfır" Her Zaman Aynı Sıfır mıdır?
Geleneksel matematikte $0$ tektir ve yutandır: $5 \times 0 = 0$. Ancak gerçek hayatta sıfırın iki farklı anlamı vardır:

1. **Ölçülen Sıfır ($0_A$ - Eylem Sıfırı):** Bir teste girdiniz, soruları çözdünüz ama hiçbirini doğru yapamadınız. Puanınız: **0**. Bu ölçülmüş, kesin bir başarısızlıktır.
2. **Bilinmeyen / Eksik Sıfır ($0_I$ - Eylemsizlik Sıfırı):** O gün hastaydınız ve sınava hiç giremediniz. Puan haneniz boş veya sistem gereği **0** görünüyor. Bu sizin başarısız olduğunuz anlamına mı gelir? Hayır, sadece veriniz yoktur.

### TOPSIS Nedir? (Telefon Alma Benzetmesi)
TOPSIS (Technique for Order Preference by Similarity to Ideal Solution), çok kriterli karar verme (ÇKKV) yöntemidir. 
Mantığı basittir:
* Pazardaki en iyi özellikleri toplayıp hayali bir **"Mükemmel Telefon" (İdeal Çözüm)** yaratır (Örn: En ucuz, en hızlı, pili en uzun giden).
* Pazardaki en kötü özellikleri toplayıp hayali bir **"Berbat Telefon" (Negatif İdeal)** yaratır.
* Seçenekleri bu iki hayali telefona olan uzaklığına göre sıralar: **Mükemmele en yakın, berbattan en uzak olan kazanır.**

### Problem Ne? Standart TOPSIS Nerede Çuvallıyor?
Bir telefona bakıyorsunuz; hızı harika, fiyatı çok uygun, ancak pil kapasitesi üretici tarafından henüz açıklanmamış (Veri Yok = $0_I$).
* **Klasik TOPSIS:** Bu boşluğu doğrudan sayısal $0$ kabul eder. Yani telefonu pili patlak, 0 dakika giden berbat bir cihaz gibi görür.
* **Sonuç:** Aslında çok iyi olan bir alternatif, sırf bir verisi henüz bilinmediği için haksızca listenin en dibine atılır.

### Çözümümüz: CZ-TOPSIS Ne Yapıyor?
CZ-TOPSIS (Contextual Zero TOPSIS); karar matrisindeki $0_I$ (bilinmeyen veri) hücrelerini cezalandırmadan hesap dışı bırakır. Alternatifi yalnızca **mevcut ve bilinen kriterleri** üzerinden değerlendirir ve adil olması için bu uzaklığı toplam kriter oranına göre matematiksel olarak ölçekler.

---

## 2. R-CZ-TOPSIS Nasıl Çalışır? (v1.1 Mimarisi)

1. **Matris Girişi & Çift-Sıfır Ayrımı:** Karar verici matrisi oluşturur. Ölçülmüş sıfırlar $0_A$, eksik veya ölçülmemiş veriler $0_I$ olarak etiketlenir.
2. **Aktif Vektör Normalizasyonu:** Sütun norm paydaları ($S_j$) yalnızca ölçülen aktif değerlerden hesaplanır ($r_{ij} = x_{ij} / S_j$).
3. **Global Ağırlıklandırma & İdeal Noktalar:** Koordinat uzayında boyut sapmasını önlemek için doğrudan evrensel kriter ağırlıkları tatbik edilir ($V_{ij} = w_j \cdot r_{ij}$). İdeal ve anti-ideal referanslar aktif hücrelerden seçilir.
4. **Alt-Uzay Mesafesi ve Temel Skor:** Alternatif yalnızca bildiği kriterler kümesinde ($J_i^*$) Öklid mesafesine tabi tutulur:
   $$D_i^+ = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^+)^2}, \quad D_i^- = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^-)^2}, \quad C_{\text{base}, i} = \frac{D_i^-}{D_i^+ + D_i^-}$$
   *(Tarihsel Not: İlk kavramsal taslaktaki $\sqrt{m/m_i^*}$ çarpanı pay ve paydada sadeleştiğinden v1.1'de mesafeler doğrudan alt-uzay metriğiyle hesaplanır).*
5. **Hard Gatekeeper Barajı:** Ağırlıklı bilgi kapsama oranı $W_i = \sum_{j \in J_i^*} w_j < 0.50$ olan veya 2'den az kriteri bulunan adaylar elenir.
6. **Asimetrik Maliyet Cezası ve Nihai Skor:** Eksik maliyet kriterlerini dikkate alan $\kappa_i$ üssüyle epistemik güvenilirlik çarpanı $\Gamma_i = W_i^{\alpha \cdot \kappa_i}$ uygulanır ve nihai skor elde edilir:
   $$C_i^* = C_{\text{base}, i} \cdot \Gamma_i$$

---

## 3. Avantajlar ve Dezavantajlar

### Avantajları (Güçlü Yönler)
* **Adil Sıralama:** Eksik verili alternatifler otomatik olarak çöpe atılmaz; mevcut başarılarına göre yarışta tutulur.
* **Veri Uydurmayı (Imputation) Engeller:** Klasik veri biliminde boşluklar ortalama veya medyan değerle doldurulur. Bu yapay tahminler gerçekliği bozar. CZ-TOPSIS veriyi yapay olarak doldurmadan çalışır.
* **Geriye Dönük Uyumluluk:** Eğer tüm veriler tamsa ($0_I$ yoksa), sistem klasik TOPSIS ile birebir aynı sonucu verir. Klasik cebiri bozmaz.
* **Geniş Uygulama Alanı:** Savunma sanayiinde sensör kopması, İK mülakatlarında eksik sınavlar, tedarikçi seçiminde yeni kurulan şirketler için benzersizdir.

### Dezavantajları ve Dikkat Edilmesi Gereken Riskler
* **Az Veriyle "Haksız Başarı" Riski:** Bir aday 5 kriterden sadece 1'ine girip onda çok yüksek aldıysa, diğer zorlu 4 kriteri eksik ($0_I$) olduğu için genel sıralamada haksızca zirveye oynayabilir.
  * *Çözümümüz:* Projeye **"Güvenilirlik / Tamlık Katsayısı" ($\gamma$)** ekleyerek veri eksikliği çok olanların skoruna hafif bir denge cezası uygulanmalıdır.
* **Teorik Açıklar:** CZ-Algebra genel matematikte henüz yeni bir taslaktır; halka teorisindeki bazı dağılma özellikleri genel durumlarda kısıtlıdır. (Bu yüzden projeyi matematik teorisi olarak değil, mühendislik/yazılım çözümü olarak sunuyoruz).

---

## 4. TÜBİTAK 2209-A / 2209-B İçin Başvuru Taslağı

### Proje Başlığı
**Eksik ve Belirsiz Veri Koşullarında Karar Destek Sistemleri İçin Bağlamsal Sıfır Cebiri (CZ-Algebra) Tabanlı TOPSIS Algoritmasının Geliştirilmesi, Simülasyonu ve Karşılaştırmalı Analizi**

### 1. Özgün Değer
Çok kriterli karar verme (ÇKKV) sistemlerinde karar matrislerinde eksik veri bulunması sıkça karşılaşılan bir problemdir. Mevcut literatürde bu sorun ya eksik verilerin yapay istatistiksel yöntemlerle doldurulmasıyla (imputation) ya da doğrudan sıfır kabul edilmesiyle geçiştirilmektedir. Ancak yapay doldurma veri dağılımında sapma (bias) yaratmakta, sıfır kabul etme ise alternatifi haksız şekilde cezalandırmaktadır.

Bu projenin özgün değeri; yeni bir cebirsel model olan Bağlamsal Sıfır Cebiri'nin (CZ-Algebra) sağladığı eylem sıfırı ($0_A$) ve eylemsizlik sıfırı ($0_I$) ayrımını temel alarak, eksik veriyi yapay olarak üretmeden global alt-uzay izdüşümü ve asimetrik epistemik ceza ($\Gamma_i$) ile işleyen **R-CZ-TOPSIS v1.1** yöntemini kodlamak, savunma ve kriz senaryolarında test etmek ve literatürdeki eksik veri doldurma yaklaşımlarıyla kıyaslayarak doğrulamaktır. *(Tarihsel Not: İlk kavramsal taslakta düşünülen $\sqrt{m / m_i^*}$ boyutsal çarpanı ve yerel ağırlıklandırma, kanonik v1.1 modelinde koordinat şişmesini önleyen global alt-uzay standardına dönüştürülmüştür).*

### 2. Yöntem
1. **Algoritmik Tasarım:** Belgedeki R-CZ-TOPSIS formülasyonu incelenecek; aşırı eksik verili alternatiflerin haksız öne geçmesini engelleyecek bir Epistemik Güvenilirlik Cezalandırma Katsayısı ($\Gamma_i$) geliştirilerek modele entegre edilecektir.
2. **Yazılım Geliştirme (Python):** `numpy` ve `pandas` kütüphaneleri kullanılarak modüler bir `rcz-topsis` çekirdeği yazılacaktır.
3. **Sentetik Veri ve Simülasyon (Monte Carlo):** Farklı boyutlarda (10 alternatif x 5 kriter vb.) karar matrisleri oluşturulacak; %10, %30 ve %50 oranlarında rastgele veri kaybı ($0_I$) enjekte edilecektir.
4. **Kıyaslama (Benchmarking):** R-CZ-TOPSIS çıktıları; Klasik TOPSIS, Ortalama Atamalı TOPSIS (Mean Imputation) ve k-NN Atamalı TOPSIS ile karşılaştırılacaktır. Sıralama tutarlılıkları Spearman Sıra Korelasyon Katsayısı ile ölçülecektir.
5. **Arayüz (Görselleştirme):** Kullanıcının CSV formatında karar matrisi yükleyip sonuçları görsel grafiklerle inceleyebileceği bir web paneli (Streamlit) kurulacaktır.

### 3. İş Paketleri ve Zaman Planı (6 Aylık Çizelge)

| İş Paketi (İP) | Açıklama | Süre | Çıktı |
|---|---|---|---|
| **İP 1: Literatür & Model** | ÇKKV eksik veri literatürü taraması ve formüle ceza katsayısı entegrasyonu | 1. Ay | Matematiksel Model Raporu |
| **İP 2: Çekirdek Kodlama** | Python ile R-CZ-TOPSIS algoritmasının ve test senaryolarının kodlanması | 2. Ay | Çalışır Python Kütüphanesi |
| **İP 3: Simülasyon & Kıyaslama** | Monte Carlo simülasyonu, %10-%50 kayıp veri testleri ve Spearman analizi | 3-4. Ay | Simülasyon Bulguları & Grafikler |
| **İP 4: Karar Paneli (Arayüz)** | Streamlit tabanlı interaktif web arayüzünün geliştirilmesi | 5. Ay | Çalışır Web Uygulaması (PoC) |
| **İP 5: Raporlama & Çıktı** | TÜBİTAK sonuç raporunun yazımı ve ulusal bildiri taslağının hazırlanması | 6. Ay | Proje Sonuç Raporu & Makale Taslağı |

### 4. Yaygın Etki
* **Akademik Çıktı:** ÇKKV alanında çalışan araştırmacılar için açık kaynaklı bir Python kütüphanesi (GitHub).
* **Bilimsel Yayın:** Ulusal bir kongrede (örneğin YA/EM - Yöneylem Araştırması ve Endüstri Mühendisliği Kongresi) sunulacak bildiri.
* **Sektörel Katkı:** Savunma sanayiinde sensör füzyonu ve radar arızalarında hedef önceliklendirme algoritmalarına referans model teşkil etmesi.

---

## 5. Adım Adım Geliştirme Yol Haritası (Cursor İle)

Geliştirmeyi **Cursor** üzerinde yaparken aşağıdaki sırayı izleyebilirsiniz:

### 1. Adım: Proje Ortamını Kurma
Terminalde sanal ortam açıp gerekli kütüphaneleri yükleyin:
```bash
python -m venv venv
source venv/bin/activate  # Windows için: venv\Scripts\activate
pip install numpy pandas streamlit matplotlib seaborn scipy
```

### 2. Adım: Çekirdek Fonksiyonu Kodlama (`core.py`)
Cursor Composer'a şu komutu verin:
> *"Python'da kanonik R-CZ-TOPSIS v1.1 algoritmasını yaz. Fonksiyon girdi olarak bir matris ve kriter ağırlıkları alsın. Hücrelerde normal sayılar veya '0_I' stringi (ya da np.nan) bulunabilir. Eğer hücre '0_I' ise normalizasyon ve uzaklık toplamından hariç tutulsun, V_ij = w_j * r_ij global alt-uzay izdüşümü kullanılsın, adayın bilinen kriter ağırlıkları toplamına (W_i) ve eksik maliyet kriterlerine bağlı olarak Gamma_i epistemik temkin cezası uygulansın. Sonuç olarak C* yakınlık skorlarını ve sıralamayı döndürsün."*

### 3. Adım: Karşılaştırma Testi (`benchmark.py`)
Belgenin 6. sayfasındaki Tablo 3'teki değerleri (Ürün A, B, C, D, E) kodunuza test matrisi olarak girin. Kodun ürettiği sıralamanın makaledeki Tablo 4 ile birebir uyuştuğunu doğrulayın:
* Klasik TOPSIS Sırası: D(#1), A(#2), B(#3), C(#4), E(#5)
* CZ-TOPSIS Sırası: D(#1), B(#2), A(#3), E(#4), C(#5)

### 4. Adım: Görsel Panel (`app.py`)
Cursor'a şunu yazdırın:
> *"Streamlit kullanarak bir karar destek arayüzü yaz. Kullanıcı bir CSV yüklesin, eksik veriler '0_I' olarak işaretlensin. Sayfada yan yana iki tablo çıksın: Biri Klasik TOPSIS sıralaması, diğeri CZ-TOPSIS sıralaması. Aradaki sıra değişimlerini bar grafiğiyle göstersin."*

---

## 6. Jüri ve Hocalardan Gelecek Zor Sorular ve Yanıtları

Bu soruları bildiğiniz anda projeyi tam bir uzman gibi savunabilirsiniz:

### Soru 1: "Eksik veriyi ortalama veya medyan ile doldurmak (Imputation) varken neden yeni bir yöntem kullanıyoruz?"
* **Cevabınız:** *"Hocam, eksik veri atama (imputation) yöntemleri sisteme yapay bir varyans ve istatistiksel sapma (bias) ekleyebilir. Olmayan bir veriyi tahmin etmek, karar vericiyi yanıltabilir. CZ-TOPSIS ise veriyi uydurmak yerine, adayı yalnızca kanıtlanmış mevcut verileri üzerinden değerlendirir ve bilgi eksikliğini ayrı bir ceza ile görünür kılar. Projemizde imputation yöntemleriyle CZ-TOPSIS'i Monte Carlo testlerinde kıyaslayarak hangi kayıp mekanizmalarında ve hangi ölçütlerde daha iyi veya daha kötü davrandığını ölçmeyi hedefliyoruz."*

### Soru 2: "Matematikte yeni bir cebir bulduğunuzu mu iddia ediyorsunuz?"
* **Cevabınız:** *"Hayır hocam. Biz saf bir cebir teorisi iddiasında bulunmuyoruz. Çalışma taslağı olan CZ-Algebra'nın karar teorisine sunduğu 'eylem sıfırı' ve 'eylemsizlik sıfırı' ayrımını bir mühendislik problemi olarak ele alıyoruz. Amacımız bu felsefi ve cebirsel ayrımı karar destek sistemlerine ve savunma senaryolarına başarılı bir algoritma olarak uyarlamaktır."*

### Soru 3: "Ya bir alternatif 10 kriterin 9'unu boş bırakıp, sadece 1 kriterde çok iyi olduğu için birinci çıkarsa? Bu bir güvenlik açığı değil mi?"
* **Cevabınız:** *"Çok haklı bir eleştiri hocam. Ham CZ formülünde bu bir sınırlılıktır. Tam da bu yüzden biz modelimize bir 'Güvenilirlik Cezalandırma Katsayısı' ($\gamma$) ekliyoruz. Eğer bir alternatifin veri eksikliği belirli bir eşiği aşarsa (örneğin %50'den fazla veri yoksa), skoru bu katsayı ile dengelenir veya sistem alternatifi 'Yetersiz Veri / Keşif Gerekli' statüsüne ayırır."*

### Soru 4: "Savunma sanayiinde bu nerede kullanılır?"
* **Cevabınız:** *"Özellikle radar jamming (elektronik köreltme) ortamında Tehdit Önceliklendirme (TEWA) yaparken kullanılır. Düşman füzesinin radar kesit alanı sensör karartması yüzünden okunamadığında ($0_I$), klasik sistem bunu sıfır tehdit zannedip önceliği düşürür. CZ-TOPSIS ise füzenin yaklaşma hızı ve rotası gibi bilinen parametrelerini adil ölçekleyerek alarm seviyesini yüksek tutar."*

---

## 7. Sözlük: Temel Terimler Kılavuzu

* **MCDM / ÇKKV (Çok Kriterli Karar Verme):** Birden fazla alternatif arasından, birbiriyle çelişen kriterlere göre en doğru seçimi yapmayı sağlayan matematiksel yöntemlerin genel adı.
* **Normalizasyon:** Farklı birimlerdeki verileri (örneğin fiyat TL cinsinden, hız km/s cinsinden) 0 ile 1 arasında aynı ölçeğe getirme işlemi.
* **Absorbing (Yutan) Eleman:** Çarpmada sıfır gibi girdiği işlemi kendi değerine dönüştüren eleman ($x \cdot 0 = 0$).
* **Lif (Fiber):** CZ cebirinde elemanların ait olduğu bağlam kümesi (Eylem lifi $A$ veya Eylemsizlik lifi $I$).
* **Monte Carlo Simülasyonu:** Bir algoritmanın başarısını test etmek için rastgele binlerce senaryo ve veri üreterek yapılan olasılıksal bilgisayar deneyi.
* **Spearman Korelasyonu:** İki farklı sıralamanın (Örn: Gerçek sıra ile tahmin edilen sıra) birbiriyle ne kadar uyumlu olduğunu ölçen istatistiksel katsayı (-1 ile +1 arası).