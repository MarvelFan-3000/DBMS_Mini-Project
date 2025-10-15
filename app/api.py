from __future__ import annotations

from datetime import datetime, date
from typing import Dict, Any

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError

from .auth import api_login_required
from .extensions import db
from .models import Item


api_bp = Blueprint("api", __name__, url_prefix="/api")


def item_to_dict(item: Item) -> Dict[str, Any]:
    return {
        "id": item.id,
        "item_code": item.item_code,
        "name": item.name,
        "category": item.category,
        "quantity": item.quantity,
        "location": item.location,
        "date_of_procurement": item.date_of_procurement.isoformat(),
        "disposal_status": item.disposal_status,
        "notes": item.notes,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        "age_days": (date.today() - item.date_of_procurement).days,
    }


@api_bp.get("/items")
@api_login_required
def list_items():
    q = (request.args.get("q") or "").strip()
    category = (request.args.get("category") or "").strip()
    location = (request.args.get("location") or "").strip()
    status = (request.args.get("status") or "").strip()

    query = Item.query

    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Item.item_code.ilike(like), Item.name.ilike(like)))

    if category:
        query = query.filter(Item.category == category)

    if location:
        query = query.filter(Item.location == location)

    if status:
        query = query.filter(Item.disposal_status == status)

    items = query.order_by(Item.updated_at.desc()).all()

    # For filters in the UI
    categories = [c[0] for c in db.session.query(Item.category).distinct().all() if c[0]]
    locations = [l[0] for l in db.session.query(Item.location).distinct().all() if l[0]]
    statuses = [s[0] for s in db.session.query(Item.disposal_status).distinct().all() if s[0]]

    return jsonify({
        "items": [item_to_dict(i) for i in items],
        "filters": {
            "categories": sorted(categories),
            "locations": sorted(locations),
            "statuses": sorted(statuses),
        },
    })


@api_bp.post("/items")
@api_login_required
def create_item():
    data = request.get_json(silent=True) or {}
    try:
        item = Item(
            item_code=(data.get("item_code") or "").strip(),
            name=(data.get("name") or "").strip(),
            category=(data.get("category") or None),
            quantity=int(data.get("quantity") or 0),
            location=(data.get("location") or None),
            date_of_procurement=datetime.strptime(data.get("date_of_procurement"), "%Y-%m-%d").date(),
            disposal_status=(data.get("disposal_status") or "Active"),
            notes=(data.get("notes") or None),
        )
    except Exception:
        return jsonify({"error": "Invalid payload"}), 400

    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Item code must be unique"}), 409

    return jsonify(item_to_dict(item)), 201


@api_bp.get("/items/<int:item_id>")
@api_login_required
def get_item(item_id: int):
    item = Item.query.get_or_404(item_id)
    return jsonify(item_to_dict(item))


@api_bp.put("/items/<int:item_id>")
@api_login_required
def update_item(item_id: int):
    item = Item.query.get_or_404(item_id)
    data = request.get_json(silent=True) or {}
    try:
        item.item_code = (data.get("item_code") or "").strip()
        item.name = (data.get("name") or "").strip()
        item.category = (data.get("category") or None)
        item.quantity = int(data.get("quantity") or 0)
        item.location = (data.get("location") or None)
        item.date_of_procurement = datetime.strptime(data.get("date_of_procurement"), "%Y-%m-%d").date()
        item.disposal_status = (data.get("disposal_status") or "Active")
        item.notes = (data.get("notes") or None)
    except Exception:
        return jsonify({"error": "Invalid payload"}), 400

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Item code must be unique"}), 409

    return jsonify(item_to_dict(item))


@api_bp.delete("/items/<int:item_id>")
@api_login_required
def delete_item(item_id: int):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"ok": True})


@api_bp.get("/reports/aging")
@api_login_required
def aging_report():
    items = Item.query.all()
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

    summary = {label: {"count": 0, "quantity": 0} for label, _, _ in buckets}

    today = date.today()
    for item in items:
        age_days = (today - item.date_of_procurement).days
        label = bucket_for_days(age_days)
        summary[label]["count"] += 1
        summary[label]["quantity"] += (item.quantity or 0)

    return jsonify({
        "summary": summary,
        "items": [item_to_dict(i) for i in items],
    })
