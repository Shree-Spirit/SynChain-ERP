"""Load demo users and sample ERP records. Safe to run more than once."""

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.security import UserRole, hash_password
from app.db.session import SessionLocal
from app.models.inventory import InventoryItem
from app.models.invoice import Invoice
from app.models.order import Order, OrderItem
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.supplier import Supplier
from app.models.user import User
from app.models.warehouse import Warehouse
from app.utils.audit import register_audit_listeners, set_current_actor


def seed() -> None:
    register_audit_listeners()
    set_current_actor("seed-script")
    db = SessionLocal()
    try:
        _ensure_users(db)
        if db.scalar(select(Supplier).limit(1)) is not None:
            db.commit()
            print("Seed skipped: sample business data already exists.")
            return

        warehouses = [
            Warehouse(name="Kolhapur Main DC", location="Shiroli MIDC, Kolhapur", capacity=10000),
            Warehouse(name="Pune Satellite", location="Chakan, Pune", capacity=4500),
            Warehouse(name="Mumbai Bonded", location="Nhava Sheva, Navi Mumbai", capacity=8000),
        ]
        db.add_all(warehouses)
        db.flush()

        suppliers = [
            Supplier(
                name="Sahyadri Steel Traders",
                contact_email="sales@sahyadristeel.example",
                phone="+91-231-2401001",
                address="Gokul Shirgaon MIDC, Kolhapur",
                category="Raw Materials",
                performance_rating=Decimal("4.50"),
            ),
            Supplier(
                name="Deccan Packaging Co.",
                contact_email="orders@deccanpack.example",
                phone="+91-20-26001122",
                address="Pimpri, Pune",
                category="Packaging",
                performance_rating=Decimal("4.10"),
            ),
            Supplier(
                name="Western Logistics Pvt Ltd",
                contact_email="ops@westernlog.example",
                phone="+91-22-27771234",
                address="Turbhe, Navi Mumbai",
                category="Logistics",
                performance_rating=Decimal("3.80"),
            ),
            Supplier(
                name="Greenfield Agro Inputs",
                contact_email="hello@greenfieldagro.example",
                phone="+91-231-2533009",
                address="Ichalkaranji, Maharashtra",
                category="Consumables",
                performance_rating=Decimal("4.70"),
            ),
            Supplier(
                name="Kitronics Components",
                contact_email="support@kitronics.example",
                phone="+91-231-2698000",
                address="KIT Campus Area, Kolhapur",
                category="Electronics",
                performance_rating=Decimal("4.20"),
            ),
        ]
        db.add_all(suppliers)
        db.flush()

        inventory = [
            InventoryItem(
                sku="STL-HR-001",
                name="HR Steel Coil 2mm",
                quantity=120,
                unit="ton",
                reorder_level=40,
                warehouse_id=warehouses[0].id,
            ),
            InventoryItem(
                sku="PKG-CTN-20",
                name="Corrugated Carton 20kg",
                quantity=800,
                unit="pcs",
                reorder_level=200,
                warehouse_id=warehouses[1].id,
            ),
            InventoryItem(
                sku="ELC-PCB-A4",
                name="Controller PCB A4",
                quantity=60,
                unit="pcs",
                reorder_level=25,
                warehouse_id=warehouses[0].id,
            ),
            InventoryItem(
                sku="AGR-WRP-05",
                name="Shrink Wrap Roll",
                quantity=45,
                unit="roll",
                reorder_level=15,
                warehouse_id=warehouses[1].id,
            ),
            InventoryItem(
                sku="LOG-PLT-EU",
                name="Euro Pallet",
                quantity=300,
                unit="pcs",
                reorder_level=80,
                warehouse_id=warehouses[2].id,
            ),
            InventoryItem(
                sku="STL-BLT-M8",
                name="M8 Fastener Kit",
                quantity=15,
                unit="box",
                reorder_level=20,
                warehouse_id=warehouses[0].id,
            ),
            InventoryItem(
                sku="ELC-SNS-12",
                name="12V Proximity Sensor",
                quantity=90,
                unit="pcs",
                reorder_level=30,
                warehouse_id=warehouses[0].id,
            ),
            InventoryItem(
                sku="PKG-TAP-48",
                name="Packing Tape 48mm",
                quantity=500,
                unit="roll",
                reorder_level=100,
                warehouse_id=warehouses[1].id,
            ),
        ]
        db.add_all(inventory)
        db.flush()

        po1 = PurchaseOrder(
            supplier_id=suppliers[0].id,
            status="sent",
            expected_date=date.today() + timedelta(days=7),
            items=[
                PurchaseOrderItem(sku="STL-HR-001", name="HR Steel Coil 2mm", quantity=20, unit_price=Decimal("42500.00")),
            ],
        )
        po2 = PurchaseOrder(
            supplier_id=suppliers[1].id,
            status="received",
            expected_date=date.today() - timedelta(days=2),
            items=[
                PurchaseOrderItem(sku="PKG-CTN-20", name="Corrugated Carton 20kg", quantity=200, unit_price=Decimal("38.50")),
                PurchaseOrderItem(sku="PKG-TAP-48", name="Packing Tape 48mm", quantity=50, unit_price=Decimal("55.00")),
            ],
        )
        po3 = PurchaseOrder(
            supplier_id=suppliers[4].id,
            status="draft",
            expected_date=date.today() + timedelta(days=14),
            items=[
                PurchaseOrderItem(sku="ELC-SNS-12", name="12V Proximity Sensor", quantity=40, unit_price=Decimal("620.00")),
            ],
        )
        db.add_all([po1, po2, po3])
        db.flush()

        order1 = Order(
            customer_name="Shivaji Auto Components",
            status="processing",
            order_date=date.today() - timedelta(days=3),
            items=[
                OrderItem(sku="ELC-PCB-A4", name="Controller PCB A4", quantity=10, unit_price=Decimal("1450.00")),
                OrderItem(sku="ELC-SNS-12", name="12V Proximity Sensor", quantity=8, unit_price=Decimal("799.00")),
            ],
        )
        order2 = Order(
            customer_name="Kolhapur Foundry Works",
            status="shipped",
            order_date=date.today() - timedelta(days=8),
            items=[
                OrderItem(sku="STL-BLT-M8", name="M8 Fastener Kit", quantity=5, unit_price=Decimal("890.00")),
            ],
        )
        order3 = Order(
            customer_name="Campus Store KIT",
            status="pending",
            order_date=date.today(),
            items=[
                OrderItem(sku="PKG-CTN-20", name="Corrugated Carton 20kg", quantity=25, unit_price=Decimal("49.00")),
            ],
        )
        db.add_all([order1, order2, order3])
        db.flush()

        db.add_all(
            [
                Invoice(
                    order_id=order1.id,
                    amount=Decimal("20892.00"),
                    status="unpaid",
                    due_date=date.today() + timedelta(days=15),
                ),
                Invoice(
                    purchase_order_id=po2.id,
                    amount=Decimal("10450.00"),
                    status="paid",
                    due_date=date.today() - timedelta(days=1),
                ),
                Invoice(
                    order_id=order2.id,
                    amount=Decimal("4450.00"),
                    status="overdue",
                    due_date=date.today() - timedelta(days=5),
                ),
            ]
        )
        db.commit()
        print("Seed completed: users, suppliers, warehouses, inventory, POs, orders, invoices.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _ensure_users(db) -> None:
    if db.scalar(select(User).where(User.username == "admin")) is None:
        db.add(
            User(
                username="admin",
                email="admin@synchain.local",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
        )
    if db.scalar(select(User).where(User.username == "ops")) is None:
        db.add(
            User(
                username="ops",
                email="ops@synchain.local",
                hashed_password=hash_password("ops123"),
                role=UserRole.OPERATIONS.value,
                is_active=True,
            )
        )
    db.flush()


if __name__ == "__main__":
    seed()
