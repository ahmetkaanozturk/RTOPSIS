"""Resmi açık veri kaynakları için kontrollü doğrulama hattı adaptörleri.

Bu modül ham veriyi karar matrisi gibi göstermeden önce kaynak, lisans, sürüm,
eksiklik semantiği ve SHA-256 kaydını zorunlu kılar. Canlı veri indirme isteğe
bağlıdır; varsayılan akış yalnızca yerel, kullanıcı tarafından indirilen dosyayı
okur.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ExternalSourceSpec:
    source_id: str
    title: str
    publisher: str
    source_url: str
    license: str
    domain: str
    raw_format: str
    missingness_note: str
    outcome_note: str


@dataclass(frozen=True)
class ProvenanceRecord:
    source_id: str
    local_path: str
    source_url: str
    publisher: str
    license: str
    accessed_at_utc: str
    sha256: str
    row_count: int
    column_count: int
    missing_cells: int
    missingness_observed_or_injected: str
    outcome_definition: str


SOURCE_SPECS: Dict[str, ExternalSourceSpec] = {
    "ted_open_data": ExternalSourceSpec(
        "ted_open_data",
        "TED Open Data / EU Public Procurement",
        "Publications Office of the European Union",
        "https://data.ted.europa.eu/",
        "EU open data terms; verify notice-level reuse conditions",
        "public_procurement",
        "CSV/JSON/RDF export",
        "Notice fields may be absent because of procedure, form, country, or reporting differences; do not label all missingness MNAR.",
        "Award/contract outcome is available only for records with an award or settled-contract notice.",
    ),
    "world_bank_gppd": ExternalSourceSpec(
        "world_bank_gppd",
        "Global Public Procurement Database",
        "World Bank",
        "https://datacatalog.worldbank.org/search/dataset/0038958/global-public-procurement-database",
        "World Bank dataset terms; verify current catalog license",
        "public_procurement_systems",
        "CSV/JSON export",
        "Aggregated indicators may be unavailable by country/year; missingness is not automatically MNAR.",
        "System-level performance indicators are not supplier-level award outcomes.",
    ),
    "nasa_phm": ExternalSourceSpec(
        "nasa_phm",
        "Prognostics Center of Excellence Data Repository",
        "NASA",
        "https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/",
        "Dataset-specific NASA reuse terms",
        "engineering_prognostics",
        "CSV/TXT/Matlab release",
        "Many releases are complete; naturally missing sensor readings must be documented, while injected masks must be labeled injected.",
        "Failure/RUL labels depend on the selected NASA dataset and must not be inferred from sensor values.",
    ),
    "nrel_ev_fleet": ExternalSourceSpec(
        "nrel_ev_fleet",
        "Modeled Electricity Demand Profiles for Public EV Fleets",
        "National Renewable Energy Laboratory / U.S. Department of Energy",
        "https://data.openei.org/submissions/8311",
        "Dataset-specific NREL/OEDI terms",
        "public_ev_fleets",
        "CSV/JSON download",
        "Aggregated/modelled profiles can have structural gaps; do not treat aggregation gaps as sensor failure.",
        "Fleet demand is an operational outcome, not necessarily a historical procurement decision label.",
    ),
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_source(source_id: str, destination: Path, url: Optional[str] = None) -> Path:
    """Download a source file explicitly requested by the caller."""
    if source_id not in SOURCE_SPECS:
        raise KeyError(f"Unknown external source: {source_id}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url or SOURCE_SPECS[source_id].source_url, headers={"User-Agent": "R-CZ-TOPSIS-research/1.0"})
    with urlopen(request, timeout=60) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
    return destination


def build_provenance(
    source_id: str,
    local_path: Path,
    *,
    missingness_observed_or_injected: str,
    outcome_definition: str,
    acquisition_url: Optional[str] = None,
) -> ProvenanceRecord:
    if source_id not in SOURCE_SPECS:
        raise KeyError(f"Unknown external source: {source_id}")
    if missingness_observed_or_injected not in {"observed", "injected", "mixed", "unknown"}:
        raise ValueError("missingness_observed_or_injected must be observed, injected, mixed, or unknown")
    frame = pd.read_csv(local_path)
    spec = SOURCE_SPECS[source_id]
    return ProvenanceRecord(
        source_id=source_id,
        local_path=str(local_path),
        source_url=acquisition_url or spec.source_url,
        publisher=spec.publisher,
        license=spec.license,
        accessed_at_utc=datetime.now(timezone.utc).isoformat(),
        sha256=_sha256_file(local_path),
        row_count=int(frame.shape[0]),
        column_count=int(frame.shape[1]),
        missing_cells=int(frame.isna().sum().sum()),
        missingness_observed_or_injected=missingness_observed_or_injected,
        outcome_definition=outcome_definition,
    )


def save_provenance(record: ProvenanceRecord, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(asdict(record), ensure_ascii=False, indent=2), encoding="utf-8")


def _numeric_columns(frame: pd.DataFrame, excluded: Iterable[str]) -> List[str]:
    excluded_set = set(excluded)
    columns = []
    for column in frame.columns:
        if column in excluded_set:
            continue
        converted = pd.to_numeric(frame[column], errors="coerce")
        if converted.notna().any():
            columns.append(column)
    return columns


def to_decision_matrix(
    frame: pd.DataFrame,
    *,
    id_column: str,
    criterion_columns: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Convert a validated external table into X, Sigma, and stable row IDs."""
    if id_column not in frame.columns:
        raise ValueError(f"Missing required id column: {id_column}")
    columns = criterion_columns or _numeric_columns(frame, [id_column])
    if len(columns) < 2:
        raise ValueError("At least two numeric criterion columns are required")
    numeric = frame[columns].apply(pd.to_numeric, errors="coerce")
    values = numeric.fillna(0.0).to_numpy(dtype=float)
    sigma = np.where(numeric.notna(), "A", "I")
    return {
        "ids": frame[id_column].astype(str).tolist(),
        "criteria": columns,
        "X": values,
        "Sigma": sigma,
        "missing_cells": int(numeric.isna().sum().sum()),
    }
