"""R-CZ-TOPSIS Yüksek Güvenceli Ürün Profilleri & Denetim Test Paketi.

Doğrulanan Özellikler:
1. Şema ve Bütünlük: SHA-256 veri özeti ve mühür üretimi.
2. Denetim Zinciri (Hash Chain): Değiştirilemezlik ve zincir tahrifatı (tamper) yakalama.
3. İhale Profili: İki kişili onay kuralı, eksik maliyet inceleme bayrağı, yakın skor alarmı.
4. Askeri Profil: Kesin otonom müdahale yasağı, bayat telemetri uyarısı, fail-closed güvenli duruş.
"""
import copy
import pytest
import numpy as np

from src.rcz_topsis.types import CritType, Context, RCZConfig
from src.rcz_topsis.schema import (
    CriterionDef,
    AlternativeDef,
    DecisionDataset,
    ProfileType,
)
from src.rcz_topsis.audit import AuditHashChain, GENESIS_HASH
from src.rcz_topsis.profiles.tender import (
    TenderCommissionAuth,
    TenderProfile,
)
from src.rcz_topsis.profiles.military_advisory import (
    MilitaryAdvisoryProfile,
    AUTONOMOUS_ENGAGEMENT_ALLOWED,
)


@pytest.fixture
def sample_dataset():
    crits = [
        CriterionDef(name="Fiyat (TL)", crit_type=CritType.COST, weight=0.4, is_critical_cost=True),
        CriterionDef(name="Kalite Skoru", crit_type=CritType.BENEFIT, weight=0.3),
        CriterionDef(name="Teslim Süresi (Gün)", crit_type=CritType.COST, weight=0.3),
    ]
    alts = [
        AlternativeDef(id="ALT-1", name="Firma A (Eksiksiz)", provider="Teklif Veren A", telemetry_age_seconds=2.0),
        AlternativeDef(id="ALT-2", name="Firma B (Fiyat Gizledi)", provider="Teklif Veren B", telemetry_age_seconds=20.0),
        AlternativeDef(id="ALT-3", name="Firma C (Yetersiz Bilgi)", provider="Teklif Veren C", telemetry_age_seconds=5.0),
    ]
    X = np.array([
        [100.0, 90.0, 30.0],
        [0.0,   95.0, 25.0],    # Fiyat yok (0_I)
        [0.0,   0.0,  20.0],    # 2 kriter yok (0_I)
    ])
    Sigma = np.array([
        ["A", "A", "A"],
        ["I", "A", "A"],
        ["I", "I", "A"],
    ], dtype=object)

    return DecisionDataset(criteria=crits, alternatives=alts, X=X, Sigma=Sigma)


# -----------------------------------------------------------------------------
# 1. Denetim Zinciri & Bütünlük Testleri
# -----------------------------------------------------------------------------
def test_audit_hash_chain_integrity():
    chain = AuditHashChain()
    r1 = chain.record_event("TEST_EVENT_1", "OPERATOR_A", "TENDER", {"step": 1})
    r2 = chain.record_event("TEST_EVENT_2", "OPERATOR_A", "TENDER", {"step": 2})
    r3 = chain.record_event("TEST_EVENT_3", "OPERATOR_B", "TENDER", {"step": 3})

    assert len(chain.records) == 3
    assert chain.verify_integrity() is True
    assert r1.prev_hash == GENESIS_HASH
    assert r2.prev_hash == r1.record_hash
    assert r3.prev_hash == r2.record_hash


def test_hashes_preserve_distinct_binary64_values(sample_dataset):
    """Bütünlük özeti, 15 basamakta çakışan farklı float64 değerlerini ayırmalıdır."""
    first = copy.deepcopy(sample_dataset)
    second = copy.deepcopy(sample_dataset)
    first.X[0, 0] = 1.0000000000000002
    second.X[0, 0] = 1.0000000000000004

    assert first.compute_sha256() != second.compute_sha256()

    from src.rcz_topsis.schema import hash_config
    assert hash_config(RCZConfig(alpha=1.0000000000000002)) != hash_config(
        RCZConfig(alpha=1.0000000000000004)
    )


def test_audit_hash_chain_tamper_detection():
    chain = AuditHashChain()
    chain.record_event("E1", "USER", "PROFILE", {"val": 100})
    chain.record_event("E2", "USER", "PROFILE", {"val": 200})

    assert chain.verify_integrity() is True

    # Kayıt içine gizlice sahte veri enjekte edildiğinde bütünlük bozulmalı
    tampered_records = copy.deepcopy(chain.records)
    tampered_records[0] = copy.deepcopy(tampered_records[0])
    tampered_records[0].details["val"] = 999999  # Tahrifat

    tampered_chain = AuditHashChain(initial_records=tampered_records)
    assert tampered_chain.verify_integrity() is False


# -----------------------------------------------------------------------------
# 2. Resmi İhale Profili Testleri
# -----------------------------------------------------------------------------
def test_tender_dual_authorization_enforcement(sample_dataset):
    profile = TenderProfile()

    # Aynı kişi iki rolü üstlenemez
    with pytest.raises(ValueError, match="farklı kişiler olmalıdır"):
        invalid_auth = TenderCommissionAuth(
            tender_id="IHAL-2026/01",
            commission_chair_id="AHMET_YILMAZ",
            auditor_id="AHMET_YILMAZ",  # Aynı kişi
            approval_timestamp_utc="2026-10-14T00:00:00Z",
        )
        profile.evaluate(sample_dataset, invalid_auth)


def test_tender_cost_hiding_inquiry_flag(sample_dataset):
    profile = TenderProfile()
    valid_auth = TenderCommissionAuth(
        tender_id="IHAL-2026/01",
        commission_chair_id="BASKAN_01",
        auditor_id="DENETCI_02",
        approval_timestamp_utc="2026-10-14T00:00:00Z",
    )
    result = profile.evaluate(sample_dataset, valid_auth)

    # İhale profili eksik maliyet için inceleme istemelidir
    assert result.requires_commission_inquiry is True
    
    # Firma B fiyat gizlediği için bayraklanmalı
    b_report = next(r for r in result.candidate_reports if r.candidate_id == "ALT-2")
    assert b_report.has_cost_hiding_risk is True
    assert "Fiyat (TL)" in b_report.missing_cost_criteria
    assert b_report.compliance_status == "KOMISYON_SAVUNMA_TALEBI_GEREKLI"

    # Firma C elenmeli
    c_report = next(r for r in result.candidate_reports if r.candidate_id == "ALT-3")
    assert c_report.compliance_status == "ELENDI_BILGI_YETERSIZ"


# -----------------------------------------------------------------------------
# 3. Askeri Taktik Karar Destek Profili Testleri
# -----------------------------------------------------------------------------
def test_military_strict_non_autonomous_invariant():
    assert AUTONOMOUS_ENGAGEMENT_ALLOWED is False


def test_military_advisory_telemetry_staleness_and_hold(sample_dataset):
    profile = MilitaryAdvisoryProfile()
    result = profile.evaluate(
        dataset=sample_dataset,
        operator_id="TACTICAL_OFFICER_01",
        mission_id="TASK-AIR-SHIELD",
        max_freshness_seconds=10.0,
    )

    assert result.operator_id == "TACTICAL_OFFICER_01"
    assert result.stale_telemetry_detected is True
    assert result.active_jamming_detected is True

    # ALT-2 telemetri yaşı 20 sn > 10 sn olduğundan bayat işaretlenmeli
    track_b = next(t for t in result.track_advisories if t.track_id == "ALT-2")
    assert "BAYAT_TELEMETRI" in track_b.freshness_status
    assert track_b.requires_visual_confirmation is True

    # ALT-3 veri yetersiz olduğundan fail-closed beklemeye alınmalı
    track_c = next(t for t in result.track_advisories if t.track_id == "ALT-3")
    assert track_c.fail_closed_hold is True
    assert "BILGI_YETERSIZ_KARARTMA" in track_c.freshness_status


# -----------------------------------------------------------------------------
# 4. Kalıcı Denetim (PersistentAuditStore) ve Kriptografik İmza Testleri
# -----------------------------------------------------------------------------
def test_persistent_audit_store_lifecycle(tmp_path):
    from src.rcz_topsis.audit import PersistentAuditStore
    log_file = tmp_path / "test_audit.jsonl"

    store1 = PersistentAuditStore(log_file)
    store1.record_event("EVT_A", "USER_1", "PROFILE_X", {"code": 101})
    store1.record_event("EVT_B", "USER_2", "PROFILE_X", {"code": 102})
    assert store1.verify_disk_integrity() is True
    assert len(store1.records) == 2

    # İkinci bir store nesnesi dosyayı baştan okuyup zinciri doğrulamalı
    store2 = PersistentAuditStore(log_file)
    assert len(store2.records) == 2
    assert store2.latest_hash == store1.latest_hash
    assert store2.verify_disk_integrity() is True

    # Dosyaya tahrifat yapıldığında bütünlük bozulmalı
    content = log_file.read_text(encoding="utf-8")
    tampered_content = content.replace("101", "999")
    log_file.write_text(tampered_content, encoding="utf-8")

    with pytest.raises(ValueError, match="bütünlük ihlali"):
        PersistentAuditStore(log_file)


def test_receipt_signer_and_verification(sample_dataset):
    from src.rcz_topsis.security.signer import ReceiptSigner
    from src.rcz_topsis.profiles.tender import TenderCommissionAuth, TenderProfile

    profile = TenderProfile()
    auth = TenderCommissionAuth(
        tender_id="IHAL-SEAL-01",
        commission_chair_id="BASKAN_01",
        auditor_id="DENETCI_01",
        approval_timestamp_utc="2026-10-14T00:00:00Z",
    )
    res = profile.evaluate(sample_dataset, auth)
    receipt = res.audit_receipt

    signer = ReceiptSigner(key_id="TEST-KURUM-KEY")
    signed_receipt = signer.sign(receipt)

    assert signed_receipt.key_id == "TEST-KURUM-KEY"
    assert signer.verify(signed_receipt) is True

    # Sahte anahtar veya değiştirilmiş makbuz reddedilmeli
    other_signer = ReceiptSigner(key_id="OTHER-KEY")
    assert other_signer.verify(signed_receipt) is False


# -----------------------------------------------------------------------------
# 5. RBAC Oturum & İki Kişili Onay Testleri
# -----------------------------------------------------------------------------
def test_rbac_authentication_and_permissions():
    from src.rcz_topsis.security.auth import (
        AuthenticationManager,
        Role,
        Permission,
        TwoPersonAuthorization,
    )

    auth_mgr = AuthenticationManager()

    chair_session = auth_mgr.authenticate("baskan_01")
    auditor_session = auth_mgr.authenticate("denetci_01")
    analyst_session = auth_mgr.authenticate("analist_01")

    assert chair_session.role == Role.COMMISSION_CHAIR
    assert chair_session.has_permission(Permission.RUN_TENDER_EVALUATION) is True
    assert chair_session.has_permission(Permission.RUN_TACTICAL_ADVISORY) is False

    assert analyst_session.has_permission(Permission.RUN_GENERIC_EVALUATION) is True
    assert analyst_session.has_permission(Permission.RUN_TENDER_EVALUATION) is False

    # İki kişili onay paketi üretimi
    dual_auth = TwoPersonAuthorization.create(
        auth_mgr=auth_mgr,
        tender_id="TENDER-RBAC-01",
        chair_session=chair_session,
        auditor_session=auditor_session,
    )
    assert dual_auth.authorization_token is not None
    assert dual_auth.chair_session.user_id == "baskan_01"


# -----------------------------------------------------------------------------
# 6. Kritik vs İkincil Maliyet ve Fail-Closed Semantikleri
# -----------------------------------------------------------------------------
def test_tender_critical_vs_secondary_cost():
    crits = [
        CriterionDef(name="Teklif Fiyatı (Ana)", crit_type=CritType.COST, weight=0.5, is_critical_cost=True),
        CriterionDef(name="Bakım Ücreti (İkincil)", crit_type=CritType.COST, weight=0.2, is_critical_cost=False),
        CriterionDef(name="Teknik Puan", crit_type=CritType.BENEFIT, weight=0.3),
    ]
    alts = [
        AlternativeDef(id="A1", name="Firma 1 (Tam)"),
        AlternativeDef(id="A2", name="Firma 2 (Yalnızca İkincil Eksik)"),
        AlternativeDef(id="A3", name="Firma 3 (Kritik Fiyat Eksik)"),
    ]
    X = np.array([
        [100.0, 20.0, 90.0],
        [105.0, 0.0,  95.0],
        [0.0,   18.0, 92.0],
    ])
    Sigma = np.array([
        ["A", "A", "A"],
        ["A", "I", "A"],  # İkincil maliyet eksik
        ["I", "A", "A"],  # Kritik maliyet eksik
    ], dtype=object)

    ds = DecisionDataset(criteria=crits, alternatives=alts, X=X, Sigma=Sigma)
    profile = TenderProfile()
    auth = TenderCommissionAuth(
        tender_id="TENDER-CRIT-01",
        commission_chair_id="BASKAN_01",
        auditor_id="DENETCI_01",
        approval_timestamp_utc="2026-10-14T00:00:00Z",
    )
    res = profile.evaluate(ds, auth)

    rep_a2 = next(r for r in res.candidate_reports if r.candidate_id == "A2")
    rep_a3 = next(r for r in res.candidate_reports if r.candidate_id == "A3")

    # A2 ikincil eksik olduğu için yalnızca ikaz almalı, savunma zorunluluğu bayrağı açmamalı
    assert rep_a2.compliance_status == "IKINCIL_MALIYET_EKSIK_IKAZ"
    assert rep_a2.has_cost_hiding_risk is False

    # A3 kritik maliyet eksik olduğu için resmi savunma talebi istemeli
    assert rep_a3.compliance_status == "KOMISYON_SAVUNMA_TALEBI_GEREKLI"
    assert rep_a3.has_cost_hiding_risk is True


def test_military_fail_closed_hold_when_all_tracks_stale_or_insufficient():
    crits = [
        CriterionDef(name="Tehdit Seviyesi", crit_type=CritType.BENEFIT, weight=0.6),
        CriterionDef(name="Hız", crit_type=CritType.BENEFIT, weight=0.4),
    ]
    alts = [
        AlternativeDef(id="T1", name="Hedef 1 (Kritik Bayat)", telemetry_age_seconds=40.0),
        AlternativeDef(id="T2", name="Hedef 2 (Veri Yetersiz)", telemetry_age_seconds=5.0),
    ]
    X = np.array([
        [80.0, 500.0],
        [0.0,  0.0],
    ])
    Sigma = np.array([
        ["A", "A"],
        ["I", "I"],
    ], dtype=object)

    ds = DecisionDataset(criteria=crits, alternatives=alts, X=X, Sigma=Sigma)
    profile = MilitaryAdvisoryProfile()

    # max_freshness = 10.0 sn -> kritik sınır 20.0 sn. T1 yaşı 40 sn olduğu için dondurulmalı.
    res = profile.evaluate(ds, operator_id="TAC_OFFICER", max_freshness_seconds=10.0)

    assert res.operational_status == "HOLD_NO_ACTIONABLE_TRACKS"
    assert res.top_priority_track is None


def test_military_jamming_reason_discrimination():
    from src.rcz_topsis.schema import MissingReason

    crits = [
        CriterionDef(name="Optik", crit_type=CritType.BENEFIT, weight=0.5),
        CriterionDef(name="Radar", crit_type=CritType.BENEFIT, weight=0.5),
    ]
    alts = [
        AlternativeDef(id="T1", name="Hedef 1"),
        AlternativeDef(id="T2", name="Hedef 2 (Referans)"),
    ]
    X = np.array([
        [90.0, 0.0],
        [80.0, 75.0],
    ])
    Sigma = np.array([
        ["A", "I"],
        ["A", "A"],
    ], dtype=object)

    # 1. Kök neden SENSOR_FAULT olduğunda jamming_detected False olmalı
    ds_fault = DecisionDataset(
        criteria=crits,
        alternatives=alts,
        X=X,
        Sigma=Sigma,
        missing_reasons={(0, 1): MissingReason.SENSOR_FAULT},
    )
    profile = MilitaryAdvisoryProfile()
    res1 = profile.evaluate(ds_fault, operator_id="TAC_OFFICER")
    assert res1.active_jamming_detected is False

    # 2. Kök neden JAMMING_SUSPECTED olduğunda jamming_detected True olmalı
    ds_jam = DecisionDataset(
        criteria=crits,
        alternatives=alts,
        X=X,
        Sigma=Sigma,
        missing_reasons={(0, 1): MissingReason.JAMMING_SUSPECTED},
    )
    res2 = profile.evaluate(ds_jam, operator_id="TAC_OFFICER")
    assert res2.active_jamming_detected is True


# -----------------------------------------------------------------------------
# 7. DecisionService Bütünsel Uçtan Uca Testi
# -----------------------------------------------------------------------------
def test_decision_service_end_to_end(sample_dataset, tmp_path):
    from src.rcz_topsis.service import DecisionService

    audit_path = tmp_path / "service_audit.jsonl"
    service = DecisionService(audit_log_path=audit_path)

    # Oturum açma
    chair_sess = service.authenticate("baskan_01")
    auditor_sess = service.authenticate("denetci_01")
    subay_sess = service.authenticate("subay_01")

    # İki kişili onay ve ihale çalıştırma
    dual_auth = service.create_dual_authorization("IHAL-SERV-01", chair_sess, auditor_sess)
    t_res, t_signed = service.evaluate_tender(chair_sess, sample_dataset, dual_auth)
    assert service.verify_signed_receipt(t_signed) is True

    # Askeri danışmanlık çalıştırma
    m_res, m_signed = service.evaluate_military_advisory(subay_sess, sample_dataset)
    assert service.verify_signed_receipt(m_signed) is True

    # Disk denetim bütünlüğü doğrulama
    assert service.verify_audit_integrity() is True

