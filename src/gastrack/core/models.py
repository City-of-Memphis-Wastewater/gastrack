import uuid
from datetime import datetime
from typing import Optional, Literal
from msgspec import Struct, field

# Define the valid sample points based on your spreadsheet data
SAMPLE_POINTS = Literal['Sheet 1', 'Sheet 2', 'Sheet 3', 'Sheet 4', 'Sheet 5', 'Sheet 6', 
                        'Inlet', 'Outlet']


# --- Analyzer Data Model (Irregular TS) ---
# Set kw_only=True to allow optional fields (with defaults) before required fields,
# though we still enforce ordering below for clarity.
class AnalyzerReading(Struct, kw_only=True): 
    # REQUIRED FIELDS first (best practice)
    timestamp: datetime
    sample_point: SAMPLE_POINTS

    # OPTIONAL FIELDS (with defaults)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    o2_pct: Optional[float] = None
    co2_pct: Optional[float] = None
    h2s_ppm: Optional[float] = None
    ch4_pct: Optional[float] = None
    net_cal_val_mj_m3: Optional[float] = None
    gross_cal_val_mj_m3: Optional[float] = None
    t_sensor_f: Optional[float] = None
    balance_n2_pct: Optional[float] = None

    # Audit fields for data corrections/fudging (Q5)
    is_manual_override: bool = False
    override_note: Optional[str] = None

# --- Daily Flow Input Model ---
class DailyFlowInput(Struct):
    date: str # Use string for date entry (e.g., "2025-09-01") for simplicity
    blower_1_scf_day: Optional[float] = None
    blower_2a_scf_day: Optional[float] = None
    blower_2b_scf_day: Optional[float] = None
    blower_2c_scf_day: Optional[float] = None
    biorem_ambient_air_scf_day: Optional[float] = None
    biogas_flared_scf_day: Optional[float] = None

# --- Factor Model (for EmFactors) ---
class Factor(Struct):
    key: str
    value: float
    description: Optional[str] = None