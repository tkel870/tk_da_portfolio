import sqlite3
import random
from datetime import date, timedelta

DB_PATH = r"../industrial_war_room.db"

random.seed(42)

REGIONS = ["Midwest", "South", "West", "Northeast", "International"]
WAREHOUSES = ["WH-A", "WH-B", "WH-C"]
PLANTS = ["Decatur", "Peoria", "Aurora"]
CATEGORIES = ["Hydraulics", "Powertrain", "Electrical", "Chassis", "Cab", "Fasteners", "Cooling", "Fuel"]

def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Speed + integrity
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")

    # Wipe existing data (keep schema)
    cur.executescript("""
    DELETE FROM production;
    DELETE FROM shipments;
    DELETE FROM inventory;
    DELETE FROM parts;
    DELETE FROM suppliers;
    """)
    conn.commit()

    # -----------------------
    # 1) Suppliers (60)
    # -----------------------
    suppliers = []
    for sid in range(1, 61):
        name = f"Supplier {sid:03d}"
        region = random.choice(REGIONS)
        suppliers.append((sid, name, region))
    cur.executemany(
        "INSERT INTO suppliers (supplier_id, supplier_name, region) VALUES (?, ?, ?);",
        suppliers
    )
    conn.commit()

    # -----------------------
    # 2) Parts (~800)
    # -----------------------
    parts = []
    for pid in range(1, 801):
        category = random.choice(CATEGORIES)
        supplier_id = random.randint(1, 60)
        part_name = f"{category} Part {pid:04d}"
        # Costs vary by category
        base = {
            "Hydraulics": 180,
            "Powertrain": 450,
            "Electrical": 95,
            "Chassis": 300,
            "Cab": 220,
            "Fasteners": 8,
            "Cooling": 120,
            "Fuel": 75
        }[category]
        unit_cost = round(random.uniform(base * 0.6, base * 1.6), 2)
        parts.append((pid, part_name, category, supplier_id, unit_cost))
    cur.executemany(
        "INSERT INTO parts (part_id, part_name, category, supplier_id, unit_cost) VALUES (?, ?, ?, ?, ?);",
        parts
    )
    conn.commit()

    # -----------------------
    # Date window (1 year)
    # -----------------------
    start = date(2024, 1, 1)
    end   = date(2024, 12, 31)
    all_days = list(daterange(start, end))

    # -----------------------
    # 3) Shipments (~25k+)
    # -----------------------
    shipment_rows = []
    shipment_id = 1

    # Create supplier reliability: some are "problem vendors"
    vendor_risk = {sid: random.random() for sid in range(1, 61)}
    # Top ~10 risky suppliers
    risky_suppliers = sorted(vendor_risk, key=vendor_risk.get, reverse=True)[:10]

    for _ in range(26000):
        part_id, part_name, category, supplier_id, unit_cost = random.choice(parts)
        ship_day = random.choice(all_days)

        # Lead time baseline by category
        base_lead = {
            "Fasteners": 2,
            "Electrical": 4,
            "Fuel": 5,
            "Cooling": 6,
            "Hydraulics": 7,
            "Cab": 8,
            "Chassis": 9,
            "Powertrain": 10
        }[category]

        # Risky suppliers have higher delays
        delay_bias = 0
        if supplier_id in risky_suppliers:
            delay_bias = random.choice([0, 1, 2, 3, 5, 7])

        transit = base_lead + random.randint(0, 5) + delay_bias
        arrival = ship_day + timedelta(days=transit)

        # Cost tied loosely to transit distance & part cost
        shipping_cost = round(max(15, random.uniform(0.03, 0.12) * unit_cost * (1 + transit/10)), 2)

        status = "Delivered"  # keep simple, can add In Transit later
        shipment_rows.append((
            shipment_id,
            supplier_id,
            part_id,
            ship_day.isoformat(),
            arrival.isoformat(),
            shipping_cost,
            status
        ))
        shipment_id += 1

    cur.executemany("""
        INSERT INTO shipments
        (shipment_id, supplier_id, part_id, ship_date, arrival_date, shipping_cost, status)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, shipment_rows)
    conn.commit()

    # -----------------------
    # 4) Inventory snapshots (~12k)
    # -----------------------
    # We create weekly snapshots for a subset of parts
    inv_rows = []
    inventory_id = 1
    tracked_parts = random.sample([p[0] for p in parts], 600)  # track 600 parts
    for day in all_days[::7]:  # weekly
        wh = random.choice(WAREHOUSES)
        for part_id in random.sample(tracked_parts, 200):  # 200 parts per snapshot week
            stock = random.randint(0, 800)
            reorder_point = random.randint(50, 200)
            inv_rows.append((inventory_id, part_id, stock, reorder_point, wh))
            inventory_id += 1

    cur.executemany("""
        INSERT INTO inventory
        (inventory_id, part_id, stock_level, reorder_point, warehouse)
        VALUES (?, ?, ?, ?, ?);
    """, inv_rows)
    conn.commit()

    # -----------------------
    # 5) Production daily (~25k)
    # -----------------------
    # We simulate that production uses parts; delays/defects correlate with risky suppliers.
    prod_rows = []
    production_id = 1

    # Map each part to supplier_id quickly
    part_to_supplier = {p[0]: p[3] for p in parts}
    part_to_category = {p[0]: p[2] for p in parts}

    for _ in range(26000):
        prod_day = random.choice(all_days)
        plant = random.choice(PLANTS)
        part_id = random.choice(tracked_parts)

        supplier_id = part_to_supplier[part_id]
        category = part_to_category[part_id]

        # Baseline production rates by category
        base_units = {
            "Fasteners": 120,
            "Electrical": 60,
            "Fuel": 55,
            "Cooling": 45,
            "Hydraulics": 35,
            "Cab": 22,
            "Chassis": 18,
            "Powertrain": 14
        }[category]

        units = max(0, int(random.gauss(base_units, base_units * 0.15)))

        # Downtime higher for risky suppliers
        downtime = int(max(0, random.gauss(35, 20)))
        if supplier_id in risky_suppliers:
            downtime += random.randint(20, 160)

        # Defects: slightly higher in certain categories + risky suppliers
        defect_base = {
            "Fasteners": 0.002,
            "Electrical": 0.010,
            "Fuel": 0.008,
            "Cooling": 0.009,
            "Hydraulics": 0.012,
            "Cab": 0.015,
            "Chassis": 0.011,
            "Powertrain": 0.018
        }[category]
        defect_rate = defect_base + (0.010 if supplier_id in risky_suppliers else 0.0)
        defects = int(round(units * min(0.08, defect_rate + random.uniform(-0.003, 0.006))))

        prod_rows.append((
            production_id,
            part_id,
            prod_day.isoformat(),
            units,
            downtime,
            defects,
            plant
        ))
        production_id += 1

    cur.executemany("""
        INSERT INTO production
        (production_id, part_id, production_date, units_produced, downtime_minutes, defects, plant)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """, prod_rows)
    conn.commit()

    # -----------------------
    # Summary counts
    # -----------------------
    def count(tbl):
        return cur.execute(f"SELECT COUNT(*) FROM {tbl};").fetchone()[0]

    print("✅ Data generated and loaded.")
    print("Row counts:")
    for t in ["suppliers", "parts", "shipments", "inventory", "production"]:
        print(f"  {t}: {count(t):,}")

    conn.close()

if __name__ == "__main__":
    main()
