#!/usr/bin/env zsh

echo "Creating database schema files..."

# Create the db directory if it doesn't exist
mkdir -p src/gastrack/db

# Write the DuckDB connection file (connection.py)
cat << EOF > src/gastrack/db/connection.py
import duckdb
import os

# Define the path to the DuckDB database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gastrack.duckdb")

# Define the path to the SQL schema file
SQL_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init_schema.sql")


def get_db_connection():
    """Establishes and returns a DuckDB connection."""
    # Use 'read_only=False' to allow writing
    return duckdb.connect(database=DB_PATH, read_only=False)

def init_db(conn: duckdb.DuckDBPyConnection):
    """Initializes the database schema if tables do not exist."""
    print("Initializing DuckDB schema...")
    try:
        with open(SQL_SCHEMA_PATH, 'r') as f:
            sql_script = f.read()
        
        # Execute the entire SQL script
        conn.execute(sql_script)
        print("DuckDB schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing database schema: {e}")

# This block ensures the database file and schema are created
# the first time any component imports 'connection.py'
if not os.path.exists(DB_PATH):
    print(f"Database file not found at {DB_PATH}. Creating and initializing...")
    conn = get_db_connection()
    init_db(conn)
    conn.close()
    
EOF

# Write the DuckDB schema (init_schema.sql)
cat << EOF > src/gastrack/db/init_schema.sql
-- DuckDB Schema for gastrack Project

-- 1. Raw Time-Series Readings (ts_analyzer_reading)
-- For irregular data from analyzer logs (O2, H2S, CH4, BTUs).
CREATE TABLE IF NOT EXISTS ts_analyzer_reading (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP,
    sample_point VARCHAR, -- e.g., 'Sheet 1', 'Sheet 6', 'Inlet', 'Outlet'
    o2_pct DOUBLE,
    co2_pct DOUBLE,
    h2s_ppm DOUBLE,
    ch4_pct DOUBLE,
    net_cal_val_mj_m3 DOUBLE,
    gross_cal_val_mj_m3 DOUBLE,
    t_sensor_f DOUBLE,
    balance_n2_pct DOUBLE,
    -- Audit fields for data fudging (Q5)
    is_manual_override BOOLEAN DEFAULT FALSE,
    override_note VARCHAR
);

-- 2. Daily Raw Flow Inputs (daily_flow_input)
-- This holds the BGFlow1/BGFlow2 data that may come from daily logs.
CREATE TABLE IF NOT EXISTS daily_flow_input (
    date DATE PRIMARY KEY,
    blower_1_scf_day DOUBLE,
    blower_2a_scf_day DOUBLE,
    blower_2b_scf_day DOUBLE,
    blower_2c_scf_day DOUBLE,
    biorem_ambient_air_scf_day DOUBLE,
    biogas_flared_scf_day DOUBLE
);

-- 3. Constant Emission & Conversion Factors (factors)
-- This holds the EmFactors!$B$x constants.
CREATE TABLE IF NOT EXISTS factors (
    key VARCHAR PRIMARY KEY,
    value DOUBLE,
    description VARCHAR
);

-- Insert initial compliance constants (based on Q4/BG Calcs)
INSERT INTO factors (key, value, description) VALUES
('HHV_PER_CH4_PCT', 10.4, 'HHV [BTU/scf]/100% CH4 - used for BTU calculation.'),
('H2S_PPM_TO_GRAINS_CCF_RATIO', 16.0, 'Conversion ratio for H2S ppm to grains/ccf (from E3 in Q4).');

-- Add placeholder for Emission Factors. These need to be confirmed from the EmFactors sheet.
-- Example factor placeholder (e.g., NOx factor from EmFactors!$B$4)
INSERT INTO factors (key, value, description) VALUES
('EMF_NOX_LBS_MMBTU', 0.05, 'Placeholder NOx Emission Factor for Flared Biogas (lbs/MMbtu).'),
('EMF_CO_LBS_MMBTU', 0.1, 'Placeholder CO Emission Factor for Flared Biogas (lbs/MMbtu).'),
('EMF_VOC_LBS_MMBTU', 0.03, 'Placeholder VOC Emission Factor for Flared Biogas (lbs/MMbtu).'),
('EMF_SO2_H2S_CONVERSION_FACTOR', 0.8, 'Placeholder H2S to SO2 Conversion Factor (80% efficiency for flare).');

EOF

echo "DuckDB connection and schema files created in src/gastrack/db/."
