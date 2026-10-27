"""R-CZ-TOPSIS Sistem Sözlüğü ve Kavramlar Rehberi Testleri.

Kullanıcının talep ettiği 4 temel kavramın (Hard Gatekeeper, Transponder,
Epistemik Ceza, Akerlof Limon Piyasası) ve taranan tüm 18 kavramın
doğruluğunu, alanlarını ve filtreleme işlevselliğini test eder.
"""
import pytest
from src.rcz_topsis.glossary import get_glossary_terms


def test_glossary_term_count_and_keys():
    """Tüm terimlerin eksiksiz yüklendiğini ve zorunlu alanlara sahip olduğunu doğrular."""
    terms = get_glossary_terms()
    assert len(terms) >= 18, f"En az 18 terim olmalı, bulunan: {len(terms)}"

    required_keys = {"id", "term", "category", "icon", "short_def", "detailed_def"}
    for t in terms:
        assert required_keys.issubset(t.keys()), f"Eksik anahtar: {required_keys - set(t.keys())} in {t}"
        assert len(t["term"].strip()) > 0
        assert len(t["short_def"].strip()) > 0
        assert len(t["detailed_def"].strip()) > 0


def test_core_four_requested_terms():
    """Kullanıcının özellikle sorduğu 4 kritik kavramın varlığını ve içerik doğruluğunu test eder."""
    terms = get_glossary_terms()
    term_ids = {t["id"]: t for t in terms}

    # 1. Hard Gatekeeper
    assert "TERM-GATEKEEPER" in term_ids
    gk = term_ids["TERM-GATEKEEPER"]
    assert "gatekeeper" in gk["term"].lower() or "baraj" in gk["term"].lower()
    assert "%50" in gk["short_def"] or "w_threshold" in gk["detailed_def"].lower()
    assert "formula" in gk

    # 2. Transponder
    assert "TERM-TRANSPONDER" in term_ids
    tp = term_ids["TERM-TRANSPONDER"]
    assert "transponder" in tp["term"].lower()
    assert "iff" in tp["term"].lower() or "dost" in tp["short_def"].lower()

    # 3. Epistemik Ceza
    assert "TERM-EPISTEMIC-PENALTY" in term_ids
    ep = term_ids["TERM-EPISTEMIC-PENALTY"]
    assert "epistemik" in ep["term"].lower() or "ceza" in ep["term"].lower()
    assert "Γ" in ep["term"] or "gamma" in ep["detailed_def"].lower()

    # 4. Akerlof Limon Piyasası
    assert "TERM-AKERLOF" in term_ids
    ak = term_ids["TERM-AKERLOF"]
    assert "akerlof" in ak["term"].lower() or "limon" in ak["term"].lower()
    assert "maliyet" in ak["detailed_def"].lower() or "sakla" in ak["detailed_def"].lower()


def test_glossary_categories():
    """Tüm terimlerin geçerli kategorilere ayrıldığını test eder."""
    terms = get_glossary_terms()
    valid_categories = {
        "🛡️ Güvenlik & Kural",
        "🎯 Askeri & Radar",
        "📐 Matematik & Model",
        "🏛️ İhale & Teori",
    }
    for t in terms:
        assert t["category"] in valid_categories, f"Geçersiz kategori: {t['category']} in {t['term']}"


def test_glossary_search_filtering():
    """Arama sorgularının doğru terimleri filtrelediğini test eder."""
    terms = get_glossary_terms()

    # 'gatekeeper' araması
    gk_results = [t for t in terms if "gatekeeper" in t["term"].lower() or "gatekeeper" in t["short_def"].lower()]
    assert len(gk_results) >= 1
    assert gk_results[0]["id"] == "TERM-GATEKEEPER"

    # 'transponder' araması
    tp_results = [t for t in terms if "transponder" in t["term"].lower()]
    assert len(tp_results) >= 1
    assert tp_results[0]["id"] == "TERM-TRANSPONDER"

    # 'limon' araması
    lm_results = [t for t in terms if "limon" in t["term"].lower() or "lemon" in t["term"].lower()]
    assert len(lm_results) >= 1
    assert lm_results[0]["id"] == "TERM-AKERLOF"

