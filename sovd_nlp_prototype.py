# sovd_nlp_prototype.py
# Keyword-based NLP processor - simpler, more maintainable
#!/usr/bin/env python3

import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from vehicle_knowledge import VehicleKnowledge
    VEHICLE_KNOWLEDGE_AVAILABLE = True
except ImportError:
    VEHICLE_KNOWLEDGE_AVAILABLE = False
    print("Warning: vehicle_knowledge module not available. Entity resolution disabled.")


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
    """
    Keyword-based Natural Language Processor for SOVD API requests.
    Scans for keywords regardless of word order for simpler, more flexible parsing.
    """
    
    def __init__(self, vehicle_knowledge: Optional['VehicleKnowledge'] = None):
        """
        Initialize NLP processor.
        
        Args:
            vehicle_knowledge: Optional VehicleKnowledge instance for entity resolution.
        """
        # Initialize vehicle knowledge
        if vehicle_knowledge is not None:
            self.vehicle_knowledge = vehicle_knowledge
        elif VEHICLE_KNOWLEDGE_AVAILABLE:
            try:
                self.vehicle_knowledge = VehicleKnowledge()
            except FileNotFoundError:
                print("Warning: vehicle_model_snapshot.json not found. Entity resolution disabled.")
                self.vehicle_knowledge = None
        else:
            self.vehicle_knowledge = None
        
        # Define keyword categories
        self._initialize_keywords()
    
    def _initialize_keywords(self):
        """Initialize keyword categories for parsing"""
        
        # Action verbs
        self.action_verbs = {
            "get": "get",
            "show": "get",
            "list": "list",
            "read": "get",
            "fetch": "get",
            "retrieve": "get",
            "display": "get",
            "check": "get",
        }
        
        # Data types (what to retrieve)
        self.data_types = {
            "logs": "logs",
            "log": "logs",
            "logging": "logs",
            "data": "data",
            "sensor": "data",
            "status": "status",
            "config": "configurations",
            "configuration": "configurations",
            "configurations": "configurations",
            "settings": "configurations",
            "operations": "operations",
            "operation": "operations",
            "faults": "faults",
            "fault": "faults",
            "errors": "faults",
            "error": "faults",
            "dtc": "faults",
            "dtcs": "faults",
            "codes": "faults",
            "capabilities": "capabilities",
            "capability": "capabilities",
            "apps": "apps",
            "applications": "apps",
            "application": "apps",
            "bulk-data": "bulk_data",
            "bulk": "bulk_data",
            "alerts": "bulk_data",
            "alert": "bulk_data",
            "rules": "bulk_data",
        }
        
        # Special keywords
        self.special_keywords = {
            "security": "security_access",
            "access": "security_access",
            "authenticate": "security_access",
            "login": "security_access",
        }
        
        # Ignore words (stop words)
        self.ignore_words = {
            "the", "a", "an", "from", "to", "in", "on", "at", "for",
            "me", "please", "i", "need", "want", "can", "you", "my",
            "all", "any", "some", "this", "that", "these", "those"
        }
    
    def parse_natural_language(self, text: str, debug: bool = False) -> Optional[Intent]:
        """
        Parse natural language using keyword scanning.
        Word order doesn't matter - scans for keywords in any position.
        
        Args:
            text: User input text
            debug: Enable debug output
        
        Returns:
            Intent with extracted entities, or None if unable to parse
        """
        text_lower = text.lower().strip()
        tokens = text_lower.split()
        
        if debug:
            print(f"Debug: Parsing '{text}'")
            print(f"Debug: Tokens: {tokens}")
        
        # Extract keywords
        parsed = {
            "action": None,
            "data_type": None,
            "component": None,
            "app": None,
            "area": None,
            "ecu": None,
            "special": None,
        }
        
        # Scan for action verb
        for token in tokens:
            if token in self.action_verbs:
                parsed["action"] = self.action_verbs[token]
                if debug:
                    print(f"Debug: Found action: {token} → {parsed['action']}")
                break
        
        # Scan for data type
        for token in tokens:
            if token in self.data_types:
                parsed["data_type"] = self.data_types[token]
                if debug:
                    print(f"Debug: Found data_type: {token} → {parsed['data_type']}")
                break
        
        # Scan for special keywords
        for token in tokens:
            if token in self.special_keywords:
                parsed["special"] = self.special_keywords[token]
                if debug:
                    print(f"Debug: Found special: {token} → {parsed['special']}")
                break
        
        # Scan for entities using vehicle knowledge
        if self.vehicle_knowledge:
            for token in tokens:
                if token in self.ignore_words:
                    continue
                
                # Try to find component
                if parsed["component"] is None:
                    component = self.vehicle_knowledge.find_component(token)
                    if component:
                        parsed["component"] = component["id"]
                        parsed["component_info"] = component
                        if debug:
                            print(f"Debug: Found component: {token} → {component['id']}")
                        continue
                
                # Try to find app
                if parsed["app"] is None:
                    app = self.vehicle_knowledge.find_app(token)
                    if app:
                        parsed["app"] = app["id"]
                        parsed["app_info"] = app
                        if debug:
                            print(f"Debug: Found app: {token} → {app['id']}")
                        continue
                
                # Try to find area
                if parsed["area"] is None:
                    area = self.vehicle_knowledge.find_area(token)
                    if area:
                        parsed["area"] = area["id"]
                        parsed["area_info"] = area
                        if debug:
                            print(f"Debug: Found area: {token} → {area['id']}")
                        continue
        
        if debug:
            print(f"Debug: Parsed keywords: {parsed}")
        
        # Determine intent from extracted keywords
        intent = self._classify_intent(parsed, debug)
        
        if debug and intent:
            print(f"Debug: Classified intent: {intent.type.value}, entities: {intent.entities}")
        
        return intent
    
    def _classify_intent(self, parsed: Dict, debug: bool = False) -> Optional[Intent]:
        """
        Classify intent based on extracted keywords.
        
        Args:
            parsed: Dictionary of extracted keywords
            debug: Enable debug output
        
        Returns:
            Intent object or None
        """
        
        # Special case: security access
        if parsed["special"] == "security_access":
            entities = {}
            if parsed["component"]:
                entities["component"] = parsed["component"]
                if "component_info" in parsed:
                    entities["component_info"] = parsed["component_info"]
            return Intent(type=IntentType.SECURITY_ACCESS, entities=entities)
        
        # Special case: capabilities
        if parsed["data_type"] == "capabilities":
            return Intent(type=IntentType.GET_CAPABILITIES, entities={})
        
        # Special case: list apps
        if parsed["action"] == "list" and parsed["data_type"] == "apps":
            return Intent(type=IntentType.LIST_APPS, entities={})
        if parsed["data_type"] == "apps" and not parsed["component"]:
            return Intent(type=IntentType.LIST_APPS, entities={})
        
        # Get logs
        if parsed["data_type"] == "logs":
            entities = {}
            if parsed["component"]:
                entities["component"] = parsed["component"]
                if "component_info" in parsed:
                    entities["component_info"] = parsed["component_info"]
                    entities["component_type"] = "component"
            if parsed["area"]:
                entities["area"] = parsed["area"]
            return Intent(type=IntentType.GET_LOGS, entities=entities)
        
        # Get faults/errors
        if parsed["data_type"] == "faults":
            return Intent(type=IntentType.GET_FAULTS, entities={})
        
        # Get configurations
        if parsed["data_type"] == "configurations":
            entities = {}
            if parsed["app"]:
                entities["app"] = parsed["app"]
                if "app_info" in parsed:
                    entities["app_info"] = parsed["app_info"]
            elif parsed["component"]:
                entities["app"] = parsed["component"]
            return Intent(type=IntentType.GET_CONFIGURATIONS, entities=entities)
        
        # Get operations
        if parsed["data_type"] == "operations":
            entities = {}
            if parsed["component"]:
                entities["component"] = parsed["component"]
                if "component_info" in parsed:
                    entities["component_info"] = parsed["component_info"]
            return Intent(type=IntentType.GET_OPERATIONS, entities=entities)
        
        # Get status
        if parsed["data_type"] == "status":
            entities = {}
            if parsed["component"]:
                entities["ecu"] = parsed["component"]
                if "component_info" in parsed:
                    entities["ecu_info"] = parsed["component_info"]
            return Intent(type=IntentType.GET_ECU_STATUS, entities=entities)
        
        # Get data (sensor data)
        if parsed["data_type"] == "data":
            entities = {}
            if parsed["component"]:
                entities["component"] = parsed["component"]
                if "component_info" in parsed:
                    entities["component_info"] = parsed["component_info"]
                    entities["component_type"] = "component"
            return Intent(type=IntentType.READ_SENSOR_DATA, entities=entities)
        
        # Get bulk data
        if parsed["data_type"] == "bulk_data":
            entities = {}
            if parsed["app"]:
                entities["app"] = parsed["app"]
                if "app_info" in parsed:
                    entities["app_info"] = parsed["app_info"]
            return Intent(type=IntentType.READ_SENSOR_DATA, entities=entities)
        
        # Fallback: if we have component but no data type, assume data
        if parsed["component"] and not parsed["data_type"]:
            entities = {
                "component": parsed["component"]
            }
            if "component_info" in parsed:
                entities["component_info"] = parsed["component_info"]
                entities["component_type"] = "component"
            return Intent(type=IntentType.READ_SENSOR_DATA, entities=entities)
        
        # Could not determine intent
        if debug:
            print("Debug: Could not classify intent from keywords")
        
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
            return SOVDRequest(method="GET", endpoint="/capabilities")


class SOVDAssistant:
    """
    Main assistant class - IDENTICAL API to regex version.
    Drop-in replacement, no external changes needed.
    """
    
    def __init__(self, base_uri: str = None, config_file: str = None, vehicle_knowledge: Optional['VehicleKnowledge'] = None):
        """Initialize SOVD Assistant with keyword-based NLP"""
        self.nlp_processor = SOVDNLPProcessor(vehicle_knowledge=vehicle_knowledge)
        self.conversation_log = []
        
        # Load base_uri from config
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
        """
        Process natural language input - IDENTICAL API to regex version.
        
        Args:
            user_input: Natural language query
            debug: Enable debug output
        
        Returns:
            Dict with success, intent, entities, http_request, etc.
        """
        
        if debug:
            print(f"Debug: Processing input: '{user_input}'")
        
        # Parse intent using keyword-based approach
        intent = self.nlp_processor.parse_natural_language(user_input, debug=debug)
        
        if not intent:
            suggestions = self._generate_smart_suggestions(user_input)
            
            return {
                "success": False,
                "message": "Could not understand request.",
                "suggestions": suggestions
            }
        
        # Validate query
        if self.nlp_processor.vehicle_knowledge:
            is_valid, validation_msg = self._validate_query(intent)
            if not is_valid:
                return {
                    "success": False,
                    "message": f"Query validation failed: {validation_msg}",
                    "suggestions": self._generate_alternative_suggestions(intent)
                }
        
        if debug:
            print(f"Debug: Final intent: {intent.type.value}, entities: {intent.entities}")
        
        # Convert to SOVD request
        sovd_request = self.nlp_processor.intent_to_sovd_request(intent)
        http_request = sovd_request.to_http_request(self.base_uri)
        
        # Log conversation
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
    
    def _validate_query(self, intent: Intent) -> Tuple[bool, str]:
        """Validate query using vehicle knowledge"""
        if not self.nlp_processor.vehicle_knowledge:
            return True, ""
        
        return self.nlp_processor.vehicle_knowledge.validate_query(
            intent.type.value,
            intent.entities
        )
    
    def _generate_smart_suggestions(self, user_input: str) -> List[str]:
        """Generate vehicle-aware suggestions"""
        suggestions = []
        
        if self.nlp_processor.vehicle_knowledge:
            words = user_input.lower().split()
            
            for word in words:
                if len(word) > 2:
                    similar = self.nlp_processor.vehicle_knowledge.suggest_similar(word, limit=2)
                    if similar:
                        suggestions.append(f"Did you mean: {', '.join(similar)}?")
                        break
        
        suggestions.extend([
            "List all apps",
            "Show capabilities",
            "Get V2X logs",
            "Show Camera data",
            "Check for faults"
        ])
        
        return suggestions[:5]
    
    def _generate_alternative_suggestions(self, intent: Intent) -> List[str]:
        """Suggest alternatives when validation fails"""
        suggestions = []
        
        if intent.type == IntentType.GET_LOGS:
            suggestions.append("Try components with logs: V2X, GOLDBOX, Switch")
        elif intent.type == IntentType.GET_OPERATIONS:
            suggestions.append("Try apps with operations: IDSReporter, NIDS_Suricata")
        
        return suggestions
    
    def _generate_curl_command(self, request: SOVDRequest) -> str:
        """Generate curl command"""
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
        """Provide human-readable explanation"""
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


if __name__ == "__main__":
    assistant = SOVDAssistant()
    
    # Test keyword-based parsing with flexible word order
    test_inputs = [
        "get logs from v2x",
        "v2x logs get",  # Different order
        "show me the v2x logs please",  # Extra words
        "get comms v2x logs",  # With area
        "camera data show",  # Different order
        "list all apps",
        "check for faults",
        "goldbox operations",
    ]
    
    print("SOVD Keyword-Based NLP Processor")
    print("=" * 50)
    print("Word order doesn't matter!")
    print()
    
    for test_input in test_inputs:
        print(f"\nInput: '{test_input}'")
        result = assistant.process_request(test_input, debug=False)
        
        if result["success"]:
            print(f"✅ Intent: {result['intent']}")
            if result["entities"]:
                print(f"   Entities: {result['entities']}")
        else:
            print(f"❌ Error: {result['message']}")
        
        print("-" * 30)
