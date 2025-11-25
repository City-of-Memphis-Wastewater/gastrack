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
-- This holds the EmFactors! constants.
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
-- Example factor placeholder (e.g., NOx factor from EmFactors!)
INSERT INTO factors (key, value, description) VALUES
('EMF_NOX_LBS_MMBTU', 0.05, 'Placeholder NOx Emission Factor for Flared Biogas (lbs/MMbtu).'),
('EMF_CO_LBS_MMBTU', 0.1, 'Placeholder CO Emission Factor for Flared Biogas (lbs/MMbtu).'),
('EMF_VOC_LBS_MMBTU', 0.03, 'Placeholder VOC Emission Factor for Flared Biogas (lbs/MMbtu).'),
('EMF_SO2_H2S_CONVERSION_FACTOR', 0.8, 'Placeholder H2S to SO2 Conversion Factor (80% efficiency for flare).');

