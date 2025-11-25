from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.exceptions import HTTPException
from typing import List
from dataclasses import asdict
from msgspec import msgpack, ValidationError

from src.gastrack.db import crud
from src.gastrack.core.models import AnalyzerReading, DailyFlowInput, Factor

# --- Handlers ---

async def ingest_readings(request: Request):
    """
    POST endpoint to ingest time-series analyzer readings.
    Expects a JSON body that can be decoded into a list of AnalyzerReading structs.
    """
    try:
        # 1. Decode and Validate using msgspec
        # Use msgspec's decoding for high-performance and validation
        body = await request.body()
        readings: List[AnalyzerReading] = msgpack.decode(
            body, type=List[AnalyzerReading], 
            # Allow 'extra_fields' is often good for flexibility, 
            # but we keep it strict for better data quality.
            # extra_fields='forbid' is the default for msgspec.
        )
    except ValidationError as e:
        # Return a 400 Bad Request if validation fails
        raise HTTPException(status_code=400, detail=f"Validation Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload format: {e}")

    # 2. Database Ingestion
    try:
        inserted_count = crud.ingest_analyzer_readings(readings)
        return JSONResponse(
            {"status": "success", "message": f"Successfully ingested {inserted_count} analyzer readings."}, 
            status_code=201
        )
    except Exception as e:
        # Log this error properly in a production system
        raise HTTPException(status_code=500, detail=f"Database ingestion failed: {e}")


async def ingest_flows(request: Request):
    """
    POST endpoint to ingest daily flow summary data.
    Expects a JSON body that can be decoded into a list of DailyFlowInput structs.
    """
    try:
        body = await request.body()
        flows: List[DailyFlowInput] = msgpack.decode(body, type=List[DailyFlowInput])
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Validation Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload format: {e}")
    
    try:
        inserted_count = crud.ingest_daily_flow_inputs(flows)
        return JSONResponse(
            {"status": "success", "message": f"Successfully ingested {inserted_count} daily flow inputs (REPLACE used)."}, 
            status_code=201
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database ingestion failed: {e}")


async def get_factors(request: Request):
    """
    GET endpoint to retrieve all emission and conversion factors.
    """
    try:
        factors: List[Factor] = crud.get_all_factors()
        
        # 3. Serialization (from Python Structs back to the wire format)
        # Use msgspec's encoding for consistency and speed
        encoded_data = msgpack.encode(factors)

        # Starlette handles Content-Type for JSONResponse, but msgpack is a binary format.
        # Since we are using msgpack for encoding, we should return the raw binary data
        # with the appropriate Content-Type header. 
        # NOTE: For simple browser interaction, we'll stick to JSONResponse for now 
        # and rely on the default JSON encoder for standard types. 
        # If performance is critical, we'd use starlette.responses.Response(encoded_data, media_type="application/x-msgpack").

        ## Using standard JSONResponse for wide compatibility
        #return JSONResponse([f.__dict__ for f in factors])
        # Use asdict() for dataclasses instead of __dict__
        return JSONResponse([asdict(f) for f in factors])
        
    except Exception as e:
        print(f"\n--- FATAL HANDLER EXCEPTION ---\nError during get_factors: {e}\n-------------------------------\n")
        raise HTTPException(status_code=500, detail=f"Could not retrieve factors: {e}")


# --- API Routes ---
api_routes = [
    Route("/readings/ingest", endpoint=ingest_readings, methods=["POST"]),
    Route("/flows/ingest", endpoint=ingest_flows, methods=["POST"]),
    Route("/factors", endpoint=get_factors, methods=["GET"]),
]