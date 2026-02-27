from dataclasses import dataclass


@dataclass
class Factor:
    name: str
    score: int        # 0=red, 1=yellow, 2=green
    label: str        # "Good", "Caution", "Poor"
    explanation: str


@dataclass
class SuitabilityScore:
    overall: int              # 0–100
    rating: str               # "Excellent", "Good", "Fair", "Poor"
    factors: list[Factor]
    notes: list[str]


def score_green_roof(building: dict) -> SuitabilityScore:
    factors = []
    notes = []

    # --- Roof area ---
    lot_area = building.get("lot_area") or 0
    if lot_area >= 5000:
        factors.append(Factor("Roof Area", 2, "Good", f"Large lot area ({int(lot_area):,} sq ft) — good candidate for meaningful green roof coverage."))
    elif lot_area >= 1500:
        factors.append(Factor("Roof Area", 1, "Moderate", f"Medium lot area ({int(lot_area):,} sq ft) — viable but smaller installation."))
    else:
        factors.append(Factor("Roof Area", 0, "Poor", f"Small lot area ({int(lot_area):,} sq ft) — limited space for a green roof."))

    # --- Building age / structural risk ---
    year_built = building.get("year_built")
    if year_built and year_built >= 1980:
        factors.append(Factor("Structural Risk", 2, "Good", f"Built in {year_built} — modern construction, lower structural uncertainty."))
    elif year_built and year_built >= 1940:
        factors.append(Factor("Structural Risk", 1, "Caution", f"Built in {year_built} — mid-century construction. Structural assessment recommended."))
    elif year_built:
        factors.append(Factor("Structural Risk", 0, "High Risk", f"Built in {year_built} — pre-war building. Structural engineer review strongly advised before any green roof installation."))
        notes.append("Pre-war buildings often have lower load-bearing capacity. This is a risk flag, not a disqualifier.")
    else:
        factors.append(Factor("Structural Risk", 1, "Unknown", "Year built unknown — structural assessment required."))

    # --- Building height / access ---
    floors = building.get("num_floors") or 0
    if floors <= 6:
        factors.append(Factor("Roof Access", 2, "Good", f"{int(floors)}-story building — roof access is straightforward."))
    elif floors <= 20:
        factors.append(Factor("Roof Access", 1, "Moderate", f"{int(floors)}-story building — roof access and material delivery will require planning."))
    else:
        factors.append(Factor("Roof Access", 0, "Difficult", f"{int(floors)}-story high-rise — roof access is complex and costly."))

    # --- Building class (use type) ---
    bclass = (building.get("building_class") or "").upper()
    if bclass.startswith(("D", "H", "O", "R")):  # Residential, hotels, offices
        factors.append(Factor("Building Type", 2, "Good", f"Building class {bclass} — residential or commercial buildings are common green roof candidates."))
    elif bclass.startswith(("C", "K", "L", "S")):  # Retail, garages
        factors.append(Factor("Building Type", 1, "Moderate", f"Building class {bclass} — viable with design consideration."))
    elif bclass.startswith(("F", "G")):  # Industrial
        factors.append(Factor("Building Type", 1, "Moderate", f"Building class {bclass} — industrial buildings often have flat roofs ideal for green roofs."))
    else:
        factors.append(Factor("Building Type", 1, "Moderate", f"Building class {bclass} — review specific use requirements."))

    # --- Compute overall score ---
    raw = sum(f.score for f in factors)
    max_raw = len(factors) * 2
    overall = int((raw / max_raw) * 100) if max_raw else 0

    if overall >= 75:
        rating = "Excellent"
    elif overall >= 50:
        rating = "Good"
    elif overall >= 25:
        rating = "Fair"
    else:
        rating = "Poor"

    return SuitabilityScore(overall=overall, rating=rating, factors=factors, notes=notes)
