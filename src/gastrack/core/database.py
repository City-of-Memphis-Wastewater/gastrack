-- Table 1: Raw Time-Series Readings (ts_analyzer_reading)
CREATE TABLE ts_analyzer_reading (
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

-- Table 2: Daily Raw Flow Inputs (daily_flow_input)
-- This holds the BGFlow1/BGFlow2 data that may come from daily logs.
CREATE TABLE daily_flow_input (
    date DATE PRIMARY KEY,
    blower_1_scf_day DOUBLE,
    blower_2a_scf_day DOUBLE,
    blower_2b_scf_day DOUBLE,
    blower_2c_scf_day DOUBLE,
    biorem_ambient_air_scf_day DOUBLE,
    biogas_flared_scf_day DOUBLE
);

-- Table 3: Constant Emission & Conversion Factors (factors)
-- This holds the EmFactors!$B$x constants.
CREATE TABLE factors (
    key VARCHAR PRIMARY KEY,
    value DOUBLE,
    description VARCHAR
);