import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class SOVDRequest:
    """Represents a SOVD HTTP request"""
    method: str
    endpoint: str
    params: Dict[str, str] = None
    headers: Dict[str, str] = None
    
    def to_http_request(self, base_uri: str = "https://vehicle.example.com") -> str:
        """Convert to HTTP request string"""
        url = f"{base_uri}{self.endpoint}"
        if self.params:
            param_str = "&".join([f"{k}={v}" for k, v in self.params.items()])
            url += f"?{param_str}"
        
        headers_str = ""
        if self.headers:
            headers_str = "\n".join([f"{k}: {v}" for k, v in self.headers.items()])
            headers_str = f"\n{headers_str}"
        
        return f"{self.method} {url} HTTP/1.1{headers_str}"

class IntentType(Enum):
    """Types of diagnostic intents"""
    LIST_APPS = "list_apps"
    GET_CAPABILITIES = "get_capabilities"
    READ_SENSOR_DATA = "read_sensor_data"
    GET_LOGS = "get_logs"
    GET_FAULTS = "get_faults"
    GET_ECU_STATUS = "get_ecu_status"
    GET_CONFIGURATIONS = "get_configurations"
    GET_OPERATIONS = "get_operations"
    SECURITY_ACCESS = "security_access"

@dataclass
class Intent:
    """Parsed user intent"""
    type: IntentType
    entities: Dict[str, str] = None

class SOVDNLPProcessor:
    """Natural Language Processor for SOVD API requests"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[IntentType, List[Dict]]:
        """Initialize pattern matching rules for intent classification"""
        return {
            IntentType.LIST_APPS: [
                {"pattern": r"\b(list|show|get)\s+(all\s+)?(apps|applications)\b", "entities": {}},
                {"pattern": r"\bwhat\s+apps\s+are\s+(available|running)\b", "entities": {}},
            ],
            
            IntentType.GET_CAPABILITIES: [
                {"pattern": r"\b(show|get|list)\s+capabilities\b", "entities": {}},
                {"pattern": r"\bwhat\s+can\s+(this\s+)?(vehicle|system)\s+do\b", "entities": {}},
            ],
            
            IntentType.READ_SENSOR_DATA: [
                {"pattern": r"\b(read|get|show)\s+(sensor\s+)?data\s+(from\s+)?(?P<component>\w+)\b", "entities": {"component": "component"}},
                {"pattern": r"\bget\s+(?P<component>\w+)\s+(sensor\s+)?data\b", "entities": {"component": "component"}},
                {"pattern": r"\bshow\s+(?P<datatype>\w+)\s+(from\s+)?(?P<component>\w+)\b", "entities": {"component": "component", "datatype": "datatype"}},
            ],
            
            IntentType.GET_LOGS: [
                {"pattern": r"\b(get|show|read|fetch)\s+(system\s+)?(logs|logging)\b", "entities": {}},
                {"pattern": r"\bshow\s+me\s+the\s+logs\b", "entities": {}},
                {"pattern": r"\b(get|read)\s+(?P<component>\w+)\s+logs\b", "entities": {"component": "component"}},
            ],
            
            IntentType.GET_FAULTS: [
                {"pattern": r"\b(get|show|read|list)\s+(all\s+)?(faults|errors|DTCs?|trouble\s+codes?)\b", "entities": {}},
                {"pattern": r"\bcheck\s+for\s+(faults|errors)\b", "entities": {}},
                {"pattern": r"\bdiagnostic\s+trouble\s+codes?\b", "entities": {}},
            ],
            
            IntentType.GET_ECU_STATUS: [
                {"pattern": r"\b(get|check|show)\s+(ecu|ECU)\s+(status|health|info)\b", "entities": {}},
                {"pattern": r"\bshow\s+(?P<ecu>\w+)\s+(ecu\s+)?status\b", "entities": {"ecu": "ecu"}},
                {"pattern": r"\bhow\s+is\s+the\s+(?P<ecu>\w+)\s+(ecu\s+)?doing\b", "entities": {"ecu": "ecu"}},
            ],
            
            IntentType.GET_CONFIGURATIONS: [
                {"pattern": r"\b(get|show)\s+(?P<app>\w+)\s+config(uration)?s?\b", "entities": {"app": "app"}},
                {"pattern": r"\bshow\s+settings\s+for\s+(?P<app>\w+)\b", "entities": {"app": "app"}},
            ],
            
            IntentType.GET_OPERATIONS: [
                {"pattern": r"\b(get|list|show)\s+(?P<component>\w+)\s+operations\b", "entities": {"component": "component"}},
                {"pattern": r"\bwhat\s+can\s+(?P<component>\w+)\s+do\b", "entities": {"component": "component"}},
            ],
            
            IntentType.SECURITY_ACCESS: [
                {"pattern": r"\b(security\s+access|authenticate|login)\b", "entities": {}},
                {"pattern": r"\bget\s+access\s+to\s+(?P<component>\w+)\b", "entities": {"component": "component"}},
            ],
        }
    
    def parse_natural_language(self, text: str) -> Optional[Intent]:
        """Parse natural language input and extract intent and entities"""
        text = text.lower().strip()
        
        for intent_type, pattern_list in self.patterns.items():
            for pattern_dict in pattern_list:
                try:
                    match = re.search(pattern_dict["pattern"], text, re.IGNORECASE)
                    if match:
                        entities = {}
                        # Extract named groups from regex
                        for entity_name, group_name in pattern_dict["entities"].items():
                            if group_name in match.groupdict() and match.group(group_name):
                                entities[entity_name] = match.group(group_name)
                        
                        return Intent(type=intent_type, entities=entities)
                except Exception as e:
                    print(f"Error processing pattern: {e}")
                    continue
        
        return None
    
    def intent_to_sovd_request(self, intent: Intent) -> SOVDRequest:
        """Convert parsed intent to SOVD HTTP request"""
        
        if intent.type == IntentType.LIST_APPS:
            return SOVDRequest(method="GET", endpoint="/apps")
        
        elif intent.type == IntentType.GET_CAPABILITIES:
            return SOVDRequest(method="GET", endpoint="/capabilities")
        
        elif intent.type == IntentType.READ_SENSOR_DATA:
            component = intent.entities.get("component", "DefaultComponent")
            datatype = intent.entities.get("datatype", "data")
            endpoint = f"/apps/{component}/data/{datatype}"
            params = {"include-schema": "true"}
            return SOVDRequest(method="GET", endpoint=endpoint, params=params)
        
        elif intent.type == IntentType.GET_LOGS:
            component = intent.entities.get("component", "System")
            endpoint = f"/components/{component}/logs"
            return SOVDRequest(method="GET", endpoint=endpoint)
        
        elif intent.type == IntentType.GET_FAULTS:
            return SOVDRequest(method="GET", endpoint="/components/diagnostics/faults")
        
        elif intent.type == IntentType.GET_ECU_STATUS:
            ecu = intent.entities.get("ecu", "Engine")
            endpoint = f"/components/{ecu}/status"
            return SOVDRequest(method="GET", endpoint=endpoint)
        
        elif intent.type == IntentType.GET_CONFIGURATIONS:
            app = intent.entities.get("app", "DefaultApp")
            endpoint = f"/apps/{app}/configurations"
            return SOVDRequest(method="GET", endpoint=endpoint)
        
        elif intent.type == IntentType.GET_OPERATIONS:
            component = intent.entities.get("component", "DefaultComponent")
            endpoint = f"/components/{component}/operations"
            return SOVDRequest(method="GET", endpoint=endpoint)
        
        elif intent.type == IntentType.SECURITY_ACCESS:
            component = intent.entities.get("component", "")
            if component:
                endpoint = f"/components/{component}/security/access"
            else:
                endpoint = "/security/access"
            return SOVDRequest(method="POST", endpoint=endpoint)
        
        else:
            # Fallback - try to get general info
            return SOVDRequest(method="GET", endpoint="/capabilities")

class SOVDAssistant:
    """Main assistant class that combines NLP processing with SOVD API generation"""
    
    def __init__(self, base_uri: str = None, config_file: str = None):
        self.nlp_processor = SOVDNLPProcessor()
        self.conversation_log = []
        
        # Load base_uri from config if available
        if config_file or base_uri is None:
            try:
                import yaml
                from pathlib import Path
                
                config_path = Path(config_file or "sovd_config.yaml")
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                        self.base_uri = base_uri or config.get("base_uri", "https://vehicle.example.com")
                else:
                    self.base_uri = base_uri or "https://vehicle.example.com"
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
                self.base_uri = base_uri or "https://vehicle.example.com"
        else:
            self.base_uri = base_uri
    
    def process_request(self, user_input: str, debug: bool = False) -> Dict:
        """Process natural language input and return SOVD request details"""
        
        if debug:
            print(f"Debug: Processing input: '{user_input}'")
        
        # Parse the intent
        intent = self.nlp_processor.parse_natural_language(user_input)
        
        if not intent:
            return {
                "success": False,
                "message": "Could not understand request. Try asking about apps, capabilities, sensor data, logs, faults, or ECU status.",
                "suggestions": [
                    "List all apps",
                    "Show capabilities", 
                    "Get engine sensor data",
                    "Read system logs",
                    "Check for faults",
                    "Get ECU status"
                ]
            }
        
        if debug:
            print(f"Debug: Detected intent: {intent.type.value}, entities: {intent.entities}")
        
        # Convert to SOVD request
        sovd_request = self.nlp_processor.intent_to_sovd_request(intent)
        
        # Generate HTTP request string
        http_request = sovd_request.to_http_request(self.base_uri)
        
        # Log the conversation
        self.conversation_log.append({
            "input": user_input,
            "intent": intent.type.value,
            "entities": intent.entities,
            "request": http_request
        })
        
        return {
            "success": True,
            "intent": intent.type.value,
            "entities": intent.entities,
            "http_request": http_request,
            "curl_command": self._generate_curl_command(sovd_request),
            "explanation": self._explain_request(intent, sovd_request)
        }
    
    def _generate_curl_command(self, request: SOVDRequest) -> str:
        """Generate curl command for the request"""
        url = f"{self.base_uri}{request.endpoint}"
        if request.params:
            param_str = "&".join([f"{k}={v}" for k, v in request.params.items()])
            url += f"?{param_str}"
        
        curl_cmd = f"curl -X {request.method} '{url}'"
        
        if request.headers:
            for key, value in request.headers.items():
                curl_cmd += f" -H '{key}: {value}'"
        
        return curl_cmd
    
    def _explain_request(self, intent: Intent, request: SOVDRequest) -> str:
        """Provide human-readable explanation of the generated request"""
        explanations = {
            IntentType.LIST_APPS: "This will list all available applications in the vehicle",
            IntentType.GET_CAPABILITIES: "This will show what diagnostic capabilities are available",
            IntentType.READ_SENSOR_DATA: f"This will read sensor data from {intent.entities.get('component', 'the specified component')}",
            IntentType.GET_LOGS: f"This will retrieve logs from {intent.entities.get('component', 'the system')}",
            IntentType.GET_FAULTS: "This will get all diagnostic trouble codes and fault information",
            IntentType.GET_ECU_STATUS: f"This will check the status of {intent.entities.get('ecu', 'the ECU')}",
            IntentType.GET_CONFIGURATIONS: f"This will get configuration settings for {intent.entities.get('app', 'the application')}",
            IntentType.GET_OPERATIONS: f"This will list available operations for {intent.entities.get('component', 'the component')}",
            IntentType.SECURITY_ACCESS: "This will initiate security access procedure",
        }
        
        return explanations.get(intent.type, "This will perform the requested diagnostic operation")

# Example usage and testing
if __name__ == "__main__":
    assistant = SOVDAssistant()
    
    # Test cases
    test_inputs = [
        "List all apps",
        "Show me the capabilities", 
        "Get engine sensor data",
        "Read PowerSteering logs",
        "Check for faults",
        "Get Engine ECU status",
        "Show AdvancedLaneKeeping configurations",
        "List PowerSteering operations",
        "I need security access to the engine",
        "What can this vehicle do?",
        "Show me RearWindows data",
    ]
    
    print("SOVD Natural Language to HTTP Request Processor")
    print("=" * 50)
    
    for test_input in test_inputs:
        print(f"\nInput: '{test_input}'")
        result = assistant.process_request(test_input)
        
        if result["success"]:
            print(f"Intent: {result['intent']}")
            if result["entities"]:
                print(f"Entities: {result['entities']}")
            print(f"HTTP Request:\n{result['http_request']}")
            print(f"cURL: {result['curl_command']}")
            print(f"Explanation: {result['explanation']}")
        else:
            print(f"Error: {result['message']}")
        
        print("-" * 30)