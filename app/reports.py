from __future__ import annotations

from collections import defaultdict
from datetime import date
from flask import Blueprint, render_template

from .auth import login_required
from .models import Item


reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


@reports_bp.route("/aging", methods=["GET"])  
@login_required
def aging_report():
    items = Item.query.all()

    # Buckets in days
    buckets = [
        ("< 6 months", 0, 180),
        ("6-12 months", 180, 365),
        ("1-2 years", 365, 730),
        ("> 2 years", 730, 10_000),
    ]

    def bucket_for_days(days: int) -> str:
        for label, start, end in buckets:
            if start <= days < end:
                return label
        return "> 2 years"

    summary_counts = defaultdict(int)
    summary_quantities = defaultdict(int)

    today = date.today()
    for item in items:
        # Include all items; optionally filter out disposed here if desired
        age_days = (today - item.date_of_procurement).days
        label = bucket_for_days(age_days)
        summary_counts[label] += 1
        summary_quantities[label] += (item.quantity or 0)

    # Sort buckets in the defined order
    ordered_labels = [b[0] for b in buckets]

    return render_template(
        "reports/aging.html",
        items=items,
        ordered_labels=ordered_labels,
        summary_counts=summary_counts,
        summary_quantities=summary_quantities,
    )
