# sovd_nlp_prototype.py
# Keyword-based NLP with dynamic extraction from vehicle model

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
    LIST_APPS_ON_COMPONENT = "list_apps_on_component"
    LIST_AREAS = "list_areas"
    LIST_COMPONENTS = "list_components"
    LIST_COMPONENTS_IN_AREA = "list_components_in_area"
    GET_CAPABILITIES = "get_capabilities"
    READ_SENSOR_DATA = "read_sensor_data"
    GET_LOGS = "get_logs"
    GET_BULK_DATA = "get_bulk_data"
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
    Keyword-based NLP with dynamic keyword extraction from vehicle model.
    Keywords are built from vehicle_model_snapshot.json at initialization.
    """
    
    # Prohibited operations (read-only tool)
    PROHIBITED_ACTIONS = {"delete", "remove", "insert", "add", "create", "write", "update", "modify"}
    
    def __init__(self, vehicle_knowledge: Optional['VehicleKnowledge'] = None):
        """Initialize NLP processor with vehicle knowledge"""
        
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
        
        # Build keywords from vehicle model
        self._build_keywords()
    
    def _build_keywords(self):
        """
        Build keyword mappings from vehicle model.
        Called once per initialization (~15-20ms).
        """
        
        # Static action verbs (read-only operations)
        self.action_verbs = {
            "get": "read",
            "show": "read",
            "list": "read",
            "read": "read",
            "fetch": "read",
            "retrieve": "read",
            "display": "read",
            "check": "read",
            # Prohibited verbs - recognized but will be rejected
            "delete": "delete",
            "remove": "delete",
            "insert": "write",
            "add": "write",
            "create": "write",
            "write": "write",
            "update": "write",
            "modify": "write",
        }
        
        # Base data types (static)
        self.data_types = {
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
            "areas": "areas",
            "area": "areas",
            "zones": "areas",
            "zone": "areas",
            "components": "components",
            "component": "components",
            "ecus": "components",
            "ecu": "components",
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
            "all", "any", "some", "this", "that", "these", "those", "of"
        }
        
        # Extract keywords from vehicle model if available
        if self.vehicle_knowledge:
            self._extract_bulk_data_keywords()
            self._extract_area_keywords()
    
    def _extract_bulk_data_keywords(self):
        """Extract bulk data categories from all apps in vehicle model"""
        
        bulk_keywords = set()
        
        for app_id, app_data in self.vehicle_knowledge.apps.items():
            if "bulk_data_map" not in app_data:
                continue
            
            bulk_map = app_data["bulk_data_map"]
            
            for category, path in bulk_map.items():
                # Add full category name: "ids_alerts" → "alerts"
                bulk_keywords.add(category)
                
                # Split on underscore and add parts: "ids_alerts" → ["ids", "alerts"]
                if "_" in category:
                    parts = category.split("_")
                    bulk_keywords.update(parts)
                
                # Extract keywords from path: "opt/suricata/logs" → ["logs"]
                if "/" in path:
                    path_parts = path.split("/")
                    bulk_keywords.update(path_parts)
        
        # Map all bulk data keywords to appropriate intent data type
        for keyword in bulk_keywords:
            keyword_lower = keyword.lower()
            
            # Map to existing data types or create new mappings
            if "log" in keyword_lower:
                self.data_types[keyword_lower] = "logs"
            elif "alert" in keyword_lower:
                self.data_types[keyword_lower] = "alerts"
            elif "rule" in keyword_lower:
                self.data_types[keyword_lower] = "rules"
            elif "config" in keyword_lower:
                self.data_types[keyword_lower] = "configurations"
            elif "capture" in keyword_lower or "pcap" in keyword_lower:
                self.data_types[keyword_lower] = "captures"
            else:
                # Generic bulk data
                self.data_types[keyword_lower] = "bulk_data"
    
    def _extract_area_keywords(self):
        """Extract area names and common aliases"""
        
        self.area_keywords = {}
        
        for area_id, area_data in self.vehicle_knowledge.areas.items():
            area_name = area_data["name"].lower()
            
            # Add area ID (case-insensitive)
            self.area_keywords[area_id.lower()] = area_id
            
            # Add full name
            self.area_keywords[area_name] = area_id
            
            # Add common aliases
            if "communication" in area_name:
                self.area_keywords["comms"] = area_id
                self.area_keywords["comm"] = area_id
                self.area_keywords["network"] = area_id
            elif "adas" in area_name.lower():
                self.area_keywords["adas"] = area_id
                self.area_keywords["nav"] = area_id
                self.area_keywords["navigation"] = area_id
            elif "chassis" in area_name:
                self.area_keywords["chassis"] = area_id
                self.area_keywords["base"] = area_id
                self.area_keywords["powertrain"] = area_id
    
    def parse_natural_language(self, text: str, debug: bool = False) -> Optional[Intent]:
        """
        Parse natural language using keyword scanning.
        Word order doesn't matter.
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
                parsed["action"] = token
                if debug:
                    print(f"Debug: Found action: {token}")
                break
        
        # Check for prohibited operations
        if parsed["action"] in self.PROHIBITED_ACTIONS:
            if debug:
                print(f"Debug: Prohibited action detected: {parsed['action']}")
            return None  # Will be handled in process_request
        
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
        
        # Scan for area (using extracted keywords)
        if hasattr(self, 'area_keywords'):
            for token in tokens:
                if token in self.area_keywords:
                    area_id = self.area_keywords[token]
                    area = self.vehicle_knowledge.find_area(area_id)
                    if area:
                        parsed["area"] = area["id"]
                        parsed["area_info"] = area
                        if debug:
                            print(f"Debug: Found area: {token} → {area['id']}")
                        break
        
        # Scan for entities using vehicle knowledge
        if self.vehicle_knowledge:
            for token in tokens:
                if token in self.ignore_words:
                    continue
                
                # Try to find component (if not already found)
                if parsed["component"] is None:
                    component = self.vehicle_knowledge.find_component(token)
                    if component:
                        parsed["component"] = component["id"]
                        parsed["component_info"] = component
                        if debug:
                            print(f"Debug: Found component: {token} → {component['id']}")
                        continue
                
                # Try to find app (if not already found)
                if parsed["app"] is None:
                    app = self.vehicle_knowledge.find_app(token)
                    if app:
                        parsed["app"] = app["id"]
                        parsed["app_info"] = app
                        if debug:
                            print(f"Debug: Found app: {token} → {app['id']}")
                        continue
            
            # Context-aware app resolution: if component found but no app, search component's apps
            if parsed["component"] and not parsed["app"]:
                component_apps = self.vehicle_knowledge.get_apps_on_component(parsed["component"])
                if component_apps and debug:
                    print(f"Debug: Searching {len(component_apps)} apps on component {parsed['component']}")
                
                matches = []
                for token in tokens:
                    if token in self.ignore_words:
                        continue
                    
                    # Check each app on this component for substring match
                    for app in component_apps:
                        app_id_lower = app["id"].lower()
                        if token in app_id_lower or token.replace("_", "") in app_id_lower.replace("_", ""):
                            if app["id"] not in [m["id"] for m in matches]:
                                matches.append(app)
                
                # Handle matches
                if len(matches) == 1:
                    parsed["app"] = matches[0]["id"]
                    parsed["app_info"] = matches[0]
                    if debug:
                        print(f"Debug: Context match found: {matches[0]['id']}")
                elif len(matches) > 1:
                    # Multiple matches - store for ambiguity handling
                    parsed["ambiguous_apps"] = matches
                    if debug:
                        print(f"Debug: Multiple matches found: {[m['id'] for m in matches]}")
        
        if debug:
            print(f"Debug: Parsed keywords: {parsed}")
        
        # Classify intent from keywords
        intent = self._classify_intent(parsed, debug)
        
        if debug and intent:
            print(f"Debug: Classified intent: {intent.type.value}, entities: {intent.entities}")
        
        return intent
    
    def _classify_intent(self, parsed: Dict, debug: bool = False) -> Optional[Intent]:
        """Classify intent based on extracted keywords"""
        
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
        
        # List areas
        if parsed["data_type"] == "areas":
            return Intent(type=IntentType.LIST_AREAS, entities={})
        
        # List components
        if parsed["data_type"] == "components":
            if parsed["area"]:
                # List components in specific area
                entities = {"area": parsed["area"]}
                if "area_info" in parsed:
                    entities["area_info"] = parsed["area_info"]
                return Intent(type=IntentType.LIST_COMPONENTS_IN_AREA, entities=entities)
            else:
                # List all components
                return Intent(type=IntentType.LIST_COMPONENTS, entities={})
        
        # List apps
        if parsed["action"] == "list" and parsed["data_type"] == "apps":
            if parsed["component"]:
                # List apps on specific component
                entities = {"component": parsed["component"]}
                if "component_info" in parsed:
                    entities["component_info"] = parsed["component_info"]
                return Intent(type=IntentType.LIST_APPS_ON_COMPONENT, entities=entities)
            else:
                # List all apps
                return Intent(type=IntentType.LIST_APPS, entities={})
        
        if parsed["data_type"] == "apps" and not parsed["component"]:
            return Intent(type=IntentType.LIST_APPS, entities={})
        
        # Get logs - handle both app and component
        if parsed["data_type"] == "logs":
            # Check for ambiguous apps
            if "ambiguous_apps" in parsed:
                # Return ambiguous result with multiple options
                return None  # Will be handled in process_request
            
            entities = {}
            
            # Priority 1: User specified an app
            if parsed["app"]:
                app_info = parsed.get("app_info")
                if app_info and "bulk_data_map" in app_info:
                    bulk_map = app_info["bulk_data_map"]
                    
                    # Find log-related bulk data
                    log_keys = [k for k in bulk_map.keys() if "log" in k.lower()]
                    
                    if log_keys:
                        entities["app"] = parsed["app"]
                        entities["bulk_data_category"] = log_keys[0]
                        entities["bulk_data_path"] = bulk_map[log_keys[0]]
                        if "app_info" in parsed:
                            entities["app_info"] = app_info
                        
                        if debug:
                            print(f"Debug: App logs - using bulk data: {log_keys[0]} → {bulk_map[log_keys[0]]}")
                        
                        return Intent(type=IntentType.GET_BULK_DATA, entities=entities)
            
            # Priority 2: Component-level logs
            if parsed["component"]:
                entities["component"] = parsed["component"]
                if "component_info" in parsed:
                    entities["component_info"] = parsed["component_info"]
                    entities["component_type"] = "component"
            
            return Intent(type=IntentType.GET_LOGS, entities=entities)
        
        # Get alerts/rules (bulk data)
        if parsed["data_type"] in ["alerts", "rules", "captures"]:
            entities = {}
            
            if parsed["app"]:
                app_info = parsed.get("app_info")
                if app_info and "bulk_data_map" in app_info:
                    bulk_map = app_info["bulk_data_map"]
                    
                    # Find matching bulk data category
                    matching_keys = [k for k in bulk_map.keys() if parsed["data_type"][:-1] in k.lower()]
                    
                    if matching_keys:
                        entities["app"] = parsed["app"]
                        entities["bulk_data_category"] = matching_keys[0]
                        entities["bulk_data_path"] = bulk_map[matching_keys[0]]
                        return Intent(type=IntentType.GET_BULK_DATA, entities=entities)
            
            # Fallback
            return None
        
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
        
        # Fallback: component mentioned but no data type
        if parsed["component"] and not parsed["data_type"]:
            entities = {
                "component": parsed["component"]
            }
            if "component_info" in parsed:
                entities["component_info"] = parsed["component_info"]
                entities["component_type"] = "component"
            return Intent(type=IntentType.READ_SENSOR_DATA, entities=entities)
        
        return None
    
    def intent_to_sovd_request(self, intent: Intent) -> SOVDRequest:
        """Convert parsed intent to SOVD HTTP request"""
        
        if intent.type == IntentType.LIST_APPS:
            return SOVDRequest(method="GET", endpoint="/apps")
        
        elif intent.type == IntentType.LIST_APPS_ON_COMPONENT:
            component = intent.entities.get("component", "Unknown")
            return SOVDRequest(method="GET", endpoint=f"/components/{component}/related-apps")
        
        elif intent.type == IntentType.LIST_AREAS:
            return SOVDRequest(method="GET", endpoint="/areas")
        
        elif intent.type == IntentType.LIST_COMPONENTS:
            return SOVDRequest(method="GET", endpoint="/components")
        
        elif intent.type == IntentType.LIST_COMPONENTS_IN_AREA:
            area = intent.entities.get("area", "Unknown")
            return SOVDRequest(method="GET", endpoint=f"/areas/{area}/related-components")
        
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
        
        elif intent.type == IntentType.GET_BULK_DATA:
            app = intent.entities.get("app", "DefaultApp")
            bulk_path = intent.entities.get("bulk_data_path", "data")
            endpoint = f"/apps/{app}/bulk-data/{bulk_path}"
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
    """Main assistant class - identical API to previous versions"""
    
    def __init__(self, base_uri: str = None, config_file: str = None, vehicle_knowledge: Optional['VehicleKnowledge'] = None):
        """Initialize SOVD Assistant"""
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
        """Process natural language input - identical API"""
        
        if debug:
            print(f"Debug: Processing input: '{user_input}'")
        
        # Check for prohibited actions early
        tokens = user_input.lower().split()
        prohibited_found = None
        for token in tokens:
            if token in SOVDNLPProcessor.PROHIBITED_ACTIONS:
                prohibited_found = token
                break
        
        if prohibited_found:
            return {
                "success": False,
                "message": f"Operation '{prohibited_found}' is not permitted. This is a read-only diagnostic tool.",
                "action_attempted": prohibited_found,
                "suggestions": [
                    "Try: get logs, show data, list apps, check status",
                    "All write/delete operations are disabled for safety"
                ]
            }
        
        # Parse intent
        intent = self.nlp_processor.parse_natural_language(user_input, debug=debug)
        
        if not intent:
            # Check if parsing failed due to ambiguity
            parsed_keywords = self.nlp_processor.parse_natural_language.__self__
            test_parse = user_input.lower().split()
            
            # Quick ambiguity check
            if self.nlp_processor.vehicle_knowledge:
                # Try to detect ambiguous apps
                component_found = None
                for token in test_parse:
                    comp = self.nlp_processor.vehicle_knowledge.find_component(token)
                    if comp:
                        component_found = comp["id"]
                        break
                
                if component_found:
                    apps = self.nlp_processor.vehicle_knowledge.get_apps_on_component(component_found)
                    matches = []
                    for token in test_parse:
                        for app in apps:
                            if token in app["id"].lower() and app["id"] not in [m["id"] for m in matches]:
                                matches.append(app)
                    
                    if len(matches) > 1:
                        # Return ambiguous result with all possible endpoints
                        suggestions = []
                        for app in matches:
                            bulk_map = app.get("bulk_data_map", {})
                            for category, path in bulk_map.items():
                                endpoint = f"/apps/{app['id']}/bulk-data/{path}"
                                suggestions.append({
                                    "app": app["id"],
                                    "category": category,
                                    "endpoint": endpoint
                                })
                        
                        return {
                            "success": False,
                            "ambiguous": True,
                            "message": f"Multiple apps found: {', '.join([m['id'] for m in matches])}",
                            "matches": [m["id"] for m in matches],
                            "possible_endpoints": suggestions[:5],  # Limit to 5
                            "suggestions": [f"Try: get {component_found} {m['id']} logs" for m in matches[:3]]
                        }
            
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
            "List all areas",
            "Show capabilities",
            "Get V2X logs",
            "Show Camera data"
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
            IntentType.LIST_APPS_ON_COMPONENT: f"This will list applications running on {intent.entities.get('component', 'the component')}",
            IntentType.LIST_AREAS: "This will list all areas/zones in the vehicle",
            IntentType.LIST_COMPONENTS: "This will list all components/ECUs in the vehicle",
            IntentType.LIST_COMPONENTS_IN_AREA: f"This will list components in the {intent.entities.get('area', 'specified')} area",
            IntentType.GET_CAPABILITIES: "This will show what diagnostic capabilities are available",
            IntentType.READ_SENSOR_DATA: f"This will read sensor data from {intent.entities.get('component', 'the specified component')}",
            IntentType.GET_LOGS: f"This will retrieve logs from {intent.entities.get('component', 'the system')}",
            IntentType.GET_BULK_DATA: f"This will retrieve {intent.entities.get('bulk_data_category', 'bulk data')} from {intent.entities.get('app', 'the application')}",
            IntentType.GET_FAULTS: "This will get all diagnostic trouble codes and fault information",
            IntentType.GET_ECU_STATUS: f"This will check the status of {intent.entities.get('ecu', 'the ECU')}",
            IntentType.GET_CONFIGURATIONS: f"This will get configuration settings for {intent.entities.get('app', 'the application')}",
            IntentType.GET_OPERATIONS: f"This will list available operations for {intent.entities.get('component', 'the component')}",
            IntentType.SECURITY_ACCESS: "This will initiate security access procedure",
        }
        
        return explanations.get(intent.type, "This will perform the requested diagnostic operation")


if __name__ == "__main__":
    assistant = SOVDAssistant()
    
    # Test with dynamic keywords
    test_inputs = [
        "list all areas",
        "get nids logs",
        "show camera data",
        "list components in adas",
        "delete v2x logs",  # Should be rejected
    ]
    
    print("SOVD Keyword-Based NLP (Dynamic Keywords from Vehicle Model)")
    print("=" * 60)
    
    for test_input in test_inputs:
        print(f"\nInput: '{test_input}'")
        result = assistant.process_request(test_input, debug=False)
        
        if result["success"]:
            print(f"✅ Intent: {result['intent']}")
            if result["entities"]:
                print(f"   Entities: {list(result['entities'].keys())}")
            print(f"   Endpoint: {result['http_request'].split()[1]}")
        else:
            print(f"❌ Error: {result['message']}")
        
        print("-" * 40)