"""R-CZ-TOPSIS Özelleştirilmiş Ürün Profilleri.

- tender: Resmi İhale ve Tedarikçi Seçimi Profili (İki Kişili Onay & Teftiş)
- military_advisory: Askeri Taktik Karar Destek Profili (İnsan Onaylı, Angajman Dışı Danışman)
"""
from .tender import TenderProfile, TenderEvaluationResult
from .military_advisory import MilitaryAdvisoryProfile, MilitaryAdvisoryResult

__all__ = [
    "TenderProfile",
    "TenderEvaluationResult",
    "MilitaryAdvisoryProfile",
    "MilitaryAdvisoryResult",
]

