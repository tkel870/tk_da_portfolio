-- ================================
-- INDUSTRIAL OPERATIONS WAR ROOM
-- Master Schema
-- ================================

PRAGMA foreign_keys = ON;

-- Drop tables if they exist (safe rebuild)
DROP TABLE IF EXISTS production;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS parts;
DROP TABLE IF EXISTS suppliers;

-- ================================
-- SUPPLIERS TABLE
-- ================================
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY,
    supplier_name TEXT,
    region TEXT
);

-- ================================
-- PARTS TABLE
-- ================================
CREATE TABLE parts (
    part_id INTEGER PRIMARY KEY,
    part_name TEXT,
    category TEXT,
    supplier_id INTEGER,
    unit_cost REAL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

-- ================================
-- INVENTORY TABLE
-- ================================
CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY,
    part_id INTEGER,
    stock_level INTEGER,
    reorder_point INTEGER,
    warehouse TEXT,
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);

-- ================================
-- SHIPMENTS TABLE
-- ================================
CREATE TABLE shipments (
    shipment_id INTEGER PRIMARY KEY,
    supplier_id INTEGER,
    part_id INTEGER,
    ship_date TEXT,
    arrival_date TEXT,
    shipping_cost REAL,
    status TEXT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);

-- ================================
-- PRODUCTION TABLE
-- ================================
CREATE TABLE production (
    production_id INTEGER PRIMARY KEY,
    part_id INTEGER,
    production_date TEXT,
    units_produced INTEGER,
    downtime_minutes INTEGER,
    defects INTEGER,
    plant TEXT,
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);
