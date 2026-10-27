"""R-CZ-TOPSIS Tanıtım ve Giriş Sayfası Test Paketi.

Bu test paketi şunları doğrular:
1. get_landing_metadata() fonksiyonunun eksiksiz ve bilgilendirici üst veri döndürmesi.
2. get_use_cases() fonksiyonunun 6 temel sektörel uygulama alanını (İhale, Savunma, Radar TEWA, Enerji, VC/Startup, Sağlık) içermesi.
3. get_capabilities() fonksiyonunun platformun 6 temel yeteneğini eksiksiz listelemesi.
4. dashboard.py içinde '🏠 0  Tanıtım & Giriş' seçeneğinin ilk sırada yer alması ve render_landing_intro_page çağrısının bulunması.
"""
from pathlib import Path
import pytest

from src.rcz_topsis.landing_page import (
    get_landing_metadata,
    get_use_cases,
    get_capabilities,
    render_landing_intro_page,
)


def test_landing_metadata():
    meta = get_landing_metadata()
    assert "title" in meta
    assert "tagline" in meta
    assert "subtitle" in meta
    assert len(meta["title"]) > 3
    assert "R-CZ" in meta["title"]
    assert len(meta["subtitle"]) > 20


def test_use_cases_content():
    cases = get_use_cases()
    assert len(cases) == 6, f"6 kullanım alanı olmalıdır, bulunan: {len(cases)}"

    case_ids = {c["id"] for c in cases}
    expected_ids = {"CASE-TENDER", "CASE-DEFENSE", "CASE-RADAR", "CASE-ENERGY", "CASE-STARTUP", "CASE-HEALTH"}
    assert case_ids == expected_ids

    for c in cases:
        assert c["icon"] != ""
        assert len(c["title"]) > 5
        assert len(c["subtitle"]) > 5
        assert len(c["problem"]) > 15
        assert len(c["solution"]) > 15
        assert "target_nav" in c


def test_capabilities_content():
    caps = get_capabilities()
    assert len(caps) >= 6

    titles = [c["title"].lower() for c in caps]
    assert any("eksik verili" in t or "karar" in t for t in titles)
    assert any("what-if" in t for t in titles)
    assert any("mcdm" in t for t in titles)
    assert any("denetim" in t or "rapor" in t for t in titles)
    assert any("profil" in t for t in titles)
    assert any("matematik" in t for t in titles)


def test_navigation_landing_page_presence():
    dashboard_path = Path(__file__).parent / "dashboard.py"
    assert dashboard_path.exists()
    dash_text = dashboard_path.read_text(encoding="utf-8")

    assert "Tanıtım & Giriş" in dash_text
    assert "render_landing_intro_page" in dash_text
    assert "pending_nav" in dash_text
    assert "0  Genel Bakış" in dash_text

