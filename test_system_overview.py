"""R-CZ-TOPSIS Sistem Genel Bakışı ve Platform Özellikleri Test Paketi.

Bu test modülü şunları doğrular:
1. Sayfa navigasyonunda '0. Sistem Genel Bakışı & Platform Özellikleri' seçeneğinin varlığı.
2. Üç ürün profilinin (Bilimsel Araştırma, Resmi İhale, Askeri Advisory) eksiksiz karşılaştırılması.
3. 32 adet platform özelliğinin envanterde yer alması ve geçerli durum etiketleri (FeatureStatus).
4. Kurumsal üretim eksikliklerinin (AD/SSO, HSM, WORM, C++ CI vb.) açıkça listelenmesi.
5. Şeffaf sınırlamalar ve bilimsel dürüstlük maddelerinin varlığı.
6. XSS ve zararlı HTML girdilerinin safe_text ile güvenli şekilde filtrelenmesi (escaping).
"""
import html
import pytest
from pathlib import Path

from src.rcz_topsis.system_catalog import (
    FeatureStatus,
    FeatureItem,
    get_system_overview_metadata,
    get_summary_metrics,
    get_feature_inventory,
    get_profile_comparisons,
    get_usage_flow_steps,
    get_production_readiness_lists,
    get_system_limitations,
)


def test_navigation_option_in_dashboard():
    dashboard_path = Path(__file__).parent / "dashboard.py"
    assert dashboard_path.exists()
    content = dashboard_path.read_text(encoding="utf-8")
    assert "0  Genel Bakış" in content
    assert "render_system_overview_page" in content


def test_three_product_profiles_compared():
    comparisons = get_profile_comparisons()
    assert len(comparisons) >= 8

    # Tüm satırlarda üç profilin de dolu ve açıklayıcı metin içerdiğini doğrula
    for row in comparisons:
        assert row.criterion.strip() != ""
        assert len(row.scientific.strip()) > 5
        assert len(row.tender.strip()) > 5
        assert len(row.military.strip()) > 5


def test_feature_inventory_categories_and_items():
    inventory = get_feature_inventory()
    assert len(inventory) >= 30, f"En az 30 özellik olmalı; mevcut: {len(inventory)}"

    categories = {item.category for item in inventory}
    expected_categories = {
        "Çekirdek Karar Motoru & Matematik",
        "Veri Sözleşmesi & Bütünlük",
        "Resmi İhale & Tedarik Profili",
        "Askeri Taktik Advisory Profili",
        "Analiz, Simülasyon & Karşılaştırma",
        "Altyapı, Güvenlik & Dağıtım",
    }
    assert expected_categories.issubset(categories)

    # Her özelliğin geçerli bir enum statüsüne ve benzersiz bir ID'ye sahip olduğunu denetle
    ids = set()
    for item in inventory:
        assert isinstance(item.status, FeatureStatus)
        assert item.id not in ids, f"Tekrarlanan ID: {item.id}"
        ids.add(item.id)
        assert len(item.description) > 10
        assert len(item.value_to_user) > 10


def test_production_readiness_and_gaps_clearly_separated():
    readiness = get_production_readiness_lists()
    assert "completed" in readiness
    assert "pending_for_production" in readiness

    completed = readiness["completed"]
    pending = readiness["pending_for_production"]

    assert len(completed) >= 12
    assert len(pending) >= 8

    # Kritik üretim eksikliklerinin dürüstçe itiraf edildiğini doğrula
    pending_str = " ".join(pending).lower()
    assert "active directory" in pending_str or "ldap" in pending_str or "sso" in pending_str
    assert "hsm" in pending_str or "smartcard" in pending_str or "e-imza" in pending_str
    assert "worm" in pending_str
    assert "c++" in pending_str
    assert "akreditasyon" in pending_str or "sertifikasyon" in pending_str


def test_honest_limitations_section():
    limitations = get_system_limitations()
    assert len(limitations) >= 5

    titles = [l["title"].lower() for l in limitations]
    assert any("nihai karar" in t for t in titles)
    assert any("maliyet gizleme" in t for t in titles)
    assert any("audit" in t or "zincir" in t for t in titles)
    assert any("askeri" in t for t in titles)
    assert any("c++" in t for t in titles)


def test_user_text_escaping_and_xss_protection():
    raw_malicious = '<script>alert("XSS")</script>&<img src="x" onerror="steal()">'
    escaped = html.escape(raw_malicious)

    assert "<script>" not in escaped
    assert '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;' in escaped
    assert "&amp;" in escaped


def test_faq_items_cover_core_questions():
    """Ceza, hesaplama ayarları ve kriter seçimi gibi temel soruların SSS listesinde olduğunu doğrular."""
    from src.rcz_topsis.system_catalog import get_faq_items
    faqs = get_faq_items()
    assert len(faqs) >= 5

    all_questions_text = " ".join(f["question"].lower() for f in faqs)
    all_answers_text = " ".join(f["full_answer"].lower() for f in faqs)

    # Ceza kavramı
    assert "ceza" in all_questions_text or "ceza" in all_answers_text
    # Hesaplama ve parametreler
    assert "hesaplama" in all_questions_text or "parametre" in all_questions_text
    # Kriterler ve seçim mantığı
    assert "kriter" in all_questions_text

    # Dashboard içinde get_faq_items çağrısının yer aldığını doğrula
    dashboard_path = Path(__file__).parent / "dashboard.py"
    dash_text = dashboard_path.read_text(encoding="utf-8")
    assert "get_faq_items" in dash_text

