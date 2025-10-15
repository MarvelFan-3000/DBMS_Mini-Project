from __future__ import annotations

from datetime import date, datetime
from .extensions import db


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    item_code = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False, index=True)
    category = db.Column(db.String(100), index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    location = db.Column(db.String(100), index=True)
    date_of_procurement = db.Column(db.Date, nullable=False)
    disposal_status = db.Column(db.String(20), nullable=False, default="Active", index=True)
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        db.Index("ix_items_procurement_date", "date_of_procurement"),
    )

    @property
    def age_days(self) -> int:
        return (date.today() - self.date_of_procurement).days
