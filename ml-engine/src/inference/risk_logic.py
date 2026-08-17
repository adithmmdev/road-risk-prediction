"""Pure risk-fusion logic used by the inference service."""


def classify_risk(final_risk: float) -> str:
    """Map a 0-100 risk score to a user-facing tier."""
    if final_risk < 35:
        return "LOW"
    if final_risk < 70:
        return "MEDIUM"
    return "HIGH"


def fuse_risk(ml_risk: float, geometry_risk: float) -> tuple[float, str]:
    """Combine ML and geometry risk into the final score and tier."""
    if not 0 <= ml_risk <= 100:
        raise ValueError("ml_risk must be between 0 and 100")
    if not 0 <= geometry_risk <= 100:
        raise ValueError("geometry_risk must be between 0 and 100")

    final_risk = 0.65 * ml_risk + 0.35 * geometry_risk
    return round(final_risk, 2), classify_risk(final_risk)
