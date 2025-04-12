-- console.sql

-- Drop the table if it already exists
DROP TABLE IF EXISTS equipment_history;

-- Create the equipment_history table
CREATE TABLE equipment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id TEXT NOT NULL,
    equipment_num TEXT NOT NULL,
    equipment_name TEXT NOT NULL,
    equipment_type TEXT NOT NULL,
    date DATETIME NOT NULL,
    author TEXT NOT NULL,
    design_pressure REAL NOT NULL,
    diameter_radius REAL,
    allowable_stress REAL NOT NULL,
    joint_efficiency REAL NOT NULL,
    corrosion_allowance REAL NOT NULL,
    initial_thickness REAL NOT NULL,
    actual_thickness REAL NOT NULL,
    time_years INTEGER NOT NULL,
    corrosion_rate REAL NOT NULL,
    corrosion_type TEXT NOT NULL,
    remaining_life REAL NOT NULL,
    next_inspection INTEGER NOT NULL,
    inspection_interval INTEGER NOT NULL,
    timestamp DATETIME NOT NULL
);