# SOVD Natural Language Interface

Keyword-based natural language wrapper for SOVD (Service-Oriented Vehicle Diagnostics) HTTP API.

## Overview

This tool translates natural language queries into SOVD-compliant HTTP requests for vehicle diagnostics. It uses keyword extraction from the vehicle model for flexible, order-independent parsing.

## Features

- **Keyword-based parsing** - Word order doesn't matter
- **Vehicle model integration** - Dynamically extracts entities from vehicle structure
- **Fuzzy entity matching** - Handles typos and variations (v2x → V2X, camera → Camera)
- **Context-aware resolution** - Scopes app searches to components
- **Query validation** - Prevents invalid requests before sending
- **Read-only enforcement** - Blocks write/delete operations
- **Ambiguity handling** - Returns multiple endpoints when query is ambiguous

## Installation

```bash
# Create virtual environment
python -m venv sovd-env
source sovd-env/bin/activate  # Windows: sovd-env\Scripts\activate

# Install dependencies
pip install pyyaml

# Export vehicle model
python export_vehicle_model.py
```

## Quick Start

```bash
# Interactive mode
python sovd_demo.py demo

# With debug output
python sovd_demo.py demo --debug

# Batch testing
python sovd_demo.py batch
```

## Usage Examples

```python
from sovd_nlp_prototype import SOVDAssistant

assistant = SOVDAssistant()

# Simple queries
result = assistant.process_request("list all apps")
result = assistant.process_request("get v2x logs")
result = assistant.process_request("show camera data")

# Flexible word order
result = assistant.process_request("logs from v2x")
result = assistant.process_request("camera data show")

# Context-aware
result = assistant.process_request("list apps in v2x")
result = assistant.process_request("get v2x hids logs")

# Hierarchical
result = assistant.process_request("list components in adas")
result = assistant.process_request("list areas")
```

## Response Format

```python
{
    "success": True,
    "intent": "get_logs",
    "entities": {
        "component": "V2X",
        "component_info": {...}
    },
    "http_request": "GET https://vehicle/components/V2X/logs HTTP/1.1",
    "curl_command": "curl -X GET 'https://vehicle/components/V2X/logs'",
    "explanation": "This will retrieve logs from V2X"
}
```

## Architecture

### Vehicle Model Integration

Keywords are extracted from `vehicle_model_snapshot.json` at initialization:

- **Areas**: Communication, ADAS, Chassis + aliases (comms, nav, etc.)
- **Components**: V2X, Camera, GOLDBOX, etc. (from vehicle model)
- **Apps**: IDSReporter, NIDS_Suricata, etc. (from vehicle model)
- **Bulk data categories**: logs, alerts, rules, captures (from app bulk_data_map)

### Keyword-Based Parsing

Scans input for keywords regardless of word order:

```
Input: "v2x logs get"
  → action: get
  → component: V2X
  → data_type: logs
  → Intent: get_logs
```

### Context-Aware Resolution

If component is found but app isn't, searches within component's apps:

```
Input: "list v2x hids logs"
  → component: V2X found
  → "hids" not found globally
  → Search V2X apps: [IDSReporter, V2X_HIDS, SOVDServer]
  → Match: V2X_HIDS
```

## Supported Intents

- `list_apps` - List all applications
- `list_apps_on_component` - List apps on specific component
- `list_areas` - List vehicle areas/zones
- `list_components` - List all components
- `list_components_in_area` - List components in specific area
- `get_logs` - Get component-level logs
- `get_bulk_data` - Get app-level bulk data (logs, alerts, rules)
- `read_sensor_data` - Read component data
- `get_faults` - Get diagnostic fault codes
- `get_configurations` - Get app configurations
- `get_operations` - List available operations

## Configuration

Base URI can be set in `sovd_config.yaml` or programmatically:

```python
assistant = SOVDAssistant(base_uri="https://vehicle-ip:8080")
```

## Testing

```bash
# Test vehicle knowledge integration
python test_phase_0_1.py

# Test entity resolution
python test_phase_2.py

# Test dynamic keywords
python test_dynamic_keywords.py

# Test context-aware resolution
python test_context_aware.py
```

## Files

- `sovd_nlp_prototype.py` - Keyword-based NLP engine
- `sovd_nlp_regex_prototype.py` - Original regex-based engine (preserved)
- `vehicle_knowledge.py` - Vehicle model interface
- `vehicle_model_snapshot.json` - Vehicle structure (generated)
- `export_vehicle_model.py` - Export utility
- `sovd_demo.py` - Interactive demo
- `sovd_config.yaml` - Configuration file

## Security

- **Read-only**: All write/delete operations are rejected
- **Validation**: Queries validated against vehicle model before execution
- **No SQL injection**: Not applicable (REST API)
- **No command injection**: Pure data queries only

## Performance

- **Initialization**: ~15-20ms (loads vehicle model, builds keywords)
- **Query parsing**: ~2-3ms
- **Total per query**: ~17-23ms (acceptable for diagnostic tool)

## Limitations

- Ambiguous queries without context may fail (e.g., "get IDS logs" without component)
- Complex multi-clause queries not supported ("get logs from X but not Y")
- Multi-word entity names require component context ("hids" needs "v2x hids")

## Troubleshooting

### Query not recognized

Enable debug mode to see keyword extraction:

```bash
python sovd_demo.py demo --debug
```

### Ambiguous results

Provide more context:

```
Instead of: "get ids logs"
Try: "get v2x ids logs"
```

### Write operation rejected

All write/delete operations are blocked by design. This is a read-only diagnostic tool.

## License

[Your License]

## Authors

[Your Name/Team]