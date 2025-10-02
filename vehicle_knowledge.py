# vehicle_knowledge.py

"""
Vehicle Knowledge Base - provides search, lookup, and validation
against the actual vehicle structure from vehicle_model.py

This module enables the NLP system to be "aware" of the real vehicle
architecture, components, apps, and their relationships.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher, get_close_matches


class VehicleKnowledge:
    """
    Knowledge base for vehicle structure. Provides fuzzy matching,
    entity resolution, and query validation against the real vehicle model.
    """
    
    def __init__(self, snapshot_file: str = "vehicle_model_snapshot.json"):
        self.snapshot_file = Path(snapshot_file)
        self.vehicle_data = self._load_snapshot()
        
        self.areas = self.vehicle_data.get("areas", {})
        self.components = self.vehicle_data.get("components", {})
        self.apps = self.vehicle_data.get("apps", {})
        
        self._build_search_indices()
    
    def _load_snapshot(self) -> Dict:
        """Load vehicle model snapshot from JSON file"""
        if not self.snapshot_file.exists():
            raise FileNotFoundError(
                f"Vehicle model snapshot not found: {self.snapshot_file}\n"
                f"Please run: python export_vehicle_model.py"
            )
        
        try:
            with open(self.snapshot_file, 'r') as f:
                snapshot = json.load(f)
            
            if "vehicle_data" not in snapshot:
                raise ValueError("Invalid snapshot format: missing 'vehicle_data'")
            
            return snapshot["vehicle_data"]
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in snapshot file: {e}")
    
    def _build_search_indices(self):
        """Build search indices for fast lookup"""
        self.component_names = {}
        for comp_id, comp_data in self.components.items():
            self.component_names[comp_id.lower()] = comp_id
            self.component_names[comp_data["name"].lower()] = comp_id
        
        self.app_names = {}
        for app_id, app_data in self.apps.items():
            self.app_names[app_id.lower()] = app_id
            self.app_names[app_data["name"].lower()] = app_id
        
        self.area_names = {}
        for area_id, area_data in self.areas.items():
            self.area_names[area_id.lower()] = area_id
            self.area_names[area_data["name"].lower()] = area_id
    
    def find_component(self, text: str) -> Optional[Dict]:
        """
        Find a component by name or ID with fuzzy matching.
        
        Args:
            text: Component name or ID (case-insensitive)
        
        Returns:
            Component dict with full info, or None if not found
        """
        text_lower = text.lower().strip()
        
        # Exact match first
        if text_lower in self.component_names:
            comp_id = self.component_names[text_lower]
            return {
                "id": comp_id,
                "type": "component",
                **self.components[comp_id]
            }
        
        # Fuzzy match on component IDs and names
        all_names = list(self.component_names.keys())
        matches = get_close_matches(text_lower, all_names, n=1, cutoff=0.6)
        
        if matches:
            comp_id = self.component_names[matches[0]]
            return {
                "id": comp_id,
                "type": "component",
                **self.components[comp_id]
            }
        
        return None
    
    def find_app(self, text: str) -> Optional[Dict]:
        """
        Find an app by name or ID with fuzzy matching.
        
        Args:
            text: App name or ID (case-insensitive)
        
        Returns:
            App dict with full info, or None if not found
        """
        text_lower = text.lower().strip()
        
        # Exact match
        if text_lower in self.app_names:
            app_id = self.app_names[text_lower]
            return {
                "id": app_id,
                "type": "app",
                **self.apps[app_id]
            }
        
        # Fuzzy match
        all_names = list(self.app_names.keys())
        matches = get_close_matches(text_lower, all_names, n=1, cutoff=0.6)
        
        if matches:
            app_id = self.app_names[matches[0]]
            return {
                "id": app_id,
                "type": "app",
                **self.apps[app_id]
            }
        
        return None
    
    def find_area(self, text: str) -> Optional[Dict]:
        """
        Find an area by name or ID with fuzzy matching.
        
        Args:
            text: Area name or ID (case-insensitive)
        
        Returns:
            Area dict with full info, or None if not found
        """
        text_lower = text.lower().strip()
        
        # Exact match
        if text_lower in self.area_names:
            area_id = self.area_names[text_lower]
            return {
                "id": area_id,
                "type": "area",
                **self.areas[area_id]
            }
        
        # Fuzzy match
        all_names = list(self.area_names.keys())
        matches = get_close_matches(text_lower, all_names, n=1, cutoff=0.6)
        
        if matches:
            area_id = self.area_names[matches[0]]
            return {
                "id": area_id,
                "type": "area",
                **self.areas[area_id]
            }
        
        return None
    
    def find_entity(self, text: str, entity_type: Optional[str] = None) -> Optional[Dict]:
        """
        Find any entity (area, component, or app) by text.
        
        Args:
            text: Entity name or ID
            entity_type: Specific type to search ('area', 'component', 'app'), 
                        or None to search all
        
        Returns:
            Entity dict with 'type' field, or None if not found
        """
        if entity_type == "component" or entity_type is None:
            result = self.find_component(text)
            if result:
                return result
        
        if entity_type == "app" or entity_type is None:
            result = self.find_app(text)
            if result:
                return result
        
        if entity_type == "area" or entity_type is None:
            result = self.find_area(text)
            if result:
                return result
        
        return None
    
    def get_component(self, component_id: str) -> Optional[Dict]:
        """Get component by exact ID"""
        return self.components.get(component_id)
    
    def get_app(self, app_id: str) -> Optional[Dict]:
        """Get app by exact ID"""
        return self.apps.get(app_id)
    
    def get_area(self, area_id: str) -> Optional[Dict]:
        """Get area by exact ID"""
        return self.areas.get(area_id)
    
    def get_apps_on_component(self, component_id: str) -> List[Dict]:
        """
        Get all apps running on a specific component.
        
        Args:
            component_id: Component ID
        
        Returns:
            List of app dicts
        """
        component = self.get_component(component_id)
        if not component:
            return []
        
        app_ids = component.get("apps", [])
        return [self.get_app(app_id) for app_id in app_ids if self.get_app(app_id)]
    
    def get_components_in_area(self, area_id: str) -> List[Dict]:
        """
        Get all components in a specific area.
        
        Args:
            area_id: Area ID
        
        Returns:
            List of component dicts
        """
        area = self.get_area(area_id)
        if not area:
            return []
        
        component_ids = area.get("components", [])
        return [self.get_component(c_id) for c_id in component_ids if self.get_component(c_id)]
    
    def get_bulk_data_paths(self, app_id: str) -> Dict[str, str]:
        """
        Get bulk data paths available for an app.
        
        Args:
            app_id: App ID
        
        Returns:
            Dict mapping bulk data category to filesystem path
        """
        app = self.get_app(app_id)
        if not app:
            return {}
        
        return app.get("bulk_data_map", {})
    
    def get_app_operations(self, app_id: str) -> List[str]:
        """
        Get available operations for an app.
        
        Args:
            app_id: App ID
        
        Returns:
            List of operation names
        """
        app = self.get_app(app_id)
        if not app:
            return []
        
        return app.get("operations", [])
    
    def validate_entity_exists(self, entity_name: str, entity_type: str) -> bool:
        """
        Check if an entity exists.
        
        Args:
            entity_name: Entity name or ID
            entity_type: 'area', 'component', or 'app'
        
        Returns:
            True if entity exists
        """
        return self.find_entity(entity_name, entity_type) is not None
    
    def suggest_similar(self, text: str, entity_type: str = None, limit: int = 3) -> List[str]:
        """
        Suggest similar entity names for a given text (for typo correction).
        
        Args:
            text: Input text (potentially misspelled)
            entity_type: Type to search, or None for all types
            limit: Max number of suggestions
        
        Returns:
            List of suggested entity IDs
        """
        text_lower = text.lower().strip()
        suggestions = []
        
        if entity_type == "component" or entity_type is None:
            matches = get_close_matches(text_lower, self.component_names.keys(), n=limit, cutoff=0.4)
            suggestions.extend([self.component_names[m] for m in matches])
        
        if entity_type == "app" or entity_type is None:
            matches = get_close_matches(text_lower, self.app_names.keys(), n=limit, cutoff=0.4)
            suggestions.extend([self.app_names[m] for m in matches])
        
        if entity_type == "area" or entity_type is None:
            matches = get_close_matches(text_lower, self.area_names.keys(), n=limit, cutoff=0.4)
            suggestions.extend([self.area_names[m] for m in matches])
        
        return list(set(suggestions))[:limit]
    
    def validate_query(self, intent_type: str, entities: Dict) -> Tuple[bool, str]:
        """
        Validate if a query makes sense for the given entities.
        
        Args:
            intent_type: Intent type (e.g., 'get_logs', 'read_sensor_data')
            entities: Dict of resolved entities
        
        Returns:
            (is_valid, error_message) tuple
        """
        
        # Validate "get_logs" - component must have apps with logs
        if intent_type == "get_logs":
            component_id = entities.get("component")
            if component_id:
                component = self.get_component(component_id)
                if not component:
                    return False, f"Component '{component_id}' not found"
                
                apps = self.get_apps_on_component(component_id)
                if not apps:
                    return False, f"Component '{component_id}' has no applications"
                
                has_logs = any(
                    "bulk_data_map" in app and 
                    any("log" in k.lower() for k in app["bulk_data_map"].keys())
                    for app in apps
                )
                if not has_logs:
                    return False, f"No apps on '{component_id}' provide logs"
        
        # Validate "get_bulk_data" - app must have bulk_data_map
        if intent_type == "get_bulk_data":
            app_id = entities.get("app")
            if app_id:
                app = self.get_app(app_id)
                if not app:
                    return False, f"App '{app_id}' not found"
                
                bulk_data = app.get("bulk_data_map", {})
                if not bulk_data:
                    return False, f"App '{app_id}' has no bulk data available"
                
                # Check if requested category exists
                category = entities.get("bulk_category")
                if category and category not in bulk_data:
                    available = ", ".join(bulk_data.keys())
                    return False, f"Bulk data category '{category}' not available. Available: {available}"
        
        # Validate "get_operations" - app must have operations
        if intent_type == "get_operations":
            app_id = entities.get("app")
            if app_id:
                app = self.get_app(app_id)
                if not app:
                    return False, f"App '{app_id}' not found"
                
                operations = app.get("operations", [])
                if not operations:
                    return False, f"App '{app_id}' has no operations defined"
        
        return True, ""
    
    def get_statistics(self) -> Dict:
        """Get statistics about the vehicle model"""
        return {
            "areas": len(self.areas),
            "components": len(self.components),
            "apps": len(self.apps),
            "components_by_architecture": self._count_by_architecture(),
            "apps_with_bulk_data": sum(1 for app in self.apps.values() if app.get("bulk_data_map")),
            "apps_with_operations": sum(1 for app in self.apps.values() if app.get("operations"))
        }
    
    def _count_by_architecture(self) -> Dict[str, int]:
        """Count components by architecture type"""
        counts = {}
        for comp in self.components.values():
            arch = comp.get("architecture", "unknown")
            counts[arch] = counts.get(arch, 0) + 1
        return counts


def test_vehicle_knowledge():
    """Test function to verify vehicle knowledge functionality"""
    try:
        vk = VehicleKnowledge()
        
        print("Vehicle Knowledge Test")
        print("=" * 50)
        
        stats = vk.get_statistics()
        print(f"\nStatistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\nTest 1: Find component 'V2X'")
        result = vk.find_component("V2X")
        print(f"  Found: {result['id'] if result else 'None'}")
        
        print(f"\nTest 2: Find component 'v2x' (lowercase)")
        result = vk.find_component("v2x")
        print(f"  Found: {result['id'] if result else 'None'}")
        
        print(f"\nTest 3: Find component 'camera' (fuzzy)")
        result = vk.find_component("camera")
        print(f"  Found: {result['id'] if result else 'None'}")
        
        print(f"\nTest 4: Find app 'NIDS'")
        result = vk.find_app("NIDS")
        print(f"  Found: {result['id'] if result else 'None'}")
        
        print(f"\nTest 5: Get apps on V2X")
        apps = vk.get_apps_on_component("V2X")
        print(f"  Apps: {[app['id'] for app in apps]}")
        
        print(f"\nTest 6: Get bulk data paths for IDSReporter")
        paths = vk.get_bulk_data_paths("IDSReporter")
        print(f"  Paths: {list(paths.keys())}")
        
        print(f"\nTest 7: Validate query - get logs from V2X")
        valid, msg = vk.validate_query("get_logs", {"component": "V2X"})
        print(f"  Valid: {valid}, Message: {msg}")
        
        print(f"\nTest 8: Validate query - get logs from Brakes (should fail)")
        valid, msg = vk.validate_query("get_logs", {"component": "Brakes"})
        print(f"  Valid: {valid}, Message: {msg}")
        
        print(f"\nTest 9: Suggest similar to 'camra' (typo)")
        suggestions = vk.suggest_similar("camra", "component")
        print(f"  Suggestions: {suggestions}")
        
        print("\nAll tests completed successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease run: python export_vehicle_model.py")
    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    test_vehicle_knowledge()