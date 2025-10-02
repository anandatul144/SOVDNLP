"""
Vehicle data model - defines the complete vehicle structure for SOVD server
"""
import os

# Base path to mock filesystems

MOCK_FS_BASE = os.path.join(os.path.dirname(__file__), "mock_filesystems") #simlink to the FS
#MOCK_FS_BASE = os.path.join(os.path.dirname(__file__), "../../../Target-mock-FS") 
VEHICLE_DATA = {
    "areas": {
        "Communication": {
            "id": "Communication",
            "name": "Communication Zone",
            "components": ["V2X", "Switch", "ECU1", "ECU2", "Ubuntu"]
        },
        "ADAS": {
            "id": "ADAS",
            "name": "ADAS/Navigation Zone",
            "components": ["Camera", "LIDAR", "GOLDBOX", "Switch", "MAB"]
        },
        "Chassis": {
            "id": "Chassis",
            "name": "Base/Chassis Zone",
            "components": ["Wheels", "Brakes", "Accelerator", "Gearbox", "MAB"]
        }
    },
    
    "components": {
        "V2X": {
            "id": "V2X",
            "name": "V2X Communication Gateway",
            "areas": ["Communication"],
            "architecture": "posix",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "posix_comms/v2x"),
            "apps": ["IDSReporter", "V2X_HIDS", "SOVDServer"],
            "role": "external_gateway",
            "identData": {
                "PartNumber": "V2X-2024-GW",
                "SoftwareVersion": "v2.1.0",
                "OS": "Ubuntu 22.04"
            },
            "currentData": {
                "CPULoad": 35,
                "Temperature": 52,
                "NetworkThroughput": 1250  # Mbps
            }
        },
        
        "Switch": {
            "id": "Switch",
            "name": "Network Switch",
            "areas": ["Communication", "ADAS"],
            "architecture": "posix",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "posix_comms/switch"),
            "apps": ["NIDS_Suricata", "Switch_IDS"],
            "role": "zone_gateway",
            "identData": {
                "PartNumber": "SW-2024-8PORT",
                "SoftwareVersion": "v1.5.2",
                "OS": "Linux Embedded"
            },
            "currentData": {
                "PortsActive": 6,
                "PacketsPerSecond": 125000,
                "Temperature": 48
            }
        },
        
        "ECU1": {
            "id": "ECU1",
            "name": "Communication ECU 1",
            "areas": ["Communication"],
            "architecture": "posix",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "posix_comms/ecu1"),
            "apps": [],
            "identData": {"PartNumber": "ECU1-2024"},
            "currentData": {"Status": "active"}
        },
        
        "ECU2": {
            "id": "ECU2",
            "name": "Communication ECU 2",
            "areas": ["Communication"],
            "architecture": "posix",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "posix_comms/ecu2"),
            "apps": [],
            "identData": {"PartNumber": "ECU2-2024"},
            "currentData": {"Status": "active"}
        },
        
        "Ubuntu": {
            "id": "Ubuntu",
            "name": "Ubuntu Telematics Unit",
            "areas": ["Communication"],
            "architecture": "posix",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "posix_comms/ubuntu"),
            "apps": ["Telematics"],
            "identData": {"OS": "Ubuntu 22.04"},
            "currentData": {"Status": "active"}
        },
        
        "Camera": {
            "id": "Camera",
            "name": "Front Camera Unit",
            "areas": ["ADAS"],
            "architecture": "adas_linux",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "adas_linux/camera"),
            "apps": ["Perception"],
            "identData": {
                "PartNumber": "CAM-2024-FWD",
                "SoftwareVersion": "v5.3.2",
                "Resolution": "1920x1080"
            },
            "currentData": {
                "FPS": 60,
                "ObjectsDetected": 5,
                "OperatingTemp": 42
            }
        },
        
        "LIDAR": {
            "id": "LIDAR",
            "name": "3D LIDAR Scanner",
            "areas": ["ADAS"],
            "architecture": "adas_linux",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "adas_linux/lidar"),
            "apps": ["LIDARDriver"],
            "identData": {
                "PartNumber": "LIDAR-VLS-128",
                "Manufacturer": "Velodyne"
            },
            "currentData": {
                "PointsPerSecond": 2400000,
                "RangeMax": 200
            }
        },
        
        "GOLDBOX": {
            "id": "GOLDBOX",
            "name": "Central ADAS Processing Unit",
            "areas": ["ADAS"],
            "architecture": "adas_linux",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "adas_linux/goldbox"),
            "apps": ["IDSManager", "HIDS_OSSEC", "ADAFusion", "GOLDBOX_IDS"],
            "role": "central_compute",
            "identData": {
                "PartNumber": "GOLDBOX-ORIN",
                "Processor": "NVIDIA Drive AGX Orin",
                "AI_TOPS": "254"
            },
            "currentData": {
                "GPUUtil": 78,
                "CPUTemp": 65,
                "PowerDraw": 120
            }
        },
        
        "MAB": {
            "id": "MAB",
            "name": "Multi-Function Actuator Box",
            "areas": ["ADAS", "Chassis"],
            "architecture": "autosar_adaptive",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "autosar_adaptive/mab"),
            "apps": ["CANIDS", "ActuatorControl"],
            "role": "zone_gateway",
            "identData": {
                "PartNumber": "MAB-2024-001",
                "AUTOSAR_Version": "Adaptive R22-11"
            },
            "currentData": {
                "SteeringTorque": 12.5,
                "BrakePressure": 850,
                "ActuatorTemp": 68
            }
        },
        
        "Brakes": {
            "id": "Brakes",
            "name": "Brake Control Module",
            "areas": ["Chassis"],
            "architecture": "autosar_classic",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "autosar_classic/brakes"),
            "apps": [],
            "identData": {
                "PartNumber": "BRK-2024-ABS",
                "AUTOSAR_Version": "4.2.2"
            },
            "currentData": {
                "FrontLeftPressure": 850,
                "FrontRightPressure": 845,
                "ABSActive": False
            }
        },
        
        "Wheels": {
            "id": "Wheels",
            "name": "Wheel Control Module",
            "areas": ["Chassis"],
            "architecture": "autosar_classic",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "autosar_classic/wheels"),
            "apps": [],
            "identData": {"PartNumber": "WHL-2024"},
            "currentData": {"RPM": 850}
        },
        
        "Accelerator": {
            "id": "Accelerator",
            "name": "Accelerator Pedal Module",
            "areas": ["Chassis"],
            "architecture": "autosar_classic",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "autosar_classic/accelerator"),
            "apps": [],
            "identData": {"PartNumber": "ACCEL-2024"},
            "currentData": {"Position": 25}
        },
        
        "Gearbox": {
            "id": "Gearbox",
            "name": "Gearbox Control Unit",
            "areas": ["Chassis"],
            "architecture": "autosar_classic",
            "filesystem_root": os.path.join(MOCK_FS_BASE, "autosar_classic/gearbox"),
            "apps": [],
            "identData": {"PartNumber": "GEAR-2024"},
            "currentData": {"CurrentGear": 4}
        }
    },
    
    "apps": {
        "IDSReporter": {
            "id": "IDSReporter",
            "name": "IDS Alert Reporter",
            "component": "V2X",
            "data": {
                "alertCount": 47,
                "lastAlertTime": "2024-10-01T15:32:12Z",
                "reporterStatus": "active"
            },
            "bulk_data_map": {
                "ids_alerts": "opt/ids_reporter/alerts",
                "reporter_logs": "opt/ids_reporter/logs",
                "config": "opt/ids_reporter/config"
            },
            "operations": ["ClearAlerts", "RestartReporter"]
        },
        
        "V2X_HIDS": {
            "id": "V2X_HIDS",
            "name": "V2X Host IDS",
            "component": "V2X",
            "data": {
                "filesMonitored": 342,
                "integrityViolations": 0
            },
            "bulk_data_map": {
                "hids_rules": "opt/ids_hids/rules",
                "hids_alerts": "opt/ids_hids/alerts"
            },
            "operations": ["RunIntegrityScan"]
        },
        
        "SOVDServer": {
            "id": "SOVDServer",
            "name": "SOVD Server",
            "component": "V2X",
            "data": {
                "activeConnections": 2,
                "requestsPerMinute": 15
            },
            "bulk_data_map": {
                "config": "opt/sovd_server/config",
                "logs": "opt/sovd_server/logs"
            },
            "operations": ["ReloadConfig"]
        },
        
        "NIDS_Suricata": {
            "id": "NIDS_Suricata",
            "name": "Network IDS (Suricata)",
            "component": "Switch",
            "data": {
                "packetsProcessed": 5847293,
                "alertsGenerated": 89,
                "droppedPackets": 12,
                "rulesetVersion": "6.0.14"
            },
            "bulk_data_map": {
                "suricata_rules": "opt/suricata/rules",
                "eve_logs": "opt/suricata/logs",
                "pcap_captures": "opt/suricata/captures"
            },
            "operations": ["ReloadRules", "StartCapture", "StopCapture"]
        },
        
        "Switch_IDS": {
            "id": "Switch_IDS",
            "name": "Switch Gateway IDS",
            "component": "Switch",
            "data": {
                "alertCount": 12
            },
            "bulk_data_map": {
                "ids_rules": "opt/ids_nids/rules",
                "ids_alerts": "opt/ids_nids/alerts"
            },
            "operations": []
        },
        
        "IDSManager": {
            "id": "IDSManager",
            "name": "Central IDS Manager",
            "component": "GOLDBOX",
            "data": {
                "totalAlertsReceived": 234,
                "correlatedIncidents": 12,
                "threatLevel": "medium"
            },
            "bulk_data_map": {
                "correlation_rules": "opt/ids_manager/correlation_rules",
                "incidents": "opt/ids_manager/incidents",
                "manager_logs": "opt/ids_manager/logs"
            },
            "operations": ["ReloadRules", "GenerateReport", "ClearIncidents"]
        },
        
        "HIDS_OSSEC": {
            "id": "HIDS_OSSEC",
            "name": "OSSEC Host IDS",
            "component": "GOLDBOX",
            "data": {
                "filesMonitored": 1247,
                "integrityViolations": 2,
                "lastScanTime": "2024-10-01T14:30:00Z"
            },
            "bulk_data_map": {
                "ossec_rules": "opt/ossec/rules",
                "ossec_alerts": "opt/ossec/logs/alerts",
                "file_integrity": "opt/ossec/syscheck"
            },
            "operations": ["RunIntegrityScan"]
        },
        
        "ADAFusion": {
            "id": "ADAFusion",
            "name": "ADAS Sensor Fusion",
            "component": "GOLDBOX",
            "data": {
                "sensorsActive": 8,
                "fusionRate": "10Hz"
            },
            "bulk_data_map": {
                "maps": "opt/adas_fusion/maps",
                "fusion_logs": "opt/adas_fusion/logs"
            },
            "operations": []
        },
        
        "GOLDBOX_IDS": {
            "id": "GOLDBOX_IDS",
            "name": "GOLDBOX Gateway IDS",
            "component": "GOLDBOX",
            "data": {
                "alertCount": 5
            },
            "bulk_data_map": {
                "hids_alerts": "opt/ids_hids_goldbox/alerts"
            },
            "operations": []
        },
        
        "CANIDS": {
            "id": "CANIDS",
            "name": "CAN Bus IDS",
            "component": "MAB",
            "data": {
                "canFramesAnalyzed": 982374,
                "anomaliesDetected": 3,
                "busLoadPercent": 42,
                "lastAnomalyTime": "2024-10-01T14:22:08Z"
            },
            "bulk_data_map": {
                "can_rules": "opt/canids/rules",
                "anomaly_logs": "opt/canids/logs",
                "can_captures": "opt/canids/captures"
            },
            "operations": ["UpdateWhitelist", "StartCANCapture"]
        },
        
        "ActuatorControl": {
            "id": "ActuatorControl",
            "name": "Actuator Control Service",
            "component": "MAB",
            "data": {
                "actuatorsActive": 8,
                "commandRate": "100Hz"
            },
            "bulk_data_map": {
                "config": "opt/actuator_control/config",
                "logs": "opt/actuator_control/logs"
            },
            "operations": []
        },
        
        "Perception": {
            "id": "Perception",
            "name": "Camera Perception",
            "component": "Camera",
            "data": {
                "objectsDetected": 5,
                "processingLatency": 12
            },
            "bulk_data_map": {
                "models": "opt/perception/models",
                "calibration": "opt/perception/calibration",
                "logs": "opt/perception/logs"
            },
            "operations": []
        },
        
        "LIDARDriver": {
            "id": "LIDARDriver",
            "name": "LIDAR Driver",
            "component": "LIDAR",
            "data": {
                "pointCloudRate": "10Hz"
            },
            "bulk_data_map": {
                "calibration": "opt/lidar_driver/calibration",
                "recordings": "opt/lidar_driver/recordings",
                "logs": "opt/lidar_driver/logs"
            },
            "operations": []
        },
        
        "Telematics": {
            "id": "Telematics",
            "name": "Telematics Service",
            "component": "Ubuntu",
            "data": {
                "connectionStatus": "connected",
                "dataRate": "50kbps"
            },
            "bulk_data_map": {
                "config": "opt/telematics/config",
                "logs": "opt/telematics/logs"
            },
            "operations": []
        }
    }
}

# Helper functions
def get_component(component_id):
    """Get component by ID"""
    return VEHICLE_DATA["components"].get(component_id)

def get_app(app_id):
    """Get app by ID"""
    return VEHICLE_DATA["apps"].get(app_id)

def get_area(area_id):
    """Get area by ID"""
    return VEHICLE_DATA["areas"].get(area_id)

def get_apps_for_component(component_id):
    """Get all apps running on a component"""
    return [app for app in VEHICLE_DATA["apps"].values() if app["component"] == component_id]

def get_components_in_area(area_id):
    """Get all components in an area"""
    area = VEHICLE_DATA["areas"].get(area_id)
    if not area:
        return []
    return [get_component(comp_id) for comp_id in area["components"]]
