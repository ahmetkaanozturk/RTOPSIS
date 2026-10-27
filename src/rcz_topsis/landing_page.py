"""R-CZ-TOPSIS Tanıtım ve Karşılama Sayfası (Landing & Introduction Page).

Bu modül, kullanıcının karar motorunun detaylı tablolarına ve analiz paneline
girmeden önce sistemin ne olduğunu, nerelerde kullanılabileceğini ve neler
yapılabileceğini anlaşılır, görsel ve etkileyici bir dille özetler.
"""
from typing import Any, Callable, Dict, List
from .glossary import render_glossary_component


def get_landing_metadata() -> Dict[str, Any]:
    """Tanıtım sayfası üst bilgi ve temel sloganları döner."""
    return {
        "title": "R-CZ-TOPSIS Platformu",
        "badge": "YENİ NESİL KARAR DESTEK MOTORU",
        "tagline": "Eksik ve Belirsiz Veri Altında Güvenilir, Açıklanabilir ve Manipülasyona Dirençli Karar Verme",
        "subtitle": (
            "Contextual Zero Cebiri (CZ-Algebra) ile hiçbir sahte sayı uydurmadan (imputation-free), "
            "ölçümlenen kriter alt-uzayında çalışan ve saklanan maliyetlere karşı asimetrik temkin cezası uygulayan "
            "yüksek güvenceli karar destek prototipi."
        ),
    }


def get_use_cases() -> List[Dict[str, str]]:
    """Sistemin nerelerde kullanılabileceğini açıklayan 6 temel sektörel alan."""
    return [
        {
            "id": "CASE-TENDER",
            "icon": "🏛️",
            "title": "Kamu İhale Süreçleri İçin Karar Destek Prototipi",
            "subtitle": "Gizli maliyet ve eksik teklifleri yakalayan denetim mekanizması",
            "problem": "Teklif veren firmalar başlangıç fiyatını düşük gösterip bakım, yedek parça ve lisans maliyetlerini teklif dosyasında boş bırakabilir. Klasik sistemler bu boşlukları 0 TL sayarak devleti yanıltır.",
            "solution": "R-CZ, eksik maliyet kriterlerini asimetrik ceza (κ_i) ve inceleme bayrağıyla görünür kılar. İki kişili komisyon akışını ve SHA-256 bütünlük makbuzunu prototip olarak gösterir; bu çıktı tek başına mevzuat veya Sayıştay uygunluk belgesi değildir.",
            "action_label": "🏛️ İhale Senaryosunu Gör",
            "target_nav": "🏆 1  Karar Paneli",
            "target_data": "tedarikci",
        },
        {
            "id": "CASE-DEFENSE",
            "icon": "🚁",
            "title": "Savunma Sanayii, İHA / SİHA & Görev Bilgisayarları",
            "subtitle": "Elektronik harp ve jammer altında kesintisiz karar sürekliliği",
            "problem": "Harekât sahasında düşman karıştırması nedeniyle optik, radar veya telemetri sensörlerinden bazıları kararabilir. Klasik algoritmalar eksik veriyi sıfır kabul edip platformu felç eder.",
            "solution": "R-CZ, çift-sıfır cebiriyle (0_A ≠ 0_I) sağlam kalan sensörlerin alt-uzayında O(N × M) deterministik hızla karar desteğini sürdürür. Graceful degradation sağlar.",
            "action_label": "🚁 İHA Doktrinini İncele",
            "target_nav": "🚁 2  İHA / SİHA Doktrini",
            "target_data": "iha",
        },
        {
            "id": "CASE-RADAR",
            "icon": "🎯",
            "title": "Taktik Hava Savunma Tehdit Değerlendirme (TEWA)",
            "subtitle": "Aldatıcı ve eksik imzalı hedeflerin şeffaf önceliklendirilmesi",
            "problem": "Düşman füzeleri veya yem İHA'lar transponder (IFF) veya hız telemetrisini maskeleyebilir. Eksik izler yanlış önceliklendirmeye ve mühimmat israfına yol açabilir.",
            "solution": "Hard Gatekeeper (%50 bilgi barajı) ve asimetrik temkin cezası ile şüpheli temaslar işaretlenir. Otonom angajman yasaktır; harekât subayına izlenebilir danışmanlık verilir.",
            "action_label": "🎯 Radar C2 Senaryosunu Aç",
            "target_nav": "🎯 3  Hava Savunma C2",
            "target_data": "radar",
        },
        {
            "id": "CASE-ENERGY",
            "icon": "⚡",
            "title": "Yenilenebilir Enerji & Kritik Altyapı Yatırımları",
            "subtitle": "Eksik meteorolojik ve fizibilite verilerinde güvenli saha seçimi",
            "problem": "Güneş veya rüzgar santrali sahalarında bazı lokasyonların 10 yıllık ölçüm verisi varken bazılarının sadece 1 yıllık verisi bulunur. Ortalama atamak büyük finansal batık riski doğurur.",
            "solution": "Veri eksiği olan sahalar yapay sayılarla şişirilmez; bilgi kapsama oranı oranında temkin payı uygulanır. Sonuç, doğrulama ve uzman değerlendirmesi gerektiren bir karar desteğidir.",
            "action_label": "⚡ Enerji Senaryosuna Geç",
            "target_nav": "🏆 1  Karar Paneli",
            "target_data": "enerji",
        },
        {
            "id": "CASE-STARTUP",
            "icon": "🚀",
            "title": "Girişim Sermayesi (VC) & Teknoloji Yatırımı",
            "subtitle": "Finansal verisi henüz olgunlaşmamış startupların adil puanlanması",
            "problem": "Erken aşama girişimlerin ciro veya kârlılık verisi henüz oluşmamıştır. Klasik modeller kârlılığı 0 diye iyi fikirleri eler; ortalama atayan modeller ise sahte rakam uydurur.",
            "solution": "Girişimler yalnızca kanıtlanmış metriklerinin (teknik ekip, büyüme hızı, patent) alt-uzayında değerlendirilir. Bilinmeyen finansal riskler için temkinli skor üretilir.",
            "action_label": "🚀 Startup Senaryosunu Gör",
            "target_nav": "🏆 1  Karar Paneli",
            "target_data": "startup",
        },
        {
            "id": "CASE-HEALTH",
            "icon": "🏥",
            "title": "Klinik Onkoloji & Biyoteknoloji İlaç Adayları",
            "subtitle": "Klinik fazları eksik tedavi alternatiflerinin risk analizi",
            "problem": "Yeni ilaç adaylarının bazılarında faz-1 toksisite verisi tam iken bazılarında uzun vadeli yan etki profili henüz tamamlanmamıştır. Yan etkiyi 'yok' saymak ölümcül olabilir.",
            "solution": "Toksisite ve yan etki gibi maliyet kriterleri eksik olan moleküllere Akerlof asimetrik cezası uygulanarak riskin görünür kılınması sağlanır.",
            "action_label": "🏥 Klinik Senaryoyu Aç",
            "target_nav": "🏆 1  Karar Paneli",
            "target_data": "ilac",
        },
    ]


def get_capabilities() -> List[Dict[str, str]]:
    """Platformda neler yapılabileceğini özetleyen 6 ana fonksiyonel yetenek."""
    return [
        {
            "icon": "📊",
            "title": "Eksik Verili Canlı Karar Verme",
            "desc": "Veri setinizdeki eksik veya ölçülemeyen hücrelere rağmen hiçbir uydurma sayı üretmeden matematiksel olarak en tutarlı şampiyonu ve sıralamayı belirler.",
        },
        {
            "icon": "🎛️",
            "title": "Canlı 'What-If' Stres Laboratuvarı",
            "desc": "Kriter ağırlıklarını kaydırarak sıralamanın nasıl değiştiğini anlık görün. Bir adayın maliyetini kasıtlı gizleyerek asimetrik cezanın devreye girişini canlı izleyin.",
        },
        {
            "icon": "⚖️",
            "title": "6 Farklı MCDM Yöntemiyle Kıyaslama",
            "desc": "R-CZ'yi Klasik TOPSIS, Ortalama Atama, VIKOR, PROMETHEE II, SAW ve AHP ile aynı anda yan yana yarıştırın; klasik modellerin nerede aldandığını gözlemleyin.",
        },
        {
            "icon": "📜",
            "title": "Kriptografik Denetim Makbuzu & Rapor",
            "desc": "Girdi matrisini donduran SHA-256 hash mührü, zaman damgalı denetim makbuzu ve kurum içi incelemeye uygun taslak PDF/HTML raporu indirin. Bu çıktı resmi kabul veya hukuki uygunluk belgesi değildir.",
        },
        {
            "icon": "🛡️",
            "title": "Kurumsal Karar Destek Ürün Profilleri",
            "desc": "Resmi İhale Profili (iki kişili komisyon onayı, yakın skor alarmı), Askeri Taktik Profil (insan onayı zorunluluğu, bayat telemetri uyarısı) veya Bilimsel Çekirdek modunda çalıştırın.",
        },
        {
            "icon": "🔬",
            "title": "Şeffaf ve Adım Adım Matematik Matrisleri",
            "desc": "Sütun norm paydalarından (S_j), alt-uzay Öklid mesafelerine (D+, D-) ve ceza çarpanlarına (Γ_i) kadar her matematiksel adımın sayısal ara dökümünü canlı denetleyin.",
        },
    ]


def render_landing_intro_page(st: Any, safe_text: Callable[[object], str]) -> None:
    """R-CZ-TOPSIS Tanıtım ve Giriş (Landing) sayfasını Streamlit üzerinde çizer."""
    meta = get_landing_metadata()
    use_cases = get_use_cases()
    caps = get_capabilities()

    # ==============================================================================
    # 1. BÜYÜK HERO VE KARŞILAMA BANNERI
    # ==============================================================================
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0b132b 0%, #1c2541 45%, #1e3a8a 100%); color: #ffffff; border-radius: 14px; padding: 26px 30px; margin-bottom: 22px; border: 1px solid rgba(255,255,255,0.18); box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.35);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
                <span style="background: rgba(59, 130, 246, 0.28); color: #bfdbfe; border: 1px solid rgba(147, 197, 253, 0.4); padding: 5px 12px; border-radius: 20px; font-size: 0.76rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">
                    🛡️ {safe_text(meta['badge'])}
                </span>
                <span style="background: rgba(16, 185, 129, 0.2); color: #a7f3d0; border: 1px solid rgba(110, 231, 183, 0.35); padding: 5px 12px; border-radius: 20px; font-size: 0.76rem; font-weight: 600;">
                    🔒 Air-Gapped / Sıfır Harici Ağ Bağımlılığı
                </span>
            </div>
            <h1 style="margin: 0 0 10px; font-size: 2.1rem; font-weight: 850; color: #ffffff; letter-spacing: -0.03em; line-height: 1.2;">
                {safe_text(meta['title'])}
            </h1>
            <div style="font-size: 1.10rem; font-weight: 600; color: #93c5fd; margin-bottom: 10px; line-height: 1.4;">
                {safe_text(meta['tagline'])}
            </div>
            <div style="font-size: 0.92rem; color: #cbd5e1; max-width: 980px; line-height: 1.55; margin-bottom: 18px;">
                {safe_text(meta['subtitle'])}
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.12);">
                <span style="font-size: 0.78rem; background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 6px;">📐 Imputation-Free Alt-Uzay</span>
                <span style="font-size: 0.78rem; background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 6px;">⚖️ Asimetrik Maliyet Savunması (κ_i)</span>
                <span style="font-size: 0.78rem; background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 6px;">🚪 Hard Gatekeeper Eşiği (%50)</span>
                <span style="font-size: 0.78rem; background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 6px;">📜 SHA-256 Kriptografik Mühür</span>
                <span style="font-size: 0.78rem; background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 6px;">🎓 TÜBİTAK 2209-A Uyumlu</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==============================================================================
    # 2. HIZLI ERİŞİM VE ÇALIŞMA ALANINA GEÇİŞ ÇAĞRISI (CALL TO ACTION)
    # ==============================================================================
    cta_c1, cta_c2, cta_c3, cta_c4 = st.columns(4)
    with cta_c1:
        if st.button("🚀 Karar Paneline Gir (Sistemi Başlat)", use_container_width=True, type="primary"):
            st.session_state["pending_nav"] = "🏆 1  Karar Paneli"
            st.rerun()
    with cta_c2:
        if st.button("🎛️ Canlı What-If Laboratuvarına Geç", use_container_width=True):
            st.session_state["pending_nav"] = "🎛️ 4  What-If Laboratuvarı"
            st.rerun()
    with cta_c3:
        if st.button("❓ Ceza & Kriter Rehberini Oku", use_container_width=True):
            st.session_state["pending_nav"] = "💡 5  Sistem Rehberi"
            st.rerun()
    with cta_c4:
        if st.button("🧭 Sistem Özellikleri & Envanteri Gör", use_container_width=True):
            st.session_state["pending_nav"] = "🧭 0  Genel Bakış"
            st.rerun()

    st.markdown("---")

    # ==============================================================================
    # 3. BU SİSTEM NEDİR? (TEMEL PROBLEM VE ÇÖZÜM MANTIĞI)
    # ==============================================================================
    st.subheader("💡 1. Bu Sistem Nedir ve Neden Geliştirildi?")
    st.caption("Klasik karar yöntemlerinin eksik veri karşısındaki zafiyetleri ve R-CZ-TOPSIS'in getirdiği bilimsel yenilik:")

    col_prob, col_sol = st.columns(2)
    with col_prob:
        st.markdown(
            """
            <div class="rcz-card-danger" style="height: 100%;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-size: 1.3rem;">❌</span>
                    <h4 style="margin: 0; color: #991b1b; font-size: 1.05rem; font-weight: 750;">Eski Sistemlerin 3 Ölümcül Hatası</h4>
                </div>
                <div style="font-size: 0.88rem; line-height: 1.55;">
                    <p><strong>1. Haksız İnfaz (False Elimination):</strong> Klasik TOPSIS eksik hücreyi <code>0.0</code> kabul eder. 10 kriterden 9'unda mükemmel olan adayın 1 önemsiz bilgisi eksikse adayı orijine çekip haksızca eler.</p>
                    <p><strong>2. Sahte Şampiyonluk (False Inflation):</strong> Maliyet veya fiyat kriteri eksik olan bir adayı 'bedava' (0 TL masraflı) sanarak haksız yere birinci sıraya oturtur.</p>
                    <p><strong>3. Uydurma Sayı Yanılgısı (Imputation Bias):</strong> Ortalama veya regresyonla doldurma modelleri, karar matrisine gerçekte var olmayan sayılar enjekte ederek varyansı bozar ve yasal denetimlerde geçersiz kalır.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_sol:
        st.markdown(
            """
            <div class="rcz-card-success" style="height: 100%;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                    <span style="font-size: 1.3rem;">🛡️</span>
                    <h4 style="margin: 0; color: #065f46; font-size: 1.05rem; font-weight: 750;">R-CZ-TOPSIS'in Getirdiği Çözüm</h4>
                </div>
                <div style="font-size: 0.88rem; line-height: 1.55;">
                    <p><strong>1. Çift-Sıfır Cebiri (0_A ≠ 0_I):</strong> Ölçülen gerçek sıfır (0 TL ceza veya 0 km hız) ile veri yokluğunu (bilinmeyen fiyat/sensör kararması) kesin olarak birbirinden ayırır.</p>
                    <p><strong>2. Imputation-Free Alt-Uzay:</strong> Adayı yapay sayılar uydurmadan, yalnızca verisi olan kriterlerin geometrik alt-uzayında (J_i*) diğer adaylarla yarıştırır.</p>
                    <p><strong>3. Asimetrik Epistemik Ceza (Γ_i):</strong> Fiyat ve arıza gibi maliyetleri gizleyen adaylara Akerlof Limon Piyasası temelli katlanan ceza keser; asgari bilgi barajını (%50) geçemeyen adayları Hard Gatekeeper ile doğrudan eler.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ==============================================================================
    # 4. NELERDE KULLANILABİLİR? (6 TEMEL SEKTÖREL ALAN VE VAKA ÇALIŞMALARI)
    # ==============================================================================
    st.subheader("🌐 2. Bu Sistem Nerelerde Kullanılabilir? (Uygulama Alanları)")
    st.caption("Farklı sektörlerdeki eksik veri ve karar problemlerine özel uyarlanmış 6 temel kurumsal kullanım alanı:")

    c_row1_col1, c_row1_col2, c_row1_col3 = st.columns(3)
    c_row2_col1, c_row2_col2, c_row2_col3 = st.columns(3)
    grid_cols = [c_row1_col1, c_row1_col2, c_row1_col3, c_row2_col1, c_row2_col2, c_row2_col3]

    for idx, uc in enumerate(use_cases):
        col = grid_cols[idx]
        with col:
            st.markdown(
                f"""
                <div class="rcz-card" style="min-height: 290px; height: 100%;">
                    <div>
                        <div style="font-size: 1.6rem; margin-bottom: 6px;">{uc['icon']}</div>
                        <h4 class="rcz-card-title">{safe_text(uc['title'])}</h4>
                        <div class="rcz-card-subtitle">{safe_text(uc['subtitle'])}</div>
                        <div class="rcz-card-body" style="margin-bottom: 8px;">
                            <strong style="color: #991b1b;">Sorun:</strong> {safe_text(uc['problem'])}
                        </div>
                        <div class="rcz-card-body" style="background: rgba(16, 185, 129, 0.08); padding: 7px 10px; border-radius: 6px; border-left: 3px solid #10b981;">
                            <strong style="color: #065f46;">R-CZ Çözümü:</strong> {safe_text(uc['solution'])}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(uc["action_label"], key=f"btn_case_{uc['id']}", use_container_width=True):
                st.session_state["pending_nav"] = uc["target_nav"]
                st.rerun()

    st.markdown("---")

    # ==============================================================================
    # 5. KAVRAMLAR VE SİSTEM SÖZLÜĞÜ (GLOSSARY)
    # ==============================================================================
    st.subheader("📚 3. Temel Kavramlar & Sistem Sözlüğü")
    st.caption("Hard Gatekeeper, Transponder, Epistemik Ceza, Akerlof Limon Piyasası ve platformda geçen tüm kavramların açıklamaları:")

    # 4 Önemli Kavram Vitrini (Öne Çıkanlar)
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown(
            """
            <div class="rcz-card-warning" style="margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 1.3rem;">🚪</span>
                    <strong style="font-size: 0.98rem;">1. Hard Gatekeeper (Asgari Bilgi Barajı)</strong>
                </div>
                <div style="font-size: 0.84rem; line-height: 1.45;">
                    <strong>Ne Demektir?</strong> Bir adayın değerlendirmeye alınabilmesi için kriter ağırlıkları toplamının en az %50'sine (W_threshold) sahip olması şartıdır.<br>
                    <strong>Neden Var?</strong> 10 kriterlik bir ihalede 8 kriteri boş bırakan bir firmanın, bilinen 2 kriteri iyi diye şampiyon olmasını önler; doğrudan eler (Skor: 0.0).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="rcz-card-danger" style="margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 1.3rem;">🍋</span>
                    <strong style="font-size: 0.98rem;">2. Akerlof Limon Piyasası (The Market for Lemons)</strong>
                </div>
                <div style="font-size: 0.84rem; line-height: 1.45;">
                    <strong>Ne Demektir?</strong> Nobel ödüllü iktisat teorisidir: Bir piyasada satıcılar malların arızasını saklar ve alıcılar da ortalama fiyat verirse, kusurlu mallar piyasayı kaplar.<br>
                    <strong>R-CZ Çözümü:</strong> Fiyat veya arıza gibi maliyet kriterlerini saklayan adayların ceza katsayısı (κ_i) katlanır; hilekâr adayın haksız kazancı engellenir.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_k2:
        st.markdown(
            """
            <div class="rcz-card-info" style="margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 1.3rem;">📡</span>
                    <strong style="font-size: 0.98rem;">3. Transponder (IFF - Dost-Düşman Tanıma)</strong>
                </div>
                <div style="font-size: 0.84rem; line-height: 1.45;">
                    <strong>Ne Demektir?</strong> Uçak ve füzelerin kimlik ve dost/düşman kodunu yer radarlarına bildiren vericidir.<br>
                    <strong>Sistemdeki Önemi:</strong> Düşman veya şüpheli hedefler transponder'ı kapatır (0_I / Inaction). R-CZ bunu sıfır sanmaz; şüpheli temas olarak işaretleyip operatörün onayına sunar.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="rcz-card-success" style="margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 1.3rem;">⚡</span>
                    <strong style="font-size: 0.98rem;">4. Epistemik Ceza (Epistemic Penalty - Γ_i)</strong>
                </div>
                <div style="font-size: 0.84rem; line-height: 1.45;">
                    <strong>Ne Demektir?</strong> Bilgi eksikliğinden doğabilecek bilinmeyen risklere karşı adayın temel puanından (C_base) kesilen matematiksel güvenlik payıdır.<br>
                    <strong>Hesaplama:</strong> Γ_i = W_i^(α · κ_i). Veri tamsa ceza %0'dır (Γ_i = 1.0); veri eksildikçe puan orantılı olarak kırılır.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # İnteraktif Arama & Kategori Sözlüğü
    with st.expander("🔍 Tüm Kavramlar Sözlüğünü Aç ve Arama Yap (18 Terim)", expanded=False):
        render_glossary_component(st, safe_text, key_prefix="landing_glossary")

    st.markdown("---")

    # ==============================================================================
    # 6. BU SİSTEMLE NELER YAPILABİLİR? (FONKSİYONEL YETENEKLER)
    # ==============================================================================
    st.subheader("⚡ 4. Bu Sistemle Neler Yapılabilir? (Platform Yetenekleri)")
    st.caption("Analiz, simülasyon, denetim ve resmi raporlama açısından platformun sunduğu fonksiyonlar:")

    cap_c1, cap_c2 = st.columns(2)
    for idx, cap in enumerate(caps):
        col = cap_c1 if idx % 2 == 0 else cap_c2
        with col:
            st.markdown(
                f"""
                <div class="rcz-card" style="min-height: 90px; height: auto; display: flex; flex-direction: row; gap: 12px; align-items: flex-start; padding: 14px 16px;">
                    <div style="font-size: 1.6rem; background: rgba(37, 99, 235, 0.1); padding: 8px 10px; border-radius: 8px;">{cap['icon']}</div>
                    <div>
                        <h4 class="rcz-card-title">{safe_text(cap['title'])}</h4>
                        <div class="rcz-card-body">{safe_text(cap['desc'])}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ==============================================================================
    # 7. SİSTEME GİRİŞ VE ÇALIŞMA ADIMLARI (3 ADIMDA BAŞLA)
    # ==============================================================================
    st.subheader("🏁 5. Nasıl Kullanılır? (3 Kolay Adımda Karar Süreci)")
    st.caption("Sistemi ilk kez kullanan karar vericiler için hızlı başlangıç yönergesi:")

    step_c1, step_c2, step_c3 = st.columns(3)
    with step_c1:
        st.markdown(
            """
            <div class="rcz-card" style="min-height: 140px; height: 100%;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="background: #1e3a8a; color: white; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.82rem;">1</span>
                    <h4 class="rcz-card-title" style="margin: 0;">Senaryo ve Veri Seçin</h4>
                </div>
                <p class="rcz-card-body" style="margin: 0;">
                    Sol menüden hazır 9 benchmark veri setinden birini (İhale, Radar TEWA, İHA, UCI Automobile, Elektrikli Araçlar vb.) seçin veya kendi CSV dosyanızı yükleyin.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with step_c2:
        st.markdown(
            """
            <div class="rcz-card" style="min-height: 140px; height: 100%;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="background: #1e3a8a; color: white; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.82rem;">2</span>
                    <h4 class="rcz-card-title" style="margin: 0;">Güvenlik & Eşik Ayarlarını Belirleyin</h4>
                </div>
                <p class="rcz-card-body" style="margin: 0;">
                    Kurumunuzun risk toleransına göre riskten kaçınma katsayısını (α) ve asgari bilgi barajını (W_threshold) belirleyin. Gerekirse İhale veya Askeri profili aktif edin.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with step_c3:
        st.markdown(
            """
            <div class="rcz-card" style="min-height: 140px; height: 100%;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                    <span style="background: #1e3a8a; color: white; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.82rem;">3</span>
                    <h4 class="rcz-card-title" style="margin: 0;">Karar Analizini ve Mührü İndirin</h4>
                </div>
                <p class="rcz-card-body" style="margin: 0;">
                    Şampiyon adayı, net adalet kazanımlarını ve elenen adayları anında görün. Tek tıkla yazdırılabilir resmi karar tutanağını (PDF/HTML) ve SHA-256 mührünü indirin.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ==============================================================================
    # 8. ALT AKSİYON ÇAĞRISI (FINAL FOOTER CTA)
    # ==============================================================================
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    f_c1, f_c2 = st.columns([2, 1])
    with f_c1:
        st.markdown(
            """
            <div class="rcz-card-info" style="padding: 14px 18px;">
                <div style="font-weight: 750; font-size: 0.95rem; margin-bottom: 4px;">🚀 Sisteme Giriş Yapmaya Hazır mısınız?</div>
                <div style="font-size: 0.84rem; line-height: 1.4;">
                    Aktif karar senaryosu ve canlı şampiyon kürsüsü için Karar Paneline geçebilir veya sol menüden dilediğiniz modülü seçebilirsiniz.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f_c2:
        if st.button("🏁 Karar Paneline Geç ve Çalıştır", type="primary", use_container_width=True, key="btn_final_cta"):
            st.session_state["pending_nav"] = "🏆 1  Karar Paneli"
            st.rerun()
