# SOVD Natural Language Interface

Convert natural language requests to SOVD HTTP API calls with configurable patterns and active learning.

## Files

- `sovd_nlp_prototype.py` - Main NLP processing engine (now reads from config)
- `sovd_demo.py` - Interactive demo with learning capabilities  
- `sovd_config.py` - Configuration management and validation
- `sovd_config.yaml` - Configuration file with patterns and endpoints

## Installation

```bash
# Create virtual environment
python -m venv sovd-env
source sovd-env/bin/activate  # Windows: sovd-env\Scripts\activate

# Install dependencies
pip install pyyaml

# Create configuration with proper patterns
python sovd_config.py create

# Validate configuration
python sovd_config.py validate
```

## Configuration

The system now properly uses `sovd_config.yaml` for all patterns and settings:

```yaml
base_uri: "https://your-vehicle-server:8080"

intent_patterns:
  read_sensor_data:
    regex_patterns:
      - r"\b(read|get|show)\s+(sensor\s+)?data\s+(from\s+)?(?P<component>\w+)\b"
      - r"\bget\s+(?P<component>\w+)\s+(?P<datatype>temperature|temp|voltage|pressure)\b"
    entities:
      component: "component" 
      datatype: "datatype"

component_aliases:
  engine: ["motor", "powerplant", "powertrain"]
  sensor: ["temperature", "temp"]
```

## Usage

### Interactive Mode with Learning

```bash
python sovd_demo.py demo --debug
```

The system now:
- Reads patterns from config (no more hardcoded patterns)
- Learns from corrections automatically
- Only saves successful training data
- Shows detailed debug information

### Learning Example

```
Your request: get engine temperature
Debug: Processing input: 'get engine temperature'
Debug: Attempting to match 'get engine temperature' against 9 intent types
Debug: Pattern matched! Intent: read_sensor_data, Entities: {'component': 'engine', 'datatype': 'temperature'}
Intent: read_sensor_data
Entities: {'component': 'engine', 'datatype': 'temperature'}
HTTP Request: GET https://your-vehicle:8080/apps/engine/data/temperature?include-schema=true
Was this correct? (y/n/comment): y
```

### Active Learning from Corrections

```
Your request: check battery level
Error: Could not understand request
What should this request do? (intent [component=X datatype=Y] or skip): read_sensor_data component=battery datatype=voltage
Pattern learned! Try your request again.

Your request: check battery level
Intent: read_sensor_data
Entities: {'component': 'battery', 'datatype': 'voltage'}
```

## Command Line Options

```bash
python sovd_demo.py demo --debug          # Interactive with debug
python sovd_demo.py batch --config my.yaml # Batch testing
python sovd_demo.py export               # Export clean training data
```

## Pattern System

Patterns are now fully configurable in YAML:

```yaml
intent_patterns:
  read_sensor_data:
    regex_patterns:
      - r"\bget\s+(?P<component>\w+)\s+(?P<datatype>temperature|temp|voltage)\b"
    entities:
      component: "component"
      datatype: "datatype" 
    priority: 2
```

## Component Aliases

The system resolves aliases from config:

```yaml
component_aliases:
  engine: ["motor", "powerplant"]
  sensor: ["temperature", "temp"]
```

## Training Data

Now only saves successful cases with feedback:
- Failed parses are not saved (reduces noise)
- User corrections trigger immediate learning
- Clean ML training data in `sovd_ml_training_data.json`

## Troubleshooting

### Temperature/sensor requests failing

The new system includes proper patterns for sensor data:
```
"get engine temperature" ✓ (now works)  
"get ecu temp" ✓ (now works)
"show voltage from battery" ✓ (now works)
```

### Learning not working

Check debug output to see pattern generation:
```bash
python sovd_demo.py demo --debug
# Shows pattern matching and learning process
```

### Config validation

```bash
python sovd_config.py validate
# Now checks intent_patterns section
```

## Integration

```python
from sovd_nlp_prototype import SOVDAssistant

assistant = SOVDAssistant(config_file="my_config.yaml")
result = assistant.process_request("get engine temperature")

# For corrections:
assistant.learn_from_correction(
    "check battery level", 
    "read_sensor_data", 
    {"component": "battery", "datatype": "voltage"}
)
```
