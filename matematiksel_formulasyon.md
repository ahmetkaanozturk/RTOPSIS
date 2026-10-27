================================================================================
R-CZ-TOPSIS (RIGOROUS CONTEXTUAL ZERO TOPSIS) MATEMATİKSEL MODEL FORMÜLASYONU
Kanonik Sürüm: R-CZ-TOPSIS v1.1 / Python Core v1.1.1
Referans Uygulama: src/rcz_topsis/core.py
================================================================================

1. GİRDİ VE PARAMETRE TANIMLARI
--------------------------------------------------------------------------------
- Alternatif sayısı:  n   (i = 1, 2, ..., n)
- Kriter sayısı:      m   (j = 1, 2, ..., m, m >= 2)
- Kriter ağırlıkları: W = [w_1, w_2, ..., w_m]^T
                      Şart: w_j > 0, sonlu ve SUM_{j=1}^{m} w_j = 1.0

- Karar Matrisi Hücresi:
  (x_ij, sigma_ij)
  sigma_ij in {A, I}
  * sigma_ij = A  --> Action (Aktif ölçüm, gerçek değer; 0_A = Gerçek sıfır performans)
  * sigma_ij = I  --> Inaction (Eylemsizlik / Bilgi yokluğu; 0_I = Ölçülmemiş / Eksik veri)

- Kriter Kümeleri:
  * J_plus  : Fayda kriterleri indeksi (CritType.BENEFIT, daha yüksek değer daha iyi)
  * J_minus : Maliyet kriterleri indeksi (CritType.COST, daha düşük değer daha iyi)
  * J_plus UNION J_minus = {1, 2, ..., m}


2. AKTİF İNDEKSLER VE BİLGİ KAPSAMA ORANI (SUPPORT WEIGHT)
--------------------------------------------------------------------------------
Alternatif i için ölçümü mevcut (sigma_ij = A) olan kriterlerin indeks kümesi:
  J_i^* = { j in {1, 2, ..., m} | sigma_ij = A }

Alternatif i için aktif kriter adedi:
  m_i^* = |J_i^*|

Alternatif i'nin toplam sistem içindeki ağırlık payı (Bilgi Kapsama Oranı / Support Weight):
  W_i = SUM_{j in J_i^*} w_j,   (0 < W_i <= 1.0)


3. GÜVENLİK EŞİĞİ VE SÜZGEÇ (HARD GATEKEEPER)
--------------------------------------------------------------------------------
Bir i alternatifinin değerlendirmeye alınabilmesi için geçerlilik göstergesi:
  I_valid(i) = 1,  EĞER (W_i >= W_threshold - threshold_tol) VE (m_i^* >= min_active_criteria)
  I_valid(i) = 0,  AKSİ HALDE

Parametreler:
* W_threshold: Minimum bilgi kapsama eşiği (Varsayılan: 0.50)
* threshold_tol: Kayan nokta yuvarlama toleransı (Varsayılan: 1e-9)
* min_active_criteria: Minimum aktif kriter sayısı (Varsayılan: 2)
* I_valid(i) = 0 olan alternatifler "INSUFFICIENT_DATA" statüsüyle değerlendirme dışı bırakılır (skor = 0.0) ve uygulamada geçerli adayların arkasında listelenir. `rank`, sonuç listesindeki son konumu gösterir; bu alanın -1 olması kanonik uygulamanın sözleşmesi değildir.


4. İZDÜŞÜMSEL VEKTÖR NORMALİZASYONU (SUBSPACE VECTOR NORMALIZATION)
--------------------------------------------------------------------------------
Her j sütunu için norm böleni (yalnızca aktif ölçülen alternatifler üzerinden):
  S_j = SQRT( SUM_{k in {r | sigma_rj = A}} (x_kj)^2 )

Normalize edilmiş karar matrisi elemanı (r_ij):
  r_ij = x_ij / S_j,    (j in J_i^* için)
  r_ij = TANIMSIZ,      (j not in J_i^* için)


5. GÜNCEL VARSAYILAN GLOBAL AĞIRLIKLANDIRMA (v1.1 KANONİK STANDART)
--------------------------------------------------------------------------------
Kanonik v1.1 sürümünde (local_reweighting = False), boyutsal şişirmeyi (coordinate inflation)
engellemek için V matrisi doğrudan evrensel global ağırlıklar ile alt-uzaya projekte edilir:

  V_ij = w_j * r_ij,    (j in J_i^* için)

Bu sayede, az kriteri bilinen alternatiflerin koordinatları yapay olarak büyütülmez;
eksik bilginin getirdiği belirsizlik alt-uzay mesafelerine adil biçimde yansıtılır.

5.B. TARİHSEL KARŞILAŞTIRMA MODU (v1.0 Dinamik Yerel Ağırlıklandırma - local_reweighting = True):
  w'_ij = w_j / W_i = w_j / ( SUM_{k in J_i^*} w_k ),   (j in J_i^* için)
  V_ij = w'_ij * r_ij
  [UYARI: Bu formül koordinatları 1/W_i kat büyüterek eksik verili adayı yapay biçimde
   ödüllendirebildiği için varsayılandan çıkarılmış; yalnızca deneysel karşılaştırma amacıyla saklanmıştır.]


6. İDEAL VE ANTİ-İDEAL REFERANS NOKTALARI
--------------------------------------------------------------------------------
Geçerli ve aktif tüm alternatiflerin V_ij değerleri üzerinden sütun bazlı ekstremumlar:

* Fayda Kriterleri (j in J_plus):
    v_j^+ = MAX_{k in {r | I_valid(r) = 1 VE sigma_rj = A}} ( V_kj )
    v_j^- = MIN_{k in {r | I_valid(r) = 1 VE sigma_rj = A}} ( V_kj )

* Maliyet Kriterleri (j in J_minus):
    v_j^+ = MIN_{k in {r | I_valid(r) = 1 VE sigma_rj = A}} ( V_kj )
    v_j^- = MAX_{k in {r | I_valid(r) = 1 VE sigma_rj = A}} ( V_kj )


7. ALT-UZAY ÖKLİD UZAKLIKLARI (SUBSPACE EUCLIDEAN DISTANCES)
--------------------------------------------------------------------------------
Alternatif i'nin yalnızca BİLDİĞİ kriterler (J_i^*) üzerindeki alt-uzay Öklid mesafeleri:

Pozitif İdeale Uzaklık:
  D_i^+ = SQRT( SUM_{j in J_i^*} (V_ij - v_j^+)^2 )

Negatif İdeale Uzaklık:
  D_i^- = SQRT( SUM_{j in J_i^*} (V_ij - v_j^-)^2 )


8. TEMEL GÖRECELİ YAKINLIK SKORU (BASE CLOSENESS SCORE)
--------------------------------------------------------------------------------
Alternatif i için temkin cezası uygulanmamış temel alt-uzay TOPSIS skoru:
  C_base_i = D_i^- / ( D_i^+ + D_i^- )

* Özel Durum (Nötr Skor): Eğer (D_i^+ + D_i^-) < eps (1e-12) ise:
  C_base_i = 0.50 kabul edilir.
* Aralık: 0.0 <= C_base_i <= 1.0


9. EKSİK MALİYET TESPİTİ VE ASİMETRİK EPİSTEMİK CEZA (CONFIDENCE FACTOR)
--------------------------------------------------------------------------------
Alternatif i'nin beyan etmediği/ölçülmeyen MALİYET kriterlerinin ağırlık toplamı:
  missing_cost_i = SUM_{j not in J_i^*, j in J_minus} w_j

Asimetrik Maliyet Eksiklik Katsayısı (kappa_i):
  kappa_i = 1.0 + missing_cost_i

Epistemik Güvenilirlik Çarpanı (Gamma_i):
  Gamma_i = ( W_i )^( alpha * kappa_i )

Parametreler:
* alpha: Epistemik riskten kaçınma katsayısı (alpha >= 0.0, Varsayılan: 0.50)
* Tam verili adayda (W_i = 1.0) Gamma_i = 1.0'dır; hiçbir ceza uygulanmaz.
* Maliyet kriteri gizleyen adayın üssü (kappa_i > 1.0) büyür ve ceza daha sertleşir.


10. NİHAİ R-CZ-TOPSIS SKORU VE SIRALAMA KURALI
--------------------------------------------------------------------------------
Alternatif i için nihai performans indeksi (C_i^*):
  C_i^* = C_base_i * Gamma_i
        = [ D_i^- / ( D_i^+ + D_i^- ) ] * [ ( W_i )^( alpha * kappa_i ) ]

Sıralama ve Eşitlik Bozma (Tie-Breaking) Kuralı:
1. Geçerli alternatifler (I_valid = 1), C_i^* skorlarına göre BÜYÜKTEN KÜÇÜĞE sıralanır.
2. Skor eşitliğinde (C_i^* == C_k^*), bilgi kapsama oranı (support_weight, W_i) daha yüksek olan öne geçer.
3. Yetersiz bilgiye sahip alternatifler (I_valid = 0), skoru 0.0 ve `INSUFFICIENT_DATA` statüsüyle listenin sonuna eklenir. `rank` değeri uygulamanın sonuç listesindeki son konumdur.


11. BİLİMSEL VE MATEMATİKSEL SINIRLAMALAR (ŞEFFAF VE DÜRÜST ÇERÇEVE)
--------------------------------------------------------------------------------
1. Ceza Etkisi ve Sınır Vaka:
   Asimetrik ceza (kappa_i), maliyet gizleme kaynaklı haksız avantajı sınırlandırmayı ve bastırmayı hedefler.
   Ancak bir adayın bilinen fayda kriterlerindeki üstünlüğü aşırı yüksekse, Gamma_i cezasına rağmen birinci sırada
   kalması matematiksel olarak mümkündür. Model "hileyi tamamen ve mutlak olarak ortadan kaldırır" iddiasında
   değildir; haksız avantajı azaltır ve kurumsal profil seviyesinde savunma/inceleme bayrağı üretir.

2. Norm Paydaları Kapsamı:
   S_j norm paydaları karar matrisindeki tüm aktif gözlemler üzerinden hesaplanır.

3. Tarihsel Boyut Dengeleme Yaklaşımı:
   İlk kavramsal taslaklarda tartışılan boyutsal ölçekleme çarpanı, göreceli yakınlık oranında (D- / (D+ + D-))
   pay ve paydada analitik olarak birbirini sadeleştirdiği için terk edilmiş olup kanonik v1.1 çekirdeğinde yer almaz.
================================================================================