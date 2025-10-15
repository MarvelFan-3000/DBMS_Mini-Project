from __future__ import annotations

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError

from .auth import login_required
from .extensions import db
from .models import Item


items_bp = Blueprint("items", __name__, url_prefix="/items")


@items_bp.route("/", methods=["GET"])  # convenience redirect
def root():
    return redirect(url_for("items.list_items"))


@items_bp.route("", methods=["GET"])  # list and search
@login_required
def list_items():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    location = request.args.get("location", "").strip()
    status = request.args.get("status", "").strip()

    query = Item.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(Item.item_code.ilike(like), Item.name.ilike(like))
        )

    if category:
        query = query.filter(Item.category == category)

    if location:
        query = query.filter(Item.location == location)

    if status:
        query = query.filter(Item.disposal_status == status)

    items = query.order_by(Item.updated_at.desc()).all()

    # Gather distinct values for filters
    categories = [c[0] for c in db.session.query(Item.category).distinct().all() if c[0]]
    locations = [l[0] for l in db.session.query(Item.location).distinct().all() if l[0]]
    statuses = [s[0] for s in db.session.query(Item.disposal_status).distinct().all() if s[0]]

    return render_template(
        "items/list.html",
        items=items,
        q=q,
        category=category,
        location=location,
        status=status,
        categories=sorted(categories),
        locations=sorted(locations),
        statuses=sorted(statuses),
    )


@items_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_item():
    if request.method == "POST":
        item = Item(
            item_code=request.form.get("item_code", "").strip(),
            name=request.form.get("name", "").strip(),
            category=request.form.get("category", "").strip() or None,
            quantity=int(request.form.get("quantity", 0) or 0),
            location=request.form.get("location", "").strip() or None,
            date_of_procurement=datetime.strptime(
                request.form.get("date_of_procurement"), "%Y-%m-%d"
            ).date(),
            disposal_status=request.form.get("disposal_status", "Active").strip() or "Active",
            notes=request.form.get("notes", "").strip() or None,
        )
        db.session.add(item)
        try:
            db.session.commit()
            flash("Item created successfully.", "success")
            return redirect(url_for("items.list_items"))
        except IntegrityError:
            db.session.rollback()
            flash("Item code must be unique.", "danger")

    return render_template("items/form.html", item=None)


@items_bp.route("/<int:item_id>", methods=["GET"])  
@login_required
def view_item(item_id: int):
    item = Item.query.get_or_404(item_id)
    return render_template("items/detail.html", item=item)


@items_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])  
@login_required
def edit_item(item_id: int):
    item = Item.query.get_or_404(item_id)

    if request.method == "POST":
        item.item_code = request.form.get("item_code", "").strip()
        item.name = request.form.get("name", "").strip()
        item.category = request.form.get("category", "").strip() or None
        item.quantity = int(request.form.get("quantity", 0) or 0)
        item.location = request.form.get("location", "").strip() or None
        item.date_of_procurement = datetime.strptime(
            request.form.get("date_of_procurement"), "%Y-%m-%d"
        ).date()
        item.disposal_status = request.form.get("disposal_status", "Active").strip() or "Active"
        item.notes = request.form.get("notes", "").strip() or None

        try:
            db.session.commit()
            flash("Item updated successfully.", "success")
            return redirect(url_for("items.view_item", item_id=item.id))
        except IntegrityError:
            db.session.rollback()
            flash("Item code must be unique.", "danger")

    return render_template("items/form.html", item=item)


@items_bp.route("/<int:item_id>/delete", methods=["POST"])  
@login_required
def delete_item(item_id: int):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash("Item deleted.", "info")
    return redirect(url_for("items.list_items"))
