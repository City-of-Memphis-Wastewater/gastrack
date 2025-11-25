import uuid
from typing import List

import duckdb
from msgspec import msgpack

from src.gastrack.db.connection import get_db_connection
from src.gastrack.core.models import AnalyzerReading, DailyFlowInput, Factor

# --- Helper Function for List Ingestion ---
def _serialize_structs_to_tuples(data: List) -> List[tuple]:
    """
    Converts a list of msgspec Structs into a list of tuples 
    suitable for DuckDB's executemany, ensuring UUIDs are converted to strings.
    """
    tuple_data = []
    for item in data:
        # Convert the Struct to a dict, then extract values in order
        item_dict = item.__dict__
        
        # Manually order and convert UUID to string for the DB (DuckDB accepts UUIDs, but string conversion is safest)
        row = []
        for key in item_dict.keys():
            value = item_dict[key]
            if isinstance(value, uuid.UUID):
                row.append(str(value))
            elif isinstance(value, datetime):
                # DuckDB should handle datetime objects directly
                row.append(value)
            else:
                row.append(value)
        tuple_data.append(tuple(row))
        
    return tuple_data


# --- 1. Analyzer Readings (TS Data) ---
def ingest_analyzer_readings(readings: List[AnalyzerReading]) -> int:
    """Inserts a list of AnalyzerReading records into the database."""
    if not readings:
        return 0

    sql = """
    INSERT INTO ts_analyzer_reading (
        id, timestamp, sample_point, o2_pct, co2_pct, h2s_ppm, ch4_pct, 
        net_cal_val_mj_m3, gross_cal_val_mj_m3, t_sensor_f, balance_n2_pct, 
        is_manual_override, override_note
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # DuckDB executemany is efficient for bulk insertion
    data_to_insert = _serialize_structs_to_tuples(readings)

    with get_db_connection() as conn:
        conn.executemany(sql, data_to_insert)
        return conn.rowcount


# --- 2. Daily Flow Input ---
def ingest_daily_flow_inputs(flows: List[DailyFlowInput]) -> int:
    """
    Inserts a list of DailyFlowInput records into the database.
    Uses REPLACE to handle potential re-ingestion for the same date.
    """
    if not flows:
        return 0

    sql = """
    REPLACE INTO daily_flow_input (
        date, blower_1_scf_day, blower_2a_scf_day, blower_2b_scf_day, 
        blower_2c_scf_day, biorem_ambient_air_scf_day, biogas_flared_scf_day
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    # Note: DuckDB's executemany may require data to match the column order exactly
    # The _serialize_structs_to_tuples function needs careful alignment with the Struct definition.
    # For now, we assume models.py fields are defined in the insertion order.
    data_to_insert = [
        (f.date, f.blower_1_scf_day, f.blower_2a_scf_day, f.blower_2b_scf_day, 
         f.blower_2c_scf_day, f.biorem_ambient_air_scf_day, f.biogas_flared_scf_day)
        for f in flows
    ]

    with get_db_connection() as conn:
        conn.executemany(sql, data_to_insert)
        return conn.rowcount

# --- 3. Factors (Retrieval) ---
def get_all_factors() -> List[Factor]:
    """Retrieves all emission and conversion factors from the factors table."""
    sql = "SELECT key, value, description FROM factors"
    
    with get_db_connection() as conn:
        # Fetch data as a list of tuples
        result = conn.execute(sql).fetchall()
    
    # Convert tuples back to msgspec Factor Structs
    factors = [Factor(key=row[0], value=row[1], description=row[2]) for row in result]
    return factors