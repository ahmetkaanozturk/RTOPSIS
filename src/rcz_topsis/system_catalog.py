"""R-CZ-TOPSIS Sistem ve Platform Özellik Kataloğu (System & Feature Catalog).

Bu modül, platformun mevcut tüm mimari bileşenlerini, ürün profillerini,
özellik envanterini, kullanım akışlarını ve üretim sınırlamalarını
tek bir doğrulanabilir veri yapısında toplar.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class FeatureStatus(str, Enum):
    AVAILABLE = "Mevcut"                           # Kodda tam çalışan ve test edilmiş
    PARTIAL = "Kısmen Mevcut"                      # Kodda var ancak harici entegrasyona bağlı
    DESIGN_ONLY = "Tasarım/Dokümantasyon"          # Mimari ve şartname var, tam bağlanmamış
    MISSING = "Eksik (Üretim İçin Gerekli)"        # Kurumsal üretim için geliştirilmesi gereken


@dataclass(frozen=True)
class FeatureItem:
    """Tek bir platform yeteneğinin envanter kartı."""
    id: str
    category: str
    name: str
    description: str
    value_to_user: str
    module_or_file: str
    status: FeatureStatus
    limitation: Optional[str] = None


@dataclass(frozen=True)
class ProfileComparisonRow:
    """Ürün profilleri karşılaştırma tablosu satırı."""
    criterion: str
    scientific: str
    tender: str
    military: str


def get_system_overview_metadata() -> Dict[str, Any]:
    """Sistem üst bilgi ve durum özetini döner."""
    return {
        "system_name": "R-CZ-TOPSIS Platformu",
        "title": "Eksik Verili Karar Destek ve Risk Analizi Sistemi",
        "description": (
            "Contextual Zero Algebra (CZ-Algebra) temelinde eksik ve karartılmış veri altında "
            "alt-uzay izdüşümü ve asimetrik epistemik ceza uygulayan çok kriterli karar destek platformu."
        ),
        "engine_version": "v1.1.1 (Python Core)",
        "dashboard_version": "v1.2-enterprise-preview",
        "system_readiness": "Yüksek Güvenceye Hazırlanmış Araştırma & Karar Destek Prototipi",
        "doctrine_warning": (
            "YASAL VE DOKTRİN UYARISI: Bu sistem tek başına nihai ihale yüklenicisi belirleme, "
            "resmi satın alma taahhüdü oluşturma veya otonom askeri silah tahsisi/angajman kararı verme "
            "yetkisine sahip değildir. Çıktılar yalnızca yetkili insan karar vericilere (Komisyon Üyeleri, "
            "Taktik Harekât Subayı) gerekçeli, açıklanabilir ve denetlenebilir teknik karar desteği sunar."
        ),
    }


def get_summary_metrics() -> List[Dict[str, str]]:
    """Doğrulanabilir özet metrik kartları."""
    return [
        {
            "label": "Karar Motoru",
            "value": "R-CZ-TOPSIS v1.1",
            "delta": "Global Alt-Uzay",
            "help": "Global ağırlıklı alt-uzay izdüşümü ve asimetrik epistemik ceza (Γ_i)",
        },
        {
            "label": "Ürün Profilleri",
            "value": "3 Aktif Profil",
            "delta": "Akademik / İhale / Askeri",
            "help": "Ortak motor üzerinde çalışan ayrı politikalı kurumsal profiller",
        },
        {
            "label": "Veri Doğrulama",
            "value": "Strict Fail-Closed",
            "delta": "NaN & Boyut Denetimli",
            "help": "DecisionDataset.validate() ile geçersiz matrisler hesaplamaya alınmaz",
        },
        {
            "label": "Audit & Bütünlük",
            "value": "Kalıcı Hash Zinciri",
            "delta": "Append-Only JSONL + İmza",
            "help": "PersistentAuditStore ve ReceiptSigner ile mühürleme",
        },
        {
            "label": "Test Kapsamı",
            "value": "70 / 71 Geçti",
            "delta": "1 Bilinçli xfail (xfail: Maliyet Saklama)",
            "help": "Pytest: matematiksel invaryantlar, stres, duman ve kurumsal testler",
        },
        {
            "label": "C++ Conformance",
            "value": "Analitik Protokol",
            "delta": "Derleme Testi Değil",
            "help": "rcz_engine.hpp şartnamesi Python motoru ile analitik olarak test edilmektedir",
        },
        {
            "label": "Air-Gapped Hazırlık",
            "value": "%100 Çevrimdışı",
            "delta": "Sıfır Dış Ağ Çağrısı",
            "help": "Google Fonts kaldırıldı, yerel sistem fontları ve requirements-frozen.txt kilitli",
        },
    ]


def get_feature_inventory() -> List[FeatureItem]:
    """Platformun 32 maddelik doğrulanmış gerçek özellik envanterini döner."""
    return [
        # 1. Çekirdek Karar Motoru & Matematik
        FeatureItem(
            id="FEAT-01",
            category="Çekirdek Karar Motoru & Matematik",
            name="R-CZ-TOPSIS Karar Motoru",
            description="Contextual Zero cebiri ile eksik verili ortamlarda alt-uzay mesafeleri hesaplayan ana algoritma.",
            value_to_user="Veri eksik olsa dahi yapay veri uydurmadan (imputation-free) matematiksel olarak tutarlı sıralama sunar.",
            module_or_file="src/rcz_topsis/core.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Adayların tamamı aynı kriterde eksikse veya kolon tamamen boşsa çalışmaz.",
        ),
        FeatureItem(
            id="FEAT-02",
            category="Çekirdek Karar Motoru & Matematik",
            name="Eksik Veri İşleme (Imputation-Free)",
            description="Ortalama veya regresyonla doldurma yapmaksızın, her adayı yalnızca ölçülebildiği kriterlerin alt-uzayında değerlendirir.",
            value_to_user="Uydurma veriyle sahte kesinlik illüzyonu oluşturulmasını engeller.",
            module_or_file="src/rcz_topsis/core.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Ölçüm sayısı azaldıkça alt-uzayın boyutu küçülür, temkin cezası artar.",
        ),
        FeatureItem(
            id="FEAT-03",
            category="Çekirdek Karar Motoru & Matematik",
            name="0_A (Ölçülmüş Sıfır) vs 0_I (Bilinmeyen Veri) Ayrımı",
            description="Sıfır puan almış gerçek performans ile ölçülmemiş/karartılmış hücreyi veri yapısı seviyesinde ayırır.",
            value_to_user="Gerçek sıfır performans ile sensör kararmasının birbiriyle karışmasını önler.",
            module_or_file="src/rcz_topsis/types.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Kullanıcının veri setini hazırlarken Context.ACTION ve Context.INACTION ayrımını doğru kodlaması gerekir.",
        ),
        FeatureItem(
            id="FEAT-04",
            category="Çekirdek Karar Motoru & Matematik",
            name="Global Alt-Uzay Ağırlıklandırması (v1.1)",
            description="v1.0'daki yerel ağırlık dağıtımından kaynaklanan koordinat şişmesini (coordinate inflation) önlemek için global ağırlık izdüşümü kullanır.",
            value_to_user="Az kriteri bilinen alternatiflerin yapay biçimde üst sıralara tırmanmasını engeller.",
            module_or_file="src/rcz_topsis/core.py",
            status=FeatureStatus.AVAILABLE,
            limitation="İsteyen kullanıcılar araştırma amacıyla v1.0 yerel ağırlık modunu seçmeli olarak açabilir.",
        ),
        FeatureItem(
            id="FEAT-05",
            category="Çekirdek Karar Motoru & Matematik",
            name="Fayda ve Maliyet Kriterleri Asimetrisi",
            description="Kriterleri CritType.BENEFIT ve CritType.COST olarak ayırarak ideal ve anti-ideal noktaları yönlü hesaplar.",
            value_to_user="Düşük fiyat veya düşük risk gibi ters yönlü kriterleri doğru optimize eder.",
            module_or_file="src/rcz_topsis/core.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Maliyet kriterlerinde aşırı uç değerler normalizasyon aralığını sıkıştırabilir.",
        ),
        FeatureItem(
            id="FEAT-06",
            category="Çekirdek Karar Motoru & Matematik",
            name="Kapsama Oranı (W_i) ve Hard Gatekeeper Eşiği",
            description="Adayın bilinen kriter ağırlıkları toplamı belirlenen eşiğin (w_threshold) altındaysa adayı doğrudan eler.",
            value_to_user="Yetersiz bilgiye sahip şüpheli veya eksik tekliflerin/hedeflerin yarışta kalmasını engeller.",
            module_or_file="src/rcz_topsis/core.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Eşik çok yüksek seçilirse (ör. %80) hafif eksik verili kaliteli adaylar elenebilir.",
        ),
        FeatureItem(
            id="FEAT-07",
            category="Çekirdek Karar Motoru & Matematik",
            name="Gamma / Asimetrik Epistemik Güvenilirlik Cezası",
            description="Eksik kriter ağırlıklarına ve alfa risk parametresine bağlı olarak skora ceza katsayısı uygular (C* = C_base * Gamma_i).",
            value_to_user="Tam verili adayların hakkını korurken, eksik verili adayları temkin payıyla geriye iter.",
            module_or_file="src/rcz_topsis/core.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Alfa = 0 seçilirse ceza devre dışı kalır; bu seçim temkinsizdir.",
        ),
        FeatureItem(
            id="FEAT-08",
            category="Çekirdek Karar Motoru & Matematik",
            name="Alternatif Sıralama ve Bağıl Yakınlık Skoru",
            description="Tüm adayları C* nihai skoru üzerinden büyükten küçüğe sıralar ve sıra numarası atar.",
            value_to_user="Karar vericiye anında net bir önceliklendirme ve tavsiye listesi sunar.",
            module_or_file="src/rcz_topsis/core.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Elenen adaylar geçerli adayların arkasında listelenir ve INSUFFICIENT_DATA statüsüyle işaretlenir.",
        ),
        FeatureItem(
            id="FEAT-09",
            category="Çekirdek Karar Motoru & Matematik",
            name="Açıklanabilirlik ve Matematiksel Ara Değerler",
            description="İdeal mesafeler (d+), anti-ideal mesafeler (d-), temel skor (C_base) ve ceza katsayısını tek tek raporlar.",
            value_to_user="Kara kutu bir model yerine her hesaplama adımını kurum içi inceleme için görünür kılar; resmi denetim kabulü veya sertifikasyon garantisi vermez.",
            module_or_file="src/rcz_topsis/core.py (RCZExplanation)",
            status=FeatureStatus.AVAILABLE,
            limitation="Ara değerler uzmanlık gerektiren çok kriterli matris matematiği içerir.",
        ),

        # 2. Veri Doğrulama ve Sözleşme Katmanı
        FeatureItem(
            id="FEAT-10",
            category="Veri Sözleşmesi & Bütünlük",
            name="CSV / Veri Seti Yükleme ve Dinamik Parser",
            description="9 farklı sektör benchmark CSV'si ve özel kullanıcı CSV yükleme yeteneği.",
            value_to_user="Kendi kurumsal matrisini yükleyip anında analiz edebilme imkanı.",
            module_or_file="dashboard.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Maksimum dosya boyutu bellek ile sınırlıdır; büyük veri tabloları için tasarlanmamıştır.",
        ),
        FeatureItem(
            id="FEAT-11",
            category="Veri Sözleşmesi & Bütünlük",
            name="Kapsamlı Fail-Closed Şema Doğrulaması",
            description="DecisionDataset.validate() ile boyut, Sigma {'A', 'I'}, pozitif ağırlık, sonlu sayı ve boş kolon denetimi.",
            value_to_user="Hatalı veya eksik biçimlendirilmiş verinin motoru çökertecek şekilde çalışmasını engeller.",
            module_or_file="src/rcz_topsis/schema.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Doğrulama başarısız olursa hesaplama derhal durdurulur (fail-closed).",
        ),
        FeatureItem(
            id="FEAT-12",
            category="Veri Sözleşmesi & Bütünlük",
            name="Veri Seti Meta Verisi ve Köken (Provenance)",
            description="Her veri seti için gerçek/sentetik ayrımı, lisans ve köken bilgisi tutan merkezi kayıt yapısı.",
            value_to_user="Hangi verinin sentetik askeri simülasyon, hangisinin gerçek UCI testi olduğunu şeffafça açıklar.",
            module_or_file="data/DATASET_METADATA.json",
            status=FeatureStatus.AVAILABLE,
            limitation="Meta veriler statik JSON dosyasında tutulur; dış veritabanına bağlı değildir.",
        ),
        FeatureItem(
            id="FEAT-13",
            category="Veri Sözleşmesi & Bütünlük",
            name="Kayıpsız IEEE-754 SHA-256 Veri Mührü",
            description="Girdi matrisi, konfigürasyon ve aday tanımlarından f'{val:.15e}' formatında deterministik hash üretimi.",
            value_to_user="Raporun hangi veri ve parametrelerle üretildiğinin matematiksel ispatını sağlar.",
            module_or_file="src/rcz_topsis/schema.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Farklı mimarilerde float serileştirme farkları yaşanmaması için IEEE-754 kanonik sıralama şarttır.",
        ),
        FeatureItem(
            id="FEAT-14",
            category="Veri Sözleşmesi & Bütünlük",
            name="Kalıcı Denetim Deposu (Audit Hash Chain)",
            description="Olayları append-only JSONL formatında diske kaydeden ve açılışta zincir bütünlüğünü denetleyen mekanizma.",
            value_to_user="Geçmiş analizlerin silinmesi veya sonradan değiştirilmesi durumunda tahrifatı anında yakalar.",
            module_or_file="src/rcz_topsis/audit.py (PersistentAuditStore)",
            status=FeatureStatus.AVAILABLE,
            limitation="Dosya sistemi bazlıdır; WORM donanım kilidi veya dağıtık defter değildir.",
        ),

        # 3. Resmi İhale ve Tedarik Profili
        FeatureItem(
            id="FEAT-15",
            category="Resmi İhale & Tedarik Profili",
            name="Resmi İhale Profili Değerlendirmesi",
            description="4734 Sayılı Kamu İhale Kanunu ve kurumsal tedarik ilkelerine uyumlu karar destek raporu üretimi.",
            value_to_user="Teklifleri çok boyutlu değerlendirirken komisyon için yasal mevzuata uygun gerekçe sunar.",
            module_or_file="src/rcz_topsis/profiles/tender.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Yazılım ihale mercii veya yasal karar makamı değildir; tavsiye raporudur.",
        ),
        FeatureItem(
            id="FEAT-16",
            category="Resmi İhale & Tedarik Profili",
            name="İki Kişili Komisyon Onay Kuralı (Two-Person Rule)",
            description="Komisyon Başkanı ve Mali Denetçi rolleri doğrulanmadan resmi değerlendirme yapılmasını engelleyen kontrol.",
            value_to_user="Tek bir operatörün usulsüz ihale kararı üretmesini kurumsal olarak engeller.",
            module_or_file="src/rcz_topsis/security/auth.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Dashboard arayüzünde session kimlikleri prototip düzeyindedir; kurumsal SSO entegrasyonu gerektirir.",
        ),
        FeatureItem(
            id="FEAT-17",
            category="Resmi İhale & Tedarik Profili",
            name="Yakın Skor İnceleme Alarmı (Close Score Alert)",
            description="İlk iki teklif arasındaki puan farkı <= %2.0 ise komisyona zorunlu inceleme maddesi oluşturur.",
            value_to_user="Kıl payı farkla kazanan tekliflerin komisyon tarafından derinlemesine incelenmesini sağlar.",
            module_or_file="src/rcz_topsis/profiles/tender.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Eşik değeri (%2.0) şartnameye göre ayarlanabilir olmalıdır.",
        ),
        FeatureItem(
            id="FEAT-18",
            category="Resmi İhale & Tedarik Profili",
            name="Kritik Maliyet vs İkincil Maliyet Ayrımı",
            description="Teklif ana fiyatı eksikse zorunlu savunma bayrağı açılırken, bakım gibi ikincil maliyetlerde yalnızca ikaz üretilir.",
            value_to_user="Önemsiz bir yan kriter yüzünden teklifin kilitlenmesini önler, ana fiyat saklamayı affetmez.",
            module_or_file="src/rcz_topsis/profiles/tender.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Maliyet gizleme riski matematiksel olarak tamamen sıfırlanamaz; yasal savunma süreci şarttır.",
        ),

        # 4. Askeri Taktik Karar Destek Profili
        FeatureItem(
            id="FEAT-19",
            category="Askeri Taktik Advisory Profili",
            name="Askeri Taktik Karar Destek Profili (C2/TEWA)",
            description="Hava savunma radar izleri ve taktik hedefler için tehdit önceliklendirme ve danışmanlık katmanı.",
            value_to_user="Harekât subayına yoğun elektronik harp altında rasyonel hedef öncelik sıralaması sunar.",
            module_or_file="src/rcz_topsis/profiles/military_advisory.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Canlı askeri link (Link-16 vb.) veya C2 radar donanım arayüzü henüz entegre değildir.",
        ),
        FeatureItem(
            id="FEAT-20",
            category="Askeri Taktik Advisory Profili",
            name="Kesin İnsan Onaylı Kullanım (Human-in-the-Loop)",
            description="Sistemin yalnızca tavsiye ürettiğini, nihai angajman sorumluluğunun harekât subayında olduğunu zorunlu kılan doktrin.",
            value_to_user="Askeri etik ve uluslararası angajman kurallarına tam uyum sağlar.",
            module_or_file="src/rcz_topsis/profiles/military_advisory.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Harekât subayının sistemi körlemesine onaylamaması (automation bias) için eğitim gereklidir.",
        ),
        FeatureItem(
            id="FEAT-21",
            category="Askeri Taktik Advisory Profili",
            name="Otonom Angajman Yasağı Kısıtı",
            description="AUTONOMOUS_ENGAGEMENT_ALLOWED bayrağı kod seviyesinde False olarak kilitlenmiştir; aktif edilirse hata fırlatır.",
            value_to_user="Yazılımın kontrolsüz silah tetiklemesi yapamayacağını garanti eder.",
            module_or_file="src/rcz_topsis/profiles/military_advisory.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Donanımsal silah arayüzü bulunmadığından bu kısıt yazılım katmanında geçerlidir.",
        ),
        FeatureItem(
            id="FEAT-22",
            category="Askeri Taktik Advisory Profili",
            name="Telemetri Tazeliği ve Sensör Yaşı Kontrolü",
            description="Sensör verisi gecikmiş izleri (stale telemetri) işaretler; kritik sınırı aşanları dondurur.",
            value_to_user="Bayatlamış hedef koordinatlarına körlemesine müdahale edilmesini engeller.",
            module_or_file="src/rcz_topsis/profiles/military_advisory.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Tazelik eşiği hedef türüne (balistik füze vs. İHA) göre dinamik uyarlanmalıdır.",
        ),
        FeatureItem(
            id="FEAT-23",
            category="Askeri Taktik Advisory Profili",
            name="Karartma / Jamming Kök Neden Ayrımı",
            description="MissingReason enumu ile sensör arızası ile kasıtlı düşman elektronik taarruzunu (jamming) birbirinden ayırır.",
            value_to_user="Operatörün radar karartmasını anlık olarak tespit etmesini ve temkinli davranmasını sağlar.",
            module_or_file="src/rcz_topsis/schema.py & profiles/military_advisory.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Kök neden analizi sensör sağlık telemetrisi ile beslenmelidir.",
        ),
        FeatureItem(
            id="FEAT-24",
            category="Askeri Taktik Advisory Profili",
            name="Güvenli Duruş (Fail-Closed / Hold Durumu)",
            description="Tüm hedefler veri yetersizliği veya aşırı bayatlık altındaysa sistem 'HOLD_NO_ACTIONABLE_TRACKS' üretir ve hedef önermez.",
            value_to_user="Kör noktada veya yoğun karartmada rastgele hedefe yönlendirme yapılmasını önler.",
            module_or_file="src/rcz_topsis/profiles/military_advisory.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Bekleme durumunda operatörün optik/manuel keşif kanallarına başvurması gerekir.",
        ),

        # 5. Analiz, Simülasyon ve Karşılaştırma
        FeatureItem(
            id="FEAT-25",
            category="Analiz, Simülasyon & Karşılaştırma",
            name="Canlı 'What-If' Duyarlılık Laboratuvarı",
            description="Ağırlıklar, eksik veri hücreleri ve ceza katsayıları anlık değiştirildiğinde sıralamanın nasıl tepki verdiğini simüle eder.",
            value_to_user="Kararın ağırlık değişimlerine veya potansiyel veri kayıplarına ne kadar dayanıklı olduğunu test eder.",
            module_or_file="dashboard.py (Modül 4)",
            status=FeatureStatus.AVAILABLE,
            limitation="Yalnızca arayüz üzerinden dinamik analiz içindir; otomatik Monte Carlo duyarlılık raporu üretmez.",
        ),
        FeatureItem(
            id="FEAT-26",
            category="Analiz, Simülasyon & Karşılaştırma",
            name="Klasik MCDM Yöntemleri Karşılaştırması",
            description="R-CZ-TOPSIS'i Klasik TOPSIS, Mean-Imputation, VIKOR, PROMETHEE II ve SAW ile yan yana kıyaslar.",
            value_to_user="Eksik veri doldurmanın sıralamayı nasıl bozduğunu diğer yöntemlerle somut olarak kanıtlar.",
            module_or_file="src/rcz_topsis/mcdm_comparisons.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Karşılaştırma yöntemleri eksik veriyi sıfır veya ortalama ile doldurmak zorundadır.",
        ),
        FeatureItem(
            id="FEAT-27",
            category="Analiz, Simülasyon & Karşılaştırma",
            name="Benchmark ve Stres Testi Çerçevesi",
            description="MCAR, MAR ve MNAR desenlerinde %10-%50 kayıp oranlarında Monte Carlo karşılaştırması yapar.",
            value_to_user="Farklı kayıp mekanizmalarında yöntemlerin sıralama korelasyonunu ölçer; tek başına üstünlük kanıtı değildir.",
            module_or_file="test_stress.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Yüksek iterasyonlu testler uzun sürdüğü için pytest aşamasında sınırlı seed ile çalışır.",
        ),
        FeatureItem(
            id="FEAT-28",
            category="Analiz, Simülasyon & Karşılaştırma",
            name="Plotly İnteraktif Grafikler ve Görselleştirme",
            description="Radar diyagramları, ceza dağılım barları ve mesafe projeksiyonu ısı haritaları.",
            value_to_user="Karmaşık karar verilerini yönetici sunumuna uygun görsel hale getirir.",
            module_or_file="dashboard.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Plotly JS bileşeni tarayıcıda çalışır; statik PDF ihracında vektörel çizim olarak çıkmaz.",
        ),
        FeatureItem(
            id="FEAT-29",
            category="Analiz, Simülasyon & Karşılaştırma",
            name="Rapor, CSV ve İmzalı Makbuz İhracı",
            description="Analiz sonuçlarını, ham metrikleri ve SHA-256 imzalı makbuzu dışa aktarma yeteneği.",
            value_to_user="Denetim dosyasına eklenebilecek doğrulanabilir veri paketi sağlar.",
            module_or_file="dashboard.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Resmi e-imza kartı (SmartCard/dongle) doğrudan entegre değildir; HMAC çıktısı sunulur.",
        ),

        # 6. Altyapı, Dağıtım ve Sertifikasyon Durumu
        FeatureItem(
            id="FEAT-30",
            category="Altyapı, Güvenlik & Dağıtım",
            name="Air-Gapped / On-Premise Dağıtım Hazırlığı",
            description="Harici CDN ve Google Fonts çağrıları temizlenmiş, kilitli bağımlılık listesi (requirements-frozen.txt) ile internetsiz çalışabilme.",
            value_to_user="İnternet çıkışı olmayan izole askeri ağlarda ve kurum içi sunucularda güvenle çalışır.",
            module_or_file="requirements-frozen.txt & dashboard.py",
            status=FeatureStatus.AVAILABLE,
            limitation="Kurulum paketinin offline wheel paketi olarak önceden taşınması gerekir.",
        ),
        FeatureItem(
            id="FEAT-31",
            category="Altyapı, Güvenlik & Dağıtım",
            name="C++ Çekirdek Motor Şartnamesi (Porting Specification)",
            description="Gömülü sistemler ve görev bilgisayarları için rcz_engine.hpp C++17 prototipi ve analitik denklik testi.",
            value_to_user="İHA veya radar görev bilgisayarlarına doğrudan entegre edilebilecek C++ yol haritası sunar.",
            module_or_file="include/rcz_engine.hpp & test_conformance.py",
            status=FeatureStatus.PARTIAL,
            limitation="Şu an analitik test Python üzerinden simüle edilmektedir; gerçek C++ derleyici CI derlemesi aktif değildir.",
        ),
        FeatureItem(
            id="FEAT-32",
            category="Altyapı, Güvenlik & Dağıtım",
            name="Kapsamlı Test ve Güvence Paketi",
            description="Çekirdek, invaryant, duman ve kurumsal profil testlerinden oluşan otomatik doğrulama paketi.",
            value_to_user="Algoritmanın matematiksel sınırlarını (0..1) ve güvenlik kurallarını sürekli denetler.",
            module_or_file="test_*.py",
            status=FeatureStatus.AVAILABLE,
            limitation="1 test (maliyet gizleme cezası) xfail olarak işaretlidir; ekonomik asimetri sınırını belgeler.",
        ),
    ]


def get_profile_comparisons() -> List[ProfileComparisonRow]:
    """Üç ürün profilinin 10 başlıkta karşılaştırmasını döner."""
    return [
        ProfileComparisonRow(
            criterion="Kullanım Amacı",
            scientific="Akademik araştırma, algoritma kıyaslama, tez ve deneysel stres testleri.",
            tender="Kamu ve özel sektör mal/hizmet tedariki, yüklenici değerlendirme tavsiyesi.",
            military="Taktik hava savunma radar izleri ve hedef önceliklendirme karar desteği.",
        ),
        ProfileComparisonRow(
            criterion="Kullanıcı Tipi",
            scientific="Araştırmacı, Veri Bilimci, Endüstri Mühendisi.",
            tender="İhale Komisyon Başkanı, Mali Denetçi, Satın Alma Uzmanı.",
            military="Taktik Harekât Subayı, Hava Savunma Komutanı, C2 Operatörü.",
        ),
        ProfileComparisonRow(
            criterion="İnsan Onayı Zorunluluğu",
            scientific="İsteğe bağlı (deneysel analiz).",
            tender="Zorunlu (İhale komisyonu kararı olmadan yasal geçerliliği yoktur).",
            military="Mutlak Zorunlu (NATO/Milli Doktrin: Human-in-the-Loop).",
        ),
        ProfileComparisonRow(
            criterion="Eksik Veri Politikası",
            scientific="Parametrik (Alfa ve w_threshold serbestçe ayarlanabilir).",
            tender="Katı (Teknik eşik %50 altındaysa doğrudan eleme; temkin cezası uygulanır).",
            military="Fail-Closed (Sensör kararmasında temkin cezası; eşik altındaysa bekleme/hold).",
        ),
        ProfileComparisonRow(
            criterion="Maliyet Kriteri Politikası",
            scientific="Standart maliyet minimizasyonu.",
            tender="Kritik/İkincil maliyet ayrımı; teklif fiyatı eksikse savunma talebi zorunlu.",
            military="Cephane sarfiyatı / risk maliyeti değerlendirmesi.",
        ),
        ProfileComparisonRow(
            criterion="Audit Yaklaşımı",
            scientific="Basit SHA-256 özeti.",
            tender="İki kişili onay (Two-Person) + Kriptografik Denetim Makbuzu + Kalıcı JSONL.",
            military="Operatör ID + Görev Kodu + Telemetri Tazeliği Mührü + Kalıcı Denetim.",
        ),
        ProfileComparisonRow(
            criterion="Çıktı Türü",
            scientific="Skorlar, grafikler ve akademik karşılaştırma tabloları.",
            tender="Resmi İhale Tavsiye Tutanağı, Savunma Bayrakları, İmzalı Makbuz.",
            military="Taktik Hedef Öncelik Kartları, Bayat Telemetri ve Karartma Uyarıları.",
        ),
        ProfileComparisonRow(
            criterion="Nihai Karar Yetkisi",
            scientific="Yoktur (Analitik sonuç).",
            tender="Kesinlikle Yoktur (Yetki İhale Komisyonu üyelerindedir).",
            military="Kesinlikle Yoktur (Yetki Taktik Harekât Subayındadır).",
        ),
        ProfileComparisonRow(
            criterion="Mevcut Güvenlik Seviyesi",
            scientific="Açık araştırma ortamı.",
            tender="Prototip seviyesinde iki kişili rol denetimi ve veri mührü.",
            military="Prototip seviyesinde fail-closed duruş ve otonom angajman kilidi.",
        ),
        ProfileComparisonRow(
            criterion="Önemli Sınırlamalar",
            scientific="Gerçek saha veri bağlantısı yoktur; statik matrislerle çalışır.",
            tender="Kurumsal ERP/EKAP entegrasyonu ve resmi e-imza kartı entegre değildir.",
            military="Gerçek radar Link-16 arayüzü ve operasyonel askeri sertifikasyon yoktur.",
        ),
    ]


def get_usage_flow_steps() -> List[Dict[str, str]]:
    """12 adımlı standart karar destek kullanım akışını döner."""
    return [
        {
            "step": "1",
            "title": "Veri Seti Seçimi / Yükleme",
            "desc": "Kullanıcı 9 hazır sektör benchmarkından birini seçer veya kendi çok kriterli CSV matrisini sisteme yükler.",
        },
        {
            "step": "2",
            "title": "Veri Sözleşmesi Oluşturma (Contract)",
            "desc": "Yüklenen tablo CriterionDef, AlternativeDef ve matris formatında DecisionDataset sözleşmesine dönüştürülür.",
        },
        {
            "step": "3",
            "title": "Sıkı Girdi Doğrulaması (Fail-Closed)",
            "desc": "DecisionDataset.validate() çalıştırılır. Matris boyutları, Sigma 'A'/'I' değerleri, ağırlık toplamı (1.0) ve sonluluk kontrol edilir.",
        },
        {
            "step": "4",
            "title": "Kriter ve Ağırlık Tanımlama",
            "desc": "Fayda ve maliyet yönleri belirlenir; kriter önem ağırlıkları normalize edilir (toplam = 1.0).",
        },
        {
            "step": "5",
            "title": "Eksik Veri ve Kapsama Analizi",
            "desc": "Hücreler 0_A (ölçülmüş sıfır) ve 0_I (bilinmeyen) olarak ayrılır; her adayın bilgi kapsama oranı (W_i) hesaplanır.",
        },
        {
            "step": "6",
            "title": "R-CZ-TOPSIS Hesaplama Motoru",
            "desc": "Global alt-uzay izdüşümüyle vektör normalizasyonu, ideal ve anti-ideal noktalar ve alt-uzay mesafeleri (d+, d-) hesaplanır.",
        },
        {
            "step": "7",
            "title": "Asimetrik Epistemik Ceza Uygulaması",
            "desc": "Adayın temel skoru (C_base), bilgi kapsama oranına bağlı ceza katsayısı (Gamma_i) ile çarpılarak nihai C* skoru bulunur.",
        },
        {
            "step": "8",
            "title": "Alternatiflerin Sıralanması & Filtreleme",
            "desc": "Asgari bilgi eşiğini (W_threshold) aşamayanlar elenir; geçerli adaylar C* skoruna göre 1..N sıralanır.",
        },
        {
            "step": "9",
            "title": "Profil Bazlı Kontrol & Alarm Denetimi",
            "desc": "İhale modunda kritik maliyet ve yakın skor denetlenir; askeri modda telemetri tazeliği ve karartma durumu incelenir.",
        },
        {
            "step": "10",
            "title": "Kriptografik Bütünlük Makbuzu",
            "desc": "Girdi, konfigürasyon ve çıktının tam hassasiyetli SHA-256 özetleri çıkarılır ve kurumsal imza ile mühürlenir.",
        },
        {
            "step": "11",
            "title": "Yetkili İnsan İncelemesi (Human-in-the-Loop)",
            "desc": "İhale Komisyonu veya Taktik Harekât Subayı sistemin sunduğu gerekçeli tavsiyeyi inceler ve takdir hakkını kullanır.",
        },
        {
            "step": "12",
            "title": "Denetim Kaydı & Çıktı Üretimi",
            "desc": "Olay append-only kalıcı denetim günlüğüne (JSONL) kaydedilir; CSV, tablo ve doğrulanabilir makbuz dışa aktarılır.",
        },
    ]


def get_production_readiness_lists() -> Dict[str, List[str]]:
    """Tamamlanan kurumsal özellikler ile üretim için eksik olanların karşılaştırması."""
    return {
        "completed": [
            "Matematiksel olarak kanıtlanmış ve test edilmiş R-CZ-TOPSIS algoritması",
            "Eksik veri altında uydurma yapmayan alt-uzay mesafe hesaplaması",
            "0_A (ölçülmüş sıfır) ile 0_I (bilinmeyen veri) ayrımı",
            "v1.1 global ağırlıklandırma ile koordinat şişmesi önleme",
            "Hard Gatekeeper eşiği ile yetersiz verili adayları eleme",
            "Kapsamlı fail-closed girdi doğrulama (DecisionDataset.validate)",
            "Kayıpsız IEEE-754 tam hassasiyetli SHA-256 veri mührü",
            "Append-only kalıcı denetim zinciri (PersistentAuditStore)",
            "Kriptografik makbuz imzalama ve doğrulama servisi (ReceiptSigner)",
            "Resmi ihale profili: İki kişili onay sözleşmesi ve yakın skor alarmı",
            "Resmi ihale profili: Kritik maliyet (teklif fiyatı) savunma bayrağı",
            "Askeri profil: Kesin otonom angajman yasağı (kod düzeyinde kilitli)",
            "Askeri profil: Telemetri tazeliği kontrolü ve bayat veri uyarısı",
            "Askeri profil: Jamming ile sensör arızası ayrımı (MissingReason)",
            "Askeri profil: Güvenli duruş (HOLD_NO_ACTIONABLE_TRACKS)",
            "Air-gapped hazır altyapı: Sıfır dış ağ bağımlılığı ve kilitli requirements-frozen.txt",
            "Otomatik testlerle invaryant ve stres doğrulama",
        ],
        "pending_for_production": [
            "Kurumsal Kimlik Yönetimi: Gerçek Active Directory / LDAP / SSO entegrasyonu",
            "Yetkilendirme Altyapısı: Sunucu taraflı merkezi RBAC/ABAC token servisi",
            "Donanımsal Dijital İmza: HSM (Hardware Security Module) veya e-İmza (SmartCard/PKI)",
            "Değiştirilemez Depolama: WORM (Write Once Read Many) kurumsal depolama entegrasyonu",
            "Çok Kullanıcılı Bağımsız Oturum: Fiziksel olarak iki ayrı cihazdan eşzamanlı onay akışı",
            "Kurumsal API Katmanı: REST / gRPC servis katmanı ve güvenli microservice mimarisi",
            "Gerçek C++ CI/CD Derlemesi: rcz_engine.hpp dosyasının GCC/Clang/MSVC ile otomatik derleme testleri",
            "SBOM ve Güvenlik Taraması: Tam yazılım malzeme listesi ve dinamik sızma testleri",
            "Canlı Askeri C2 / Radar Entegrasyonu: Link-16 / ASTERIX radar telemetri akış protokolleri",
            "Hukuki ve Mevzuat Uyumluluğu: KİK/Sayıştay mevzuat incelemesi ve kurum onayı (henüz yok)",
            "Resmi Akreditasyon: Savunma Sanayii Başkanlığı / NATO STANAG resmi sistem sertifikasyonu",
        ],
    }


def get_system_limitations() -> List[Dict[str, str]]:
    """Dürüst ve şeffaf platform sınırlamaları."""
    return [
        {
            "title": "Nihai Karar Verme Yetkisinin Bulunmaması",
            "desc": (
                "Sistem hiçbir koşulda yasal bir ihale kararı veremez veya askeri angajman/ateşleme emri üretemez. "
                "Yalnızca insan karar vericinin (Komisyon Üyeleri veya Taktik Harekât Subayı) sorumluluğundaki "
                "nihai karar sürecine gerekçelendirilmiş teknik destek sağlar."
            ),
        },
        {
            "title": "Maliyet Gizleme Riskinin Matematiksel Sınırı",
            "desc": (
                "Eksik maliyet bilgisi matematiksel olarak temkin cezası ile cezalandırılır ve komisyona resmi savunma "
                "talebi açması tavsiye edilir. Ancak hiçbir matematiksel algoritma, bilerek gizlenen bir maliyetin "
                "arka plandaki gerçek değerini sihirli biçimde tahmin edemez; idari ve hukuki soruşturma zorunludur."
            ),
        },
        {
            "title": "Audit Zincirinin Donanımsal Sınırları",
            "desc": (
                "PersistentAuditStore yazılım düzeyinde kriptografik hash zinciri bütünlüğünü denetler. "
                "Ancak dosyanın bulunduğu diskin fiziksel imhası veya root/admin yetkisiyle diskten tamamen silinmesi "
                "riskine karşı WORM veya harici bağımsız yedekleme altyapısı ile desteklenmelidir."
            ),
        },
        {
            "title": "Dashboard Kimlik Alanlarının Prototip Niteliği",
            "desc": (
                "Arayüzdeki operatör ve komisyon başkanı kimlik alanları mimari akışı göstermek üzere tasarlanmış "
                "prototip girdi alanlarıdır; kurumsal SSO veya biyometrik akıllı kart entegrasyonu yerine geçmez."
            ),
        },
        {
            "title": "Askeri Profilin Operasyonel Sertifikasyon Durumu",
            "desc": (
                "Askeri taktik profil bir araştırma ve kavramsal gösterim (proof-of-concept) katmanıdır. "
                "Operasyonel askeri görev bilgisayarı yazılımı, DO-178C aviyonik sertifikasyonu veya canlı silah "
                "kontrol sistemi değildir."
            ),
        },
        {
            "title": "C++ Conformance Gerçek Derleyici Durumu",
            "desc": (
                "include/rcz_engine.hpp başlık dosyası gömülü sistemler için tasarlanmış bir referans şartnamedir. "
                "Mevcut test paketi (test_conformance.py) matematiksel protokol denklik simülasyonu yapar; "
                "üretim ortamında hedef işlemci için GCC/Clang çapraz derlemesi ve donanım testleri yapılmalıdır."
            ),
        },
        {
            "title": "Veri Setlerinin Sentetik / Gerçek Durumu",
            "desc": (
                "Sistemdeki UCI Automobile ve Elektrikli Araç veri setleri kamuya açık gerçek test bültenlerine dayanırken; "
                "Hava Savunma Radar, İHA ve Tedarikçi setleri kamuya açık parametrelerden modellenmiş sentetik "
                "araştırma benchmarklarıdır (Bkz: data/DATASET_METADATA.json)."
            ),
        },
    ]


def get_faq_items() -> List[Dict[str, str]]:
    """Kullanıcıların en çok merak ettiği temel sorular (Ceza, Hesaplama, Kriter Seçimi) ve kapsamlı yanıtları."""
    return [
        {
            "id": "FAQ-01",
            "category": "⚖️ Ceza Mantığı",
            "question": "Bu sistemde 'Ceza' (Penalty) dediğimiz şey nedir ve neden uygulanır?",
            "short_answer": (
                "Ceza, eksik veya saklanan bilgisi olan adayların nihai skoruna uygulanan bir 'temkin/ihtiyat indirimidir'. "
                "Bir cezalandırma veya intikam mekanizması değil; bilinmeyen verilere karşı karar vericiyi koruyan matematiksel bir güvenlik payıdır."
            ),
            "full_answer": (
                "Çok kriterli karar vermede bir adayın bazı özellikleri bilinmiyorsa, o adaya tam güven duyulamaz.\n\n"
                "**1. Matematiksel Çarpan (Γ_i):** Her adayın önce bilinen kriterler alt-uzayındaki temel puanı ($C_{\\text{base}}$) hesaplanır. "
                "Ardından bu puan Epistemik Güvenilirlik Çarpanı ($\\Gamma_i = W_i^{\\alpha \\cdot \\kappa_i}$) ile çarpılarak nihai skora ($C^* = C_{\\text{base}} \\cdot \\Gamma_i$) dönüştürülür.\n\n"
                "**2. Tam Veri Durumu:** Adayın tüm kriterleri eksiksiz ölçülmüşse bilgi kapsama oranı $W_i = 1.0$ olur ve $\\Gamma_i = 1.0$ (yani %0 ceza) uygulanır.\n\n"
                "**3. Asimetrik Maliyet Cezası ($\\kappa_i$) ve Akerlof Limon Piyasası:** İhale ve alım süreçlerinde adaylar hız, güç, konfor gibi faydaları överken; "
                "fiyat, bakım masrafı, yakıt veya arıza oranı gibi maliyet/risk kriterlerini gizleme eğilimindedir. "
                "Klasik TOPSIS eksik maliyeti 0 TL (bedava) sayarak adayı haksız şampiyon yaparken, R-CZ modeli gizlenen her maliyet kriteri için "
                "ceza üssünü büyütür ($\\kappa_i = 1 + \\text{missing\\_cost}$). Böylece maliyet saklayan adaya üssel ceza kesilerek haksız avantajı bastırılır."
            ),
        },
        {
            "id": "FAQ-02",
            "category": "🎛️ Hesaplama ve Kalibrasyon",
            "question": "Hesaplama neye göre ayarlanıyor? Parametreler (α, Eşikler, Ağırlıklar) nasıl çalışır?",
            "short_answer": (
                "Hesaplama keyfi değildir; karar vericinin kurum politikasına göre ayarlayabildiği 4 temel matematiksel kaldıraçla kontrol edilir: "
                "Riskten kaçınma katsayısı (α), Gatekeeper asgari bilgi barajı (W_threshold), asgari kriter sayısı (m_min) ve global ağırlıklandırma."
            ),
            "full_answer": (
                "Yan menüdeki (sidebar) parametreler hesaplama motorunun davranışını şu şekilde ayarlar:\n\n"
                "**1. Epistemik Riskten Kaçınma Katsayısı ($\\alpha$ - Alpha):**\n"
                "- $\\alpha = 0.0$: Ceza tamamen kapatılır ($\\Gamma = 1.0$). Adaylar yalnızca bildikleri kriterlerle yarışır.\n"
                "- $\\alpha = 0.50$ (Varsayılan): Dengeli akademik ve kurumsal standarttır; eksik verili adayı uyarır ama güçlü yönlerini ezmez.\n"
                "- $\\alpha \\ge 1.0$ (Katı Güvenlik Modu): Askeri veya kritik kamu ihalelerinde kullanılır; bilgi eksikliğine tolerans göstermez.\n\n"
                "**2. Hard Gatekeeper Eşiği ($W_{\\text{threshold}}$ - Asgari Bilgi Barajı):**\n"
                "Bir adayın yarışabilmesi için kriter ağırlıklarının en az yüzde kaçına sahip olması gerektiğini belirler (Varsayılan: %50 / 0.50). "
                "Toplam ağırlığı %50'nin altında kalan veya 2'den az kriteri bilinen adaylar doğrudan elenir (Skor: 0.0, Sıra: -1).\n\n"
                "**3. Global Alt-Uzay Ağırlıklandırması (v1.1 Varsayılanı):**\n"
                "Adayın bildiği kriterler $V_{ij} = w_j \\cdot (X_{ij} / S_j)$ formülüyle normalize edilir. v1.0'daki yerel bölme ($1/W_i$) koordinat şişmesine "
                "yol açabildiği için v1.1'de global ağırlık izdüşümü standart yapılmıştır."
            ),
        },
        {
            "id": "FAQ-03",
            "category": "📊 Kriter Seçimi ve Yönetimi",
            "question": "Alınan kriterler nedir ve kriterler neye göre seçilir?",
            "short_answer": (
                "Kriterler, karar problemini tanımlayan ölçülebilir başarı boyutlarıdır. İki ana kategoriye ayrılır: Fayda (büyük olan iyi) "
                "ve Maliyet (küçük olan iyi). Kriterler ihale teknik şartnamesi, askeri harekât gereksinimleri veya mühendislik hedeflerine göre belirlenir."
            ),
            "full_answer": (
                "Karar matrisindeki sütunlar rastgele değil, belirli karar teorisi ilkelerine göre seçilir:\n\n"
                "**1. Kriter Türleri (Yön):**\n"
                "- **Fayda Kriterleri (Benefit, ↑):** Değeri arttıkça alternatifin üstün olduğu kriterlerdir (Örn: Motor Gücü, Menzil, Batarya Kapasitesi, Güvenlik Puanı, Faydalı Yük Kapasitesi).\n"
                "- **Maliyet / Risk Kriterleri (Cost, ↓):** Değeri azaldıkça alternatifin üstün olduğu kriterlerdir (Örn: Satın Alma Fiyatı, Yıllık Bakım Masrafı, Arıza Oranı, Ağırlık, Radar İzi/RCS, Tepki Süresi).\n\n"
                "**2. Kriterler Neye Göre Seçilir?**\n"
                "- **İhtiyaç Analizi:** Resmi ihale teknik şartnamesi, askeri doktrin veya ürün katalog standartları temel alınır.\n"
                "- **Birbirinden Bağımsızlık (Non-Redundancy):** Kriterlerin aynı özelliği mükerrer ölçmemesi (multicollinearity olmaması) gerekir.\n"
                "- **Ölçülebilirlik:** Doğrudan fiziksel birimlerle (TL, USD, km/saat, kg, m, saat) veya nesnel standart skalayla (1-10) ölçülebilir olmalıdır.\n\n"
                "**3. Kriter Ağırlıkları ($w_j$) Nasıl Belirlenir?**\n"
                "Her kriterin karar için taşıdığı önem ağırlığı analitik yöntemlerle (AHP, Shannon Entropi, uzman paneli oylaması veya şartname yüzdeleri) "
                "belirlenir ve toplamı %100'e ($\\sum w_j = 1.0$) eşitlenir."
            ),
        },
        {
            "id": "FAQ-04",
            "category": "🧩 Eksik Veri Davranışı",
            "question": "Bir adayın kriteri eksik olduğunda sistem ne yapar? Yapay sayı uydurur mu?",
            "short_answer": (
                "Kesinlikle hayır (Imputation-Free). R-CZ sistemi boş hücrelere ortalama veya regresyonla sahte sayı uydurmaz. "
                "Adayı yalnızca bildiği kriterlerin alt-uzayında değerlendirir ve eksiklik için şeffaf bir temkin indirimi uygular."
            ),
            "full_answer": (
                "Klasik istatistik ve yapay zeka yaklaşımları boş hücreleri sütun ortalaması veya k-NN tahmini ile doldurur. "
                "Bu durum ihale ve askeri sistemlerde sahte kesinlik illüzyonu yaratır ve yasal denetimlerde geçersizdir.\n\n"
                "R-CZ'nin Yaklaşımı:\n"
                "1. **Çift-Sıfır Cebiri ($0_A$ vs $0_I$):** Ölçülmüş gerçek sıfır (0 TL ceza veya 0 km hız) ile veri yokluğunu (bilinmeyen fiyat/sensör kararması) birbirinden ayırır.\n"
                "2. **Alt-Uzay İzdüşümü:** Aday yalnızca verisi olan kriterlerin geometrik alt-uzayında ($J_i^*$) Öklid mesafesine tabi tutulur.\n"
                "3. **Epistemik Şeffaflık:** Eksik veri yapay sayıyla maskelenmez; karar vericiye adayın bilgi kapsama oranı (%$W_i$) ve ceza kesintisi açıkça raporlanır."
            ),
        },
        {
            "id": "FAQ-05",
            "category": "🏆 Karar ve Şampiyonluk",
            "question": "Eksik bilgisi olan bir adayın birinci (şampiyon) olması mümkün müdür?",
            "short_answer": (
                "Evet, mümkündür. Bilinen kriterlerdeki üstünlüğü çok yüksekse ve eksik bilgi önemsiz bir kriterdeyse, aday hafif temkin cezasına rağmen zirveyi koruyabilir. "
                "Sistem kaliteli adayı körlemesine infaz etmez; ancak gizlenen bilgi kritik bir maliyetse ceza hızla ağırlaşır."
            ),
            "full_answer": (
                "R-CZ-TOPSIS, iki uç yanlılığı da önleyen dengeli bir modeldir:\n"
                "- **Haksız İnfazı Önler:** 10 kriterden 9'unda rakiplerini ikiye katlayan kaliteli bir aday, 1 önemsiz bilgisi eksik diye elenmez.\n"
                "- **Haksız Şampiyonluğu Bastırır:** Eksik kriter bir maliyet/fiyat ise veya adayın toplam bilgisi yetersizse, asimetrik ceza adayı aşağı çeker.\n"
                "- **Özetle:** Karar vericiye 'Bu aday bilinen yönleriyle güçlüdür, ancak eksik kriteri nedeniyle skoru %X düşürülmüştür' diyerek şeffaf tercih zemini sunar."
            ),
        },
    ]


def render_system_overview_page(st: Any, safe_text: Any) -> None:
    """Streamlit üzerinde 0. Sistem Genel Bakışı / Platform Özellikleri sayfasını çizer."""
    meta = get_system_overview_metadata()

    # 1. ÜST BİLGİ ALANI
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%); color: #ffffff; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.15); box-shadow: 0 4px 14px rgba(0,0,0,0.15);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #ffffff;">🧭 {safe_text(meta['system_name'])}</h2>
                    <div style="font-size: 0.95rem; font-weight: 600; color: #93c5fd; margin-top: 4px;">{safe_text(meta['title'])}</div>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;">Çekirdek: {safe_text(meta['engine_version'])}</span>
                    <span style="background: rgba(255,255,255,0.12); padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 600;">Arayüz: {safe_text(meta['dashboard_version'])}</span>
                    <span style="background: rgba(245, 158, 11, 0.25); border: 1px solid rgba(245, 158, 11, 0.5); color: #fde68a; padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 700;">{safe_text(meta['system_readiness'])}</span>
                </div>
            </div>
            <div style="font-size: 0.88rem; color: #e2e8f0; margin-top: 10px; line-height: 1.5; max-width: 980px;">
                {safe_text(meta['description'])}
            </div>
            <div style="margin-top: 14px; background: rgba(220, 38, 38, 0.22); border-left: 4px solid #ef4444; padding: 10px 14px; border-radius: 4px; font-size: 0.82rem; line-height: 1.45; color: #fee2e2;">
                <strong>⚠️ {safe_text(meta['doctrine_warning'])}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. ÖZET METRİK KARTLARI
    metrics = get_summary_metrics()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label=metrics[0]["label"], value=metrics[0]["value"], delta=metrics[0]["delta"], help=metrics[0]["help"])
    with c2:
        st.metric(label=metrics[1]["label"], value=metrics[1]["value"], delta=metrics[1]["delta"], help=metrics[1]["help"])
    with c3:
        st.metric(label=metrics[2]["label"], value=metrics[2]["value"], delta=metrics[2]["delta"], help=metrics[2]["help"])
    with c4:
        st.metric(label=metrics[3]["label"], value=metrics[3]["value"], delta=metrics[3]["delta"], help=metrics[3]["help"])

    c5, c6, c7 = st.columns(3)
    with c5:
        st.metric(label=metrics[4]["label"], value=metrics[4]["value"], delta=metrics[4]["delta"], help=metrics[4]["help"])
    with c6:
        st.metric(label=metrics[5]["label"], value=metrics[5]["value"], delta=metrics[5]["delta"], help=metrics[5]["help"])
    with c7:
        st.metric(label=metrics[6]["label"], value=metrics[6]["value"], delta=metrics[6]["delta"], help=metrics[6]["help"])

    st.markdown("---")

    # 3. TÜM ÖZELLİKLERİN KATEGORİK ENVANTERİ
    st.subheader("📦 1. Sistem Özellik Envanteri & Modül Yetenekleri (32 Doğrulanmış Özellik)")
    st.caption("Aşağıdaki listede platformda gerçekten kodlanmış, test edilmiş ve mimari olarak tanımlanmış tüm özellikler şeffaf durum etiketleriyle sunulmaktadır.")

    features = get_feature_inventory()
    categories = [
        "Tüm Özellikler (32)",
        "Çekirdek Karar Motoru & Matematik",
        "Veri Sözleşmesi & Bütünlük",
        "Resmi İhale & Tedarik Profili",
        "Askeri Taktik Advisory Profili",
        "Analiz, Simülasyon & Karşılaştırma",
        "Altyapı, Güvenlik & Dağıtım",
    ]

    selected_cat = st.selectbox("Filtrele veya Kategori Seçin:", categories, index=0)

    filtered_features = features if selected_cat == "Tüm Özellikler (32)" else [f for f in features if f.category == selected_cat]

    status_styles = {
        FeatureStatus.AVAILABLE: ("✅ Mevcut", "#ecfdf5", "#065f46", "#a7f3d0"),
        FeatureStatus.PARTIAL: ("⚠️ Kısmen Mevcut", "#fffbeb", "#92400e", "#fde68a"),
        FeatureStatus.DESIGN_ONLY: ("📐 Tasarım Seviyesinde", "#eff6ff", "#1e40af", "#bfdbfe"),
        FeatureStatus.MISSING: ("❌ Üretim İçin Eksik", "#fff1f2", "#9f1239", "#fecdd3"),
    }

    cols = st.columns(2)
    for idx, feat in enumerate(filtered_features):
        col = cols[idx % 2]
        badge_text, bg, fg, border = status_styles.get(feat.status, ("Bilinmiyor", "#f3f4f6", "#374151", "#d1d5db"))
        with col:
            with st.expander(f"{badge_text} | {feat.id}: {feat.name}", expanded=False):
                st.markdown(f"**Kategori:** `{feat.category}` | **Modül/Dosya:** `{feat.module_or_file}`")
                st.markdown(f"**Açıklama:** {safe_text(feat.description)}")
                st.markdown(f"**Kullanıcıya Değeri:** {safe_text(feat.value_to_user)}")
                if feat.limitation:
                    st.warning(f"**Önemli Sınırlama:** {safe_text(feat.limitation)}")

    st.markdown("---")

    # 4. ÜRÜN PROFİLLERİ KARŞILAŞTIRMA TABLOSU
    st.subheader("⚖️ 2. Kurumsal Ürün Profilleri Karşılaştırma Tablosu")
    st.caption("Ortak R-CZ matematik motoru üzerinde koşan 3 farklı ürün profilinin yetki, güvenlik ve veri politikaları:")

    comp_rows = get_profile_comparisons()
    table_html = """
    <div class="rcz-comparison-wrap">
        <table class="rcz-comparison">
            <thead>
                <tr>
                    <th>Kriter / Politika</th>
                    <th>🔬 Bilimsel Araştırma</th>
                    <th>🏛️ Resmi İhale &amp; Tedarik</th>
                    <th>🎯 Askeri Taktik Advisory</th>
                </tr>
            </thead>
            <tbody>
    """
    for r in comp_rows:
        table_html += (
            "<tr>"
            f"<td>{safe_text(r.criterion)}</td>"
            f"<td>{safe_text(r.scientific)}</td>"
            f"<td>{safe_text(r.tender)}</td>"
            f"<td>{safe_text(r.military)}</td>"
            "</tr>"
        )
    table_html += """
            </tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")

    # 5. KULLANIM AKIŞI (12 ADIM)
    st.subheader("🔄 3. Uçtan Uca Karar Destek Süreci (12 Aşamalı Akış)")
    st.caption("Platformda verinin yüklenmesinden doğrulanmış rapor ve denetim makbuzu üretilmesine kadar izlenen aşamalar:")

    steps = get_usage_flow_steps()
    # 4'erli sütunlarda 3 satır
    for row_idx in range(3):
        r_cols = st.columns(4)
        for c_idx in range(4):
            step_num = row_idx * 4 + c_idx
            if step_num < len(steps):
                s = steps[step_num]
                with r_cols[c_idx]:
                    st.markdown(
                        f"""
                        <div class="rcz-card" style="min-height: 140px; height: 100%; padding: 12px; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                                <span style="background: #2563eb; color: #ffffff; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.74rem; font-weight: 700;">{s['step']}</span>
                                <span class="rcz-card-title" style="margin: 0; font-size: 0.82rem;">{safe_text(s['title'])}</span>
                            </div>
                            <div class="rcz-card-body" style="font-size: 0.75rem; line-height: 1.4;">
                                {safe_text(s['desc'])}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.markdown("---")

    # 6. PLATFORM ÇIKTILARI BÖLÜMÜ
    st.subheader("📊 4. Sistemin Ürettiği Çıktılar ve Rapor Paketleri")
    out_col1, out_col2 = st.columns(2)
    with out_col1:
        st.markdown(
            r"""
            #### 📈 Karar ve Sıralama Çıktıları
            * **Nihai Sıralama ($1..N$):** Adayların epistemik güvenilirlik katsayısı uygulanmış nihai öncelik sırası.
            * **Nihai Yakınlık Skoru ($C^*$):** $[0.0, 1.0]$ kapalılık aralığında normalize edilmiş kesin puan.
            * **Temel Alt-Uzay Skoru ($C_{\text{base}}$):** Ceza uygulanmadan önceki ham alt-uzay TOPSIS skoru.
            * **Bilgi Kapsama Oranı ($W_i$):** Adayın bilinen kriter ağırlıkları toplamı ($\sum w_j$).
            * **Epistemik Ceza Katsayısı ($\Gamma_i$):** Eksik bilgi nedeniyle uygulanan temkin çarpanı.
            * **İdeal / Anti-İdeal Mesafeler ($d^+, d^-$):** Alt-uzaydaki Öklid izdüşüm uzaklıkları.
            * **Aday Uygunluk Statüsü:** `ACTIVE` (geçerli) veya `INSUFFICIENT_DATA` (bilgi yetersizliği nedeniyle elendi).
            """
        )
    with out_col2:
        st.markdown(
            r"""
            #### 🛡️ Denetim, Bütünlük ve Alarm Çıktıları
            * **Kayıpsız Veri Mührü (SHA-256):** Girdilerin IEEE-754 tam duyarlıkla çıkarılmış kriptografik özeti.
            * **Kalıcı Denetim Makbuzu (`IntegrityReceipt`):** Zaman damgalı, operatör kimlikli ve mühürlü özet.
            * **Dijital İmza (`SignedReceipt`):** Kurumsal anahtarla imzalanmış HMAC-SHA256 doğrulanabilir mührü.
            * **Kalıcı Olay Günlüğü (`PersistentAuditStore`):** Diskte append-only JSONL formatında hash zinciri.
            * **İhale Savunma Bayrağı:** Teklif fiyatı beyan etmeyen yükleniciler için resmi savunma talebi uyarısı.
            * **Yakın Skor Alarmı:** İlk 2 teklif farkı $\le \%2.0$ olduğunda zorunlu komisyon inceleme uyarısı.
            * **Askeri Güvenli Duruş:** `HOLD_NO_ACTIONABLE_TRACKS` ve bayat telemetri doğrulaması ikazı.
            """
        )

    st.markdown("---")

    # 7. GÜVENLİK VE ÜRETİM HAZIRLIĞI
    st.subheader("🛡️ 5. Güvenlik, Doğrulama ve Üretim Hazırlığı Durumu")
    st.caption("Akademik araştırma prototipi ile gerçek kurumsal üretim dağıtımı arasındaki mevcut ve eksik kontroller:")

    prod = get_production_readiness_lists()
    sec_col1, sec_col2 = st.columns(2)
    with sec_col1:
        st.success("### ✅ Tamamlanmış / Prototipte Bulunanlar (17 Madde)")
        for item in prod["completed"]:
            st.markdown(f"- ✔️ **{safe_text(item)}**")

    with sec_col2:
        st.warning("### 🛠️ Üretim İçin Hâlâ Gerekli Olanlar (11 Madde)")
        for item in prod["pending_for_production"]:
            st.markdown(f"- ⏳ **{safe_text(item)}**")

    st.markdown("---")

    # 8. SINIRLAMALAR VE DÜRÜSTLÜK BÖLÜMÜ
    st.subheader("⚠️ 6. Platform Sınırlamaları ve Bilimsel Dürüstlük İlkeleri")
    st.caption("Sistemin yanlış anlaşılmasını ve yetkisi dışındaki alanlarda kullanılmasını engellemek için belirlenen kesin sınırlar:")

    limits = get_system_limitations()
    for l in limits:
        with st.expander(f"📌 {safe_text(l['title'])}", expanded=True):
            st.write(safe_text(l["desc"]))

    st.markdown("---")

    # 9. SIKÇA SORULAN SORULAR (SSS / FAQ)
    st.subheader("❓ 7. Sıkça Sorulan Sorular: Ceza Mantığı, Parametre Ayarları ve Kriter Seçimi")
    st.caption("Sistemin nasıl çalıştığı, ceza kavramı, hesaplama mekanizması ve kriter belirleme standartları hakkında merak edilenler:")

    faq_items = get_faq_items()
    for item in faq_items:
        with st.expander(f"{item['category']} | {safe_text(item['question'])}", expanded=False):
            st.markdown(
                f"""
                <div class="rcz-card-info" style="padding: 10px 14px; margin-bottom: 12px;">
                    <strong style="color: #1e40af;">Kısa Özet:</strong><br>
                    <span style="font-size: 0.90rem;">{safe_text(item['short_answer'])}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(item["full_answer"])
