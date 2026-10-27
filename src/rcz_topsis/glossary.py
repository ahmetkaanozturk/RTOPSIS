"""R-CZ-TOPSIS Kapsamlı Kavramlar Rehberi ve Sistem Sözlüğü (Glossary).

Bu modül; Hard Gatekeeper, Transponder (IFF), Epistemik Ceza, Akerlof Limon Piyasası
ve platformda kullanılan tüm matematiksel, askeri ve kurumsal kavramları
hem sade vatandaşın hem de teknik denetçilerin rahatça anlayabileceği şekilde tanımlar.
"""
from typing import Any, Callable, Dict, List, Optional


def get_glossary_terms() -> List[Dict[str, Any]]:
    """Sistemde kullanılan 18 temel kavramın yapılandırılmış sözlük dökümü."""
    return [
        # 1. KULLANICININ ÖZELLİKLE İSTEDİĞİ 4 KRİTİK KAVRAM
        {
            "id": "TERM-GATEKEEPER",
            "term": "Hard Gatekeeper (Asgari Bilgi Barajı)",
            "category": "🛡️ Güvenlik & Kural",
            "icon": "🚪",
            "short_def": "Bir adayın değerlendirmeye alınabilmesi için kriterlerin ağırlık toplamının en az %50'sine sahip olması şartıdır. Verisi %50'nin altındaysa doğrudan elenir.",
            "detailed_def": (
                "Karar teorisinde bilgi eksikliğinin şans eseri ödüllendirilmesini önleyen katı bir regülatif kapı bekçisidir.\n\n"
                "• **Nasıl Çalışır:** Adayın bilinen kriter ağırlıkları toplamı W_i = ∑_{j in J_i*} w_j formülüyle toplanır. "
                "Eğer W_i < 0.50 (veya belirlenen W_threshold) ise aday 'INSUFFICIENT_DATA' statüsüyle değerlendirme dışı bırakılır; skor 0.0 olur ve sonuç listesinde geçerli adayların arkasında gösterilir.\n"
                "• **Örnek:** 10 kriterlik bir ihalede 8 kriteri boş bırakan bir firma otomatik olarak güvenilir kabul edilmez; nihai karar yine şartname ve yetkili komisyon incelemesine bağlıdır."
            ),
            "formula": r"I_{\text{valid}}(i) = 1 \iff W_i \ge W_{\text{threshold}} - 10^{-9} \quad \text{ve} \quad m_i^* \ge m_{\text{min}}",
        },
        {
            "id": "TERM-TRANSPONDER",
            "term": "Transponder (IFF - Dost-Düşman Tanıma Sistemi)",
            "category": "🎯 Askeri & Radar",
            "icon": "📡",
            "short_def": "Uçak, İHA ve füzelerin kimlik, irtifa ve dost/düşman kodunu yer radarlarına bildiren elektronik sinyal vericisidir. Kapalı veya eksikse hedef hemen şüpheli sayılır.",
            "detailed_def": (
                "Hava Savunma C2 ve TEWA (Tehdit Değerlendirme) harekâtlarında en kritik telemetri kaynağıdır.\n\n"
                "• **Sistemdeki Rolü:** Düşman savaş uçakları, seyir füzeleri veya kamikaze İHA'lar kimliklerini gizlemek için transponder'larını kapatır (karartılmış veri / Context.INACTION / 0_I).\n"
                "• **R-CZ'nin Tepkisi:** Transponder verisi eksik olan temasları yok sayıp 0 sanmak yerine, asimetrik ceza ve Gatekeeper filtresiyle 'şüpheli temas' olarak işaretler ve operatörün onayına sunar."
            ),
            "formula": r"\text{IFF} \in \{\text{Friendly, Hostile, Unknown}\} \quad \longrightarrow \quad \sigma_{ij} = \text{INACTION} \implies \Gamma_i \text{ devreye girer}",
        },
        {
            "id": "TERM-EPISTEMIC-PENALTY",
            "term": "Epistemik Ceza (Epistemic Penalty / Temkin İndirimi - Γ_i)",
            "category": "📐 Matematik & Model",
            "icon": "⚡",
            "short_def": "Bir adayın eksik bilgisi olduğunda, karar vericiyi bilinmeyenin doğuracağı risklerden korumak için adayın temel puanından kesilen matematiksel güvenlik indirimidir.",
            "detailed_def": (
                "Felsefede 'epistemoloji' bilgi felsefesi demektir. Epistemik ceza, 'bilgi yoksunluğuna karşı duyulan matematiksel şüphe payı'dır.\n\n"
                "• **Nasıl Çalışır:** Adayın bilinen kriterlerdeki temel puanı C_base önce hesaplanır. Ardından Γ_i = W_i^(α · κ_i) çarpanı ile çarpılır (C* = C_base · Γ_i).\n"
                "• **Önemli Kural:** Adayın tüm verisi tamsa (W_i = 1.0) ceza %0'dır (Γ_i = 1.0). Veri azaldıkça çarpan 1'in altına iner (örn. 0.82) ve adayın puanı %18 kırılır."
            ),
            "formula": r"\Gamma_i = (W_i)^{\alpha \cdot \kappa_i}, \quad C_i^* = C_{\text{base}, i} \times \Gamma_i \quad (\Gamma_i \in (0, 1])",
        },
        {
            "id": "TERM-AKERLOF",
            "term": "Akerlof Limon Piyasası (The Market for Lemons)",
            "category": "🏛️ İhale & Teori",
            "icon": "🍋",
            "short_def": "Nobel ödüllü Akerlof'un teorisi: Satıcılar arabaların arızalarını (limon = çürük araç) saklarsa ve sistem onlara ortalama puan verirse, dürüstler kaçar, meydan kusurlu tekliflere kalır.",
            "detailed_def": (
                "George Akerlof 1970 yılında asimetrik bilgi (bilgi saklama) teorisiyle Nobel ödülü almıştır.\n\n"
                "• **İhaledeki Felaket:** Bir yüklenici yakıt tüketimini veya bakım masrafını teklif dosyasında boş bırakırsa ve sistem ona 'ortalama' bir değer atarsa, kusurunu saklayan hilekâr ödüllendirilmiş olur.\n"
                "• **R-CZ Çözümü:** Gizlenen kriter bir Maliyet/Risk kriteri ise ceza katsayısı üssel olarak büyütülür (κ_i = 1 + missing_cost). Böylece maliyet saklayanın cezası katlanır ve haksız avantajı bastırılır."
            ),
            "formula": r"\kappa_i = 1.0 + \sum_{j \notin J_i^*, j \in \text{Cost}} w_j \quad \implies \quad \text{Maliyet gizlendikçe } \kappa_i > 1 \text{ olur ve üs patlar}",
        },

        # 2. SİTEDEKİ DİĞER TEMEL VE ÖZGÜN KAVRAMLAR
        {
            "id": "TERM-CZ-ALGEBRA",
            "term": "Contextual Zero Cebiri (CZ-Algebra: 0_A vs 0_I)",
            "category": "📐 Matematik & Model",
            "icon": "0️⃣",
            "short_def": "Ölçülmüş gerçek sıfır (0_A, örn. 0 TL ceza veya 0 km hız) ile verinin hiç bilinmemesini (0_I, karartılmış veri) birbirinden ayıran çift-sıfır cebirsel mantığıdır.",
            "detailed_def": (
                "Klasik bilgisayar algoritmaları hem ölçülmüş sıfıra hem de boş hücreye aynı '0.0' değerini yazar. Bu, karar modellerini körleştirir.\n\n"
                "• **0_A (Actionable Zero):** Kriter ölçülmüştür ve sonucu gerçekten sıfırdır (örn: sıfır kaza, sıfır gecikme cezası). Bu bir başarıdır.\n"
                "• **0_I (Inaction Zero):** Kriter ölçülmemiştir, gizlenmiştir veya sensör kararmıştır (örn: bilinmeyen fiyat, karartılmış radar). Bu bir belirsizliktir.\n"
                "R-CZ veri tabanında bu iki sıfırı asla birbirine karıştırmaz."
            ),
            "formula": r"0_A \in \text{Action (Ölçülmüş Sıfır)} \quad \neq \quad 0_I \in \text{Inaction (Bilinmeyen / Eksik Hücre)}",
        },
        {
            "id": "TERM-SUBSPACE",
            "term": "Alt-Uzay İzdüşümü (Subspace Euclidean Distance - J_i*)",
            "category": "📐 Matematik & Model",
            "icon": "📐",
            "short_def": "Eksik verili adaya sahte sayı uydurmadan, adayı yalnızca ölçülebildiği kriterlerin koordinat ekseninde diğer adaylarla yarıştırma yöntemidir.",
            "detailed_def": (
                "Örneğin 8 kriterlik bir karar matrisinde adayın yalnızca 5 kriteri ölçülmüş olsun.\n\n"
                "• **Nasıl Çalışır:** Klasik model diğer 3 kritere sahte sayı uydururken (imputation), R-CZ o 3 kriteri adayın boyutundan çıkarır. Adayı sadece ölçülen 5 kriterin oluşturduğu 5 boyutlu alt-uzayda (J_i*) Öklid mesafelerine tabi tutar.\n"
                "• **Faydası:** Sahte veri üretilmediği için hesaplama girdisinin bütünlüğü audit makbuzuyla gösterilebilir; bu durum tek başına mahkeme veya Sayıştay kabulü anlamına gelmez."
            ),
            "formula": r"D_i^+ = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^+)^2}, \quad D_i^- = \sqrt{\sum_{j \in J_i^*} (V_{ij} - v_j^-)^2}",
        },
        {
            "id": "TERM-NORM",
            "term": "Sütun Norm Paydası (S_j) & Vektör Normalizasyonu",
            "category": "📐 Matematik & Model",
            "icon": "📏",
            "short_def": "Farklı ölçü birimlerini (TL, km/s, kg, saat) [0, 1] aralığında ortak bir puana dönüştürmek için aktif gözlemlerin kareler toplamının karekökünü alma işlemidir.",
            "detailed_def": (
                "Karar matrisinde fiyat milyon TL iken hız km/s, ağırlık ise ton cinsindendir. Bunları doğrudan toplayamazsınız.\n\n"
                "• **R-CZ Farkı:** Klasik TOPSIS eksik hücreleri 0 kabul edip norm paydasına katar. R-CZ ise yalnızca gerçekte ölçülmüş aktif hücrelerin (A_j) kareler toplamının karekökünü (S_j) alır. Böylece norm paydası yapay biçimde küçülmez."
            ),
            "formula": r"S_j = \sqrt{\sum_{k, \sigma_{kj}=A} X_{kj}^2}, \quad r_{ij} = \frac{X_{ij}}{S_j}, \quad V_{ij} = w_j \cdot r_{ij}",
        },
        {
            "id": "TERM-IDEAL-POINTS",
            "term": "İdeal (v+) ve Anti-İdeal (v-) Çözüm Noktaları",
            "category": "📐 Matematik & Model",
            "icon": "🎯",
            "short_def": "Kriter uzayında ulaşılabilecek en kusursuz hedef nokta (v+) ile kesinlikle kaçınılması gereken en kötü noktadır (v-).",
            "detailed_def": (
                "TOPSIS'in temel geometrik felsefesidir: 'En iyi alternatif, ideale en yakın ve anti-ideale en uzak olandır.'\n\n"
                "• **Fayda Kriteri (↑):** En yüksek değer v+ (ideal), en düşük değer v- (anti-ideal) olur.\n"
                "• **Maliyet Kriteri (↓):** En düşük değer v+ (ideal), en yüksek değer v- (anti-ideal) olur."
            ),
            "formula": r"v_j^+ = \begin{cases} \max_k V_{kj} & \text{Fayda} \\ \min_k V_{kj} & \text{Maliyet} \end{cases}, \quad v_j^- = \begin{cases} \min_k V_{kj} & \text{Fayda} \\ \max_k V_{kj} & \text{Maliyet} \end{cases}",
        },
        {
            "id": "TERM-SCORES",
            "term": "Temel Skor (C_base) vs Nihai Skor (C*)",
            "category": "📐 Matematik & Model",
            "icon": "🏆",
            "short_def": "C_base adayın bildiği kriterlerdeki saf başarısıdır. C* ise eksik verisi için temkin cezası (Γ_i) düşüldükten sonraki tescilli nihai başarı puanıdır.",
            "detailed_def": (
                "İki skor arasındaki fark, sistemin ne kadar 'temkin indirimi' uyguladığını tam şeffaflıkla gösterir.\n\n"
                "• C_base = %80 olan bir adayın 1 önemli maliyet kriteri eksikse Γ_i = 0.85 olur ve nihai puanı C* = %68'e iner.\n"
                "• Karar verici tek ekranda adayın hem ham potansiyelini hem de veri eksiği cezasını ayrı ayrı denetleyebilir."
            ),
            "formula": r"C_{\text{base}, i} = \frac{D_i^-}{D_i^+ + D_i^-}, \quad C_i^* = C_{\text{base}, i} \times \Gamma_i",
        },
        {
            "id": "TERM-GRACEFUL",
            "term": "Graceful Degradation (Kademeli Bozulma / Yumuşak İniş)",
            "category": "🎯 Askeri & Radar",
            "icon": "🛡️",
            "short_def": "Savaş alanında veya kriz anında sensörlerin bir kısmı hasar görse bile sistemin tamamen kilitlenmeyip sağlam kalan kanallarla göreve devam edebilmesidir.",
            "detailed_def": (
                "Kritik aviyonik ve görev bilgisayarlarında aranan en önemli mimari dayanıklılık özelliğidir.\n\n"
                "• Bir İHA'nın radar sensörü jammer ile karartıldığında, uçuş bilgisayarı optik ve telemetri kanallarıyla karar üretmeye devam eder. Tüm sistem 'sensör hatası' verip kapanmaz."
            ),
            "formula": r"\text{Sensör Kararması } \implies J_i^* \text{ boyutu küçülür, } O(NM) \text{ süreklilik korunur}",
        },
        {
            "id": "TERM-JAMMER",
            "term": "Jammer (Elektronik Karıştırma / EH)",
            "category": "🎯 Askeri & Radar",
            "icon": "⚡",
            "short_def": "Düşmanın radar, GPS veya telsiz frekanslarına yüksek güçte elektromanyetik gürültü basarak sensörleri körleştirmesi veya sahte iz üretmesidir.",
            "detailed_def": (
                "Modern harp sahasında verinin eksik kalmasının 1 numaralı sebebidir.\n\n"
                "• Radar TEWA senaryosunda hedef izler jammer koruması altına girdiğinde hedef hızı veya irtifası sensör ekranından düşebilir. R-CZ bu kararmaları 'sıfır' saymayıp 'Inaction (0_I)' olarak işaretler."
            ),
            "formula": r"\text{Jammer Aktif} \implies \text{Sensör Tazeliği Düşer, Graceful Mod Devreye Girer}",
        },
        {
            "id": "TERM-TEWA",
            "term": "TEWA (Tehdit Değerlendirme & Silah Tahsisi - C2)",
            "category": "🎯 Askeri & Radar",
            "icon": "🎯",
            "short_def": "Hava savunma radarına yakalanan onlarca hedefi hız, menzil ve kimliklerine göre tehlike sırasına dizip hangi füzenin hangi hedefe ateşleneceğini planlayan komuta kontrol algoritmasıdır.",
            "detailed_def": (
                "Threat Evaluation and Weapon Assignment (TEWA), saniyeler içinde karar verilmesi gereken yüksek tempolu bir C2 sürecidir.\n\n"
                "• R-CZ'nin rolü: Operatöre açıklanabilir (XAI) bir tehdit sıralaması sunar; ancak otonom ateşleme yapmaz, kesin onay harekât subayındadır."
            ),
            "formula": r"\text{Hedef Öncelik Puanı } C_i^* \propto \frac{\text{Hız} \uparrow, \text{RCS} \uparrow}{\text{Menzil} \downarrow, \text{Varış Süresi} \downarrow}",
        },
        {
            "id": "TERM-IMPUTATION",
            "term": "Imputation vs Imputation-Free",
            "category": "🏛️ İhale & Teori",
            "icon": "🧩",
            "short_def": "Imputation boş hücrelere ortalama veya regresyonla sahte sayı uydurmaktır. Imputation-Free ise hiçbir yapay sayı üretmeden yalnızca ölçülen gerçek verilerle çalışmaktır.",
            "detailed_def": (
                "Yapay zeka modellerinin %90'ı eksik veri gördüğünde boşluğa sütun ortalamasını yazar.\n\n"
                "• **Tehlike:** Savunma ihalelerinde veya adli süreçlerde karar matrisine uydurma sayı yazılması kanunen suç teşkil edebilir ve ihaleyi mahkemede iptal ettirir.\n"
                "• **R-CZ Yaklaşımı:** %100 Imputation-Free'dir. Tek bir yapay sayı türetmez."
            ),
            "formula": r"\tilde{X}_{ij} = \text{mean}(X_{\cdot j}) \quad (\text{Yasaklı Uydurma}) \quad \longleftrightarrow \quad J_i^* \text{ Alt-Uzay (R-CZ İlkesi)}",
        },
        {
            "id": "TERM-RECEIPT",
            "term": "SHA-256 Denetim Makbuzu (Integrity Receipt)",
            "category": "🛡️ Güvenlik & Kural",
            "icon": "📜",
            "short_def": "Girdi tablosunu, komisyon üyelerinin kimliklerini, parametreleri ve sıralama sonucunu tek bir kriptografik özette donduran değiştirilemez dijital mühürdür.",
            "detailed_def": (
                "Kurum içi inceleme ve bütünlük kontrolü için tasarlanmış tamper-evident bir delil zinciridir; resmi denetim kabulü veya hukuki geçerlilik garantisi değildir.\n\n"
                "• Bir ihalenin kararı verildikten sonra kaydedilmiş veride tek bir rakam dahi değiştirilirse SHA-256 mührü bozulur ve sistem 'Veri Tahrif Edildi!' alarmı verir."
            ),
            "formula": r"\text{Mühür} = \text{SHA256}(\text{DatasetHash} \,\|\, \text{ConfigHash} \,\|\, \text{OutputHash} \,\|\, \text{Timestamp})",
        },
        {
            "id": "TERM-FAIL-CLOSED",
            "term": "Fail-Closed (Güvenli Duruş Kuralı)",
            "category": "🛡️ Güvenlik & Kural",
            "icon": "🔒",
            "short_def": "Sensör verileri bayatladığında veya bilgi yetersiz kaldığında sistemin asla otonom işlem yapmayıp güvenli duruşa geçerek insan operatörü beklemesidir.",
            "detailed_def": (
                "Yazılım ve silah güvenliğinde iki ilke vardır: 'Fail-Open' (hata olsa da devam et) ve 'Fail-Closed' (hata varsa dur ve kilitle).\n\n"
                "• R-CZ Askeri Profilinde Fail-Closed zorunludur: Şüpheli izlerde veya tüm hedefler belirsizleştiğinde 'HOLD_NO_ACTIONABLE_TRACKS' emri üretir."
            ),
            "formula": r"\text{Bayat Telemetri } > 15\,\text{sn} \implies \text{Duruş: HOLD (Operatör Doğrulaması Şart)}",
        },
        {
            "id": "TERM-ALPHA",
            "term": "Epistemik Risk Katsayısı (α - Alpha)",
            "category": "📐 Matematik & Model",
            "icon": "🎛️",
            "short_def": "Kurumun bilgi eksikliğine karşı ne kadar hoşgörülü veya ne kadar katı olacağını belirleyen ana duyarlılık kaldıracıdır.",
            "detailed_def": (
                "Yan menüdeki slider ile anında ayarlanabilir:\n\n"
                "• α = 0.0: Ceza kapalıdır. Adaylar sadece bildikleriyle yarışır.\n"
                "• α = 0.50: Dengeli akademik standarttır. Eksik veriliyi uyarır ama iyi adayları hemen ezmez.\n"
                "• α ≥ 1.0: Katı moddur. Savunma ve kritik alımlarda bilgi eksikliğine sert ceza keser."
            ),
            "formula": r"\alpha \in [0.0, 2.0], \quad \Gamma_i = W_i^{(\alpha \cdot \kappa_i)}",
        },
        {
            "id": "TERM-SHANNON",
            "term": "Shannon Entropisi (Nesnel Kriter Ağırlıklandırması)",
            "category": "🏛️ İhale & Teori",
            "icon": "📊",
            "short_def": "Kriterlerin önem derecelerini insan kanaatine bırakmadan, veri tablosundaki varyans ve bilgi dağılımından matematiksel olarak hesaplama yöntemidir.",
            "detailed_def": (
                "Bir kriterde tüm adayların performansı birbirine çok yakınsa o kriterin ayırt ediciliği düşüktür.\n\n"
                "• Shannon entropisi varyansı yüksek, yani adayları en iyi ayrıştıran kriterlere otomatik olarak daha yüksek ağırlık (w_j) atar."
            ),
            "formula": r"E_j = -k \sum_{i=1}^n p_{ij} \ln(p_{ij}), \quad w_j = \frac{1 - E_j}{\sum (1 - E_k)}",
        },
        {
            "id": "TERM-AHP",
            "term": "AHP (Analitik Hiyerarşi Süreci) & Tutarlılık Oranı (CR)",
            "category": "🏛️ İhale & Teori",
            "icon": "🌲",
            "short_def": "Soyut insan tercihlerini 1-9 ölçeğiyle sayısallaştıran ve karar vericinin mantıksal çelişkilerini (CR < 0.10) denetleyen çok kriterli yöntemdir.",
            "detailed_def": (
                "Thomas Saaty tarafından geliştirilmiştir.\n\n"
                "• Kriterler ikişer ikişer karşılaştırılır (A, B'den 3 kat daha önemlidir gibi). Matrisin özvektörü ağırlıkları üretir; Tutarlılık Oranı (CR) ise karar vericinin çelişkili puan verip vermediğini denetler."
            ),
            "formula": r"CR = \frac{CI}{RI} < 0.10 \quad (\text{Tutarlı Karar Verici Sınırı})",
        },
    ]


def render_glossary_component(st: Any, safe_text: Callable[[object], str], key_prefix: str = "glossary") -> None:
    """Tüm terimleri arama ve kategori filtresiyle birlikte modern kartlar halinde çizer."""
    terms = get_glossary_terms()

    categories = [
        "Tüm Terimler (18)",
        "🛡️ Güvenlik & Kural",
        "🎯 Askeri & Radar",
        "📐 Matematik & Model",
        "🏛️ İhale & Teori",
    ]

    col_s1, col_s2 = st.columns([1.5, 2.5])
    with col_s1:
        selected_category = st.selectbox("📂 Terim Kategorisi:", categories, index=0, key=f"{key_prefix}_cat_select")
    with col_s2:
        search_query = st.text_input("🔍 Terim veya Kavram Ara:", placeholder="Örn: transponder, gatekeeper, akerlof, ceza...", key=f"{key_prefix}_search_input")

    # Filtreleme
    filtered = terms
    if selected_category != "Tüm Terimler (18)":
        filtered = [t for t in filtered if t["category"] == selected_category]

    if search_query.strip():
        q = search_query.strip().lower()
        filtered = [
            t for t in filtered
            if q in t["term"].lower() or q in t["short_def"].lower() or q in t["detailed_def"].lower()
        ]

    st.caption(f"Toplam **{len(filtered)}** kavram listeleniyor:")

    # 2 sütunlu yüksek kontrastlı kart düzeni
    col_g1, col_g2 = st.columns(2)
    for idx, t in enumerate(filtered):
        col = col_g1 if idx % 2 == 0 else col_g2
        with col:
            with st.expander(f"{t['icon']} {t['term']}", expanded=True if (idx < 4 and not search_query.strip()) else False):
                st.markdown(
                    f"""
                    <div class="rcz-glossary-card">
                        <div class="rcz-glossary-badge">{safe_text(t['category'])}</div>
                        <div class="rcz-glossary-summary">
                            <strong>Özet:</strong> {safe_text(t['short_def'])}
                        </div>
                        <div class="rcz-glossary-body">
                            {t['detailed_def']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if "formula" in t:
                    st.caption("Matematiksel / Mantıksal İfade:")
                    st.latex(t["formula"])
