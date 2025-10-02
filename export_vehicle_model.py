#!/usr/bin/env python3
# export_vehicle_model.py

"""
Export vehicle model data to JSON snapshot for NLP wrapper.
This creates a standalone snapshot that the NLP system can use
without depending on the SOVD server.

Usage:
    python export_vehicle_model.py

Output:
    vehicle_model_snapshot.json
"""

import json
import sys
from pathlib import Path

def export_vehicle_model():
    """
    Export VEHICLE_DATA from vehicle_model.py to JSON file.
    Assumes vehicle_model.py is in the same directory or in sys.path.
    """
    try:
        from vehicle_model import VEHICLE_DATA
        
        snapshot = {
            "metadata": {
                "version": "1.0",
                "description": "Vehicle model snapshot for SOVD NLP wrapper",
                "exported_from": "vehicle_model.py"
            },
            "vehicle_data": VEHICLE_DATA
        }
        
        output_file = Path("vehicle_model_snapshot.json")
        with open(output_file, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"Successfully exported vehicle model to {output_file}")
        print(f"Areas: {len(VEHICLE_DATA['areas'])}")
        print(f"Components: {len(VEHICLE_DATA['components'])}")
        print(f"Apps: {len(VEHICLE_DATA['apps'])}")
        
        return True
        
    except ImportError as e:
        print(f"Error: Could not import vehicle_model.py: {e}")
        print("\nPlease ensure vehicle_model.py is in the current directory")
        print("or add its location to PYTHONPATH")
        return False
    
    except Exception as e:
        print(f"Error during export: {e}")
        return False

if __name__ == "__main__":
    success = export_vehicle_model()
    sys.exit(0 if success else 1)