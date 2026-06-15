"""
PENdp D14 Integration Module

DEPRECATION NOTICE:
    patch_engine_weights() is deprecated. Use integration.update_weights_with_d14()
    for dynamic weight adjustment instead.

Single source of truth for D14_WEIGHT: imported from pendp.config
"""
import warnings
from typing import Dict, Optional

from pendp.config import D14_WEIGHT


def patch_engine_weights(
    base_weights: Optional[Dict[str, float]] = None,
    d14_borrow_from: str = "D2",
    borrow_amount: float = 0.025,
) -> Dict[str, float]:
    """DEPRECATED: Static weight borrowing for D14.

    Borrows weight from one dimension and assigns it to D14.
    Replaced by integration.update_weights_with_d14() which does
    dynamic adjustment based on D14 score.

    Args:
        base_weights: Base weights dict (default: from SCORING_DIMENSIONS)
        d14_borrow_from: Dimension to borrow from (default: "D2")
        borrow_amount: Amount to borrow (default: 0.025 = 2.5%)

    Returns:
        Adjusted weights dict with total = 1.0
    """
    warnings.warn(
        "patch_engine_weights() is deprecated. "
        "Use integration.update_weights_with_d14() for dynamic weight adjustment.",
        DeprecationWarning,
        stacklevel=2,
    )

    from pendp.pipeline.integration import update_weights_with_d14

    # Forward to the dynamic version
    return update_weights_with_d14(
        base_weights=base_weights,
        d14_score=5.0,  # Neutral score = static borrowing behavior
    )
