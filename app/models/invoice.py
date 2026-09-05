from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Invoice(TimestampMixin, Base):
    __tablename__ = "invoices"
    __table_args__ = (
        CheckConstraint(
            "(order_id IS NOT NULL AND purchase_order_id IS NULL) "
            "OR (order_id IS NULL AND purchase_order_id IS NOT NULL)",
            name="ck_invoice_one_source",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    purchase_order_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("purchase_orders.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="unpaid", index=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    order = relationship("Order", back_populates="invoices")
    purchase_order = relationship("PurchaseOrder", back_populates="invoices")
