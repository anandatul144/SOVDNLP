# sovd_config.py
#!/usr/bin/env python3
"""
SOVD Configuration Management
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

class SOVDConfig:
    """Configuration manager for SOVD NLP system"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else Path("sovd_config.yaml")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    if self.config_file.suffix.lower() == '.json':
                        return json.load(f)
                    else:
                        return yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        return {
            "base_uri": "https://vehicle.example.com",
            "intent_patterns": {
                "list_apps": {
                    "regex_patterns": [
                        r"\b(list|show|get)\s+(all\s+)?(apps|applications)\b",
                        r"\bwhat\s+apps\s+are\s+(available|running)\b"
                    ],
                    "entities": {},
                    "priority": 1
                },
                "get_capabilities": {
                    "regex_patterns": [
                        r"\b(show|get|list)\s+capabilities\b",
                        r"\bwhat\s+can\s+(this\s+)?(vehicle|system)\s+do\b"
                    ],
                    "entities": {},
                    "priority": 1
                },
                "read_sensor_data": {
                    "regex_patterns": [
                        r"\b(read|get|show)\s+(sensor\s+)?data\s+(from\s+)?(?P<component>\w+)\b",
                        r"\bget\s+(?P<component>\w+)\s+(sensor\s+)?data\b",
                        r"\bshow\s+(?P<datatype>temperature|temp|voltage|pressure|rpm|speed)\s+(from\s+)?(?P<component>\w+)\b",
                        r"\bget\s+(?P<component>\w+)\s+(?P<datatype>temperature|temp|voltage|pressure|rpm|speed)\b"
                    ],
                    "entities": {"component": "component", "datatype": "datatype"},
                    "priority": 2
                },
                "get_logs": {
                    "regex_patterns": [
                        r"\b(get|show|read|fetch)\s+(system\s+)?(logs|logging)\b",
                        r"\bshow\s+me\s+the\s+logs\b",
                        r"\b(get|read)\s+(?P<component>\w+)\s+logs\b"
                    ],
                    "entities": {"component": "component"},
                    "priority": 2
                },
                "get_faults": {
                    "regex_patterns": [
                        r"\b(get|show|read|list)\s+(all\s+)?(faults|errors|DTCs?|trouble\s+codes?)\b",
                        r"\bcheck\s+for\s+(faults|errors)\b",
                        r"\bdiagnostic\s+trouble\s+codes?\b",
                        r"\bi\s+need\s+to\s+check\s+for\s+error\s+codes?\b"
                    ],
                    "entities": {},
                    "priority": 1
                },
                "get_ecu_status": {
                    "regex_patterns": [
                        r"\b(get|check|show)\s+(ecu|ECU)\s+(status|health|info)\b",
                        r"\bshow\s+(?P<ecu>\w+)\s+(ecu\s+)?status\b",
                        r"\bhow\s+is\s+the\s+(?P<ecu>\w+)\s+(ecu\s+)?doing\b",
                        r"\bshow\s+me\s+the\s+(?P<ecu>\w+)\s+status\b"
                    ],
                    "entities": {"ecu": "ecu"},
                    "priority": 2
                },
                "get_configurations": {
                    "regex_patterns": [
                        r"\b(get|show)\s+(?P<app>\w+)\s+config(uration)?s?\b",
                        r"\bshow\s+settings\s+for\s+(?P<app>\w+)\b"
                    ],
                    "entities": {"app": "app"},
                    "priority": 2
                },
                "get_operations": {
                    "regex_patterns": [
                        r"\b(get|list|show)\s+(?P<component>\w+)\s+operations\b",
                        r"\bwhat\s+can\s+(?P<component>\w+)\s+do\b"
                    ],
                    "entities": {"component": "component"},
                    "priority": 2
                },
                "security_access": {
                    "regex_patterns": [
                        r"\b(security\s+access|authenticate|login)\b",
                        r"\bget\s+access\s+to\s+(?P<component>\w+)\b"
                    ],
                    "entities": {"component": "component"},
                    "priority": 1
                }
            },
            "endpoints": {
                "list_apps": {
                    "path_template": "/apps",
                    "method": "GET",
                    "description": "List all available applications"
                },
                "get_capabilities": {
                    "path_template": "/capabilities", 
                    "method": "GET",
                    "description": "Get system capabilities"
                },
                "read_sensor_data": {
                    "path_template": "/apps/{app}/data/{datatype}",
                    "method": "GET",
                    "description": "Read sensor data from specified app/component"
                },
                "get_logs": {
                    "path_template": "/components/{component}/logs",
                    "method": "GET", 
                    "description": "Get logs from specified component"
                },
                "get_faults": {
                    "path_template": "/components/diagnostics/faults",
                    "method": "GET",
                    "description": "Get diagnostic trouble codes and faults"
                },
                "get_ecu_status": {
                    "path_template": "/components/{ecu}/status",
                    "method": "GET",
                    "description": "Get ECU status information"
                },
                "get_configurations": {
                    "path_template": "/apps/{app}/configurations",
                    "method": "GET",
                    "description": "Get application configurations"
                },
                "get_operations": {
                    "path_template": "/components/{component}/operations",
                    "method": "GET", 
                    "description": "List available operations for component"
                },
                "security_access": {
                    "path_template": "/security/access",
                    "method": "POST",
                    "description": "Request security access"
                }
            },
            "component_aliases": {
                "engine": ["motor", "powerplant", "powertrain"],
                "transmission": ["gearbox", "trans"],
                "steering": ["powersteering", "steer"], 
                "brakes": ["brake", "braking"],
                "suspension": ["susp", "shocks"],
                "battery": ["batt", "power"],
                "hvac": ["climate", "aircon", "heating", "cooling"]
            }
        }
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                if self.config_file.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2)
                else:
                    yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check base_uri
        base_uri = self.config.get("base_uri", "")
        if not base_uri:
            issues.append("Missing base_uri configuration")
        elif not base_uri.startswith(('http://', 'https://')):
            issues.append(f"base_uri should start with http:// or https://")
        
        # Check intent_patterns
        intent_patterns = self.config.get("intent_patterns", {})
        if not intent_patterns:
            issues.append("No intent_patterns configured - add them or recreate config file")
        else:
            for name, pattern_config in intent_patterns.items():
                if not isinstance(pattern_config, dict):
                    issues.append(f"Intent pattern '{name}' should be a dictionary")
                    continue
                    
                regex_patterns = pattern_config.get("regex_patterns", [])
                if not regex_patterns:
                    issues.append(f"Intent pattern '{name}' missing regex_patterns")
                elif not isinstance(regex_patterns, list):
                    issues.append(f"Intent pattern '{name}' regex_patterns should be a list")
                else:
                    # Validate regex patterns
                    for i, regex_pattern in enumerate(regex_patterns):
                        try:
                            import re
                            re.compile(regex_pattern)
                        except re.error as e:
                            issues.append(f"Intent pattern '{name}' regex {i+1} is invalid: {e}")
        
        # Check endpoints
        endpoints = self.config.get("endpoints", {})
        if not endpoints:
            issues.append("No endpoints configured")
        else:
            for name, endpoint in endpoints.items():
                if not isinstance(endpoint, dict):
                    issues.append(f"Endpoint '{name}' should be a dictionary")
                    continue
                    
                if "path_template" not in endpoint:
                    issues.append(f"Endpoint '{name}' missing path_template")
                elif not endpoint["path_template"].startswith("/"):
                    issues.append(f"Endpoint '{name}' path_template should start with '/'")
                
                if "method" not in endpoint:
                    issues.append(f"Endpoint '{name}' missing method")
                elif endpoint["method"] not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    issues.append(f"Endpoint '{name}' has invalid HTTP method")
        
        return issues
    
    def fix_missing_patterns(self):
        """Add missing intent_patterns to existing config"""
        if "intent_patterns" not in self.config:
            print("Adding missing intent_patterns to configuration")
            default_config = self._create_default_config()
            self.config["intent_patterns"] = default_config["intent_patterns"]
            self.save_config()
            return True
        return False

def create_sample_config(filename: str = "sovd_config.yaml"):
    """Create a sample configuration file with complete patterns"""
    try:
        # Create config directly - don't load existing file
        config = SOVDConfig.__new__(SOVDConfig)  # Create without calling __init__
        config.config_file = Path(filename)
        config.config = config._create_default_config()  # Get full default config
        
        config.save_config()
        print(f"Configuration created: {filename}")
        
        # Validate the created file
        config_test = SOVDConfig(filename)
        issues = config_test.validate_config()
        if issues:
            print("Warning: Created config has issues:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("Created config is valid")
            
    except Exception as e:
        print(f"Error creating config: {e}")

def validate_config_file(filename: str):
    """Validate a configuration file"""
    try:
        config = SOVDConfig(filename)
        issues = config.validate_config()
        
        if issues:
            print(f"Configuration issues found in {filename}:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print(f"Configuration {filename} is valid")
            base_uri = config.config.get('base_uri', 'Not set')
            intent_count = len(config.config.get('intent_patterns', {}))
            endpoint_count = len(config.config.get('endpoints', {}))
            print(f"Base URI: {base_uri}")
            print(f"Intent patterns: {intent_count}")
            print(f"Endpoints: {endpoint_count}")
            return True
            
    except FileNotFoundError:
        print(f"Configuration file not found: {filename}")
        return False
    except Exception as e:
        print(f"Error validating {filename}: {e}")
        return False

def fix_config_file(filename: str):
    """Fix missing intent_patterns in config file"""
    try:
        config = SOVDConfig(filename)
        
        if config.fix_missing_patterns():
            print(f"Fixed {filename} - added missing intent_patterns")
            
            # Validate after fix
            issues = config.validate_config()
            if issues:
                print("Remaining issues:")
                for issue in issues:
                    print(f"  {issue}")
            else:
                print(f"Configuration {filename} is now valid")
        else:
            print(f"Configuration {filename} already has intent_patterns")
            
    except FileNotFoundError:
        print(f"Configuration file not found: {filename}")
    except Exception as e:
        print(f"Error fixing {filename}: {e}")

def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="SOVD Configuration Management")
    parser.add_argument(
        'command',
        choices=['create', 'validate', 'fix'],
        help='Command to execute'
    )
    parser.add_argument(
        'filename',
        nargs='?',
        default='sovd_config.yaml',
        help='Configuration filename'
    )
    
    args = parser.parse_args()
    
    try:
        if args.command == "create":
            create_sample_config(args.filename)
        elif args.command == "validate":
            is_valid = validate_config_file(args.filename)
            sys.exit(0 if is_valid else 1)
        elif args.command == "fix":
            fix_config_file(args.filename)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()