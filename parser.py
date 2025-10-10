"""
Blueprint JSON parsing functionality
"""
import json
from pathlib import Path
from typing import Dict, Any


class BlueprintParser:
    """Handles loading and parsing of Fusion blueprint JSON files."""
    
    def load_blueprint(self, file_path: Path) -> Dict[str, Any]:
        """
        Load a blueprint JSON file and return parsed data.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dict containing the parsed blueprint data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file isn't valid JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in {file_path.name}: {e.msg}", e.doc, e.pos)
        except FileNotFoundError:
            raise FileNotFoundError(f"Blueprint file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading {file_path.name}: {str(e)}")
    
    def get_scenario_name(self, blueprint_data: Dict[str, Any], filename: str) -> str:
        """
        Extract scenario name from blueprint data, fallback to filename.
        
        Args:
            blueprint_data: Parsed blueprint JSON
            filename: Filename without extension to use as fallback
            
        Returns:
            Scenario name string
        """
        return blueprint_data.get('name', filename)
    
    def get_modules(self, blueprint_data: Dict[str, Any], include_orphans: bool = False) -> list:
        """
        Extract ALL modules from the blueprint flow, including nested routes and error handlers.
        
        Args:
            blueprint_data: Parsed blueprint JSON
            include_orphans: Whether to include orphaned modules from metadata.designer.orphans
            
        Returns:
            List of all module dictionaries (flattened from nested structure)
        """
        all_modules = []
        top_level_flow = blueprint_data.get('flow', [])
        
        def extract_modules_recursive(modules_list):
            """Recursively extract modules from nested route structures and error handlers."""
            for module in modules_list:
                all_modules.append(module)
                
                # Check if this module has routes (nested flows)
                routes = module.get('routes', [])
                for route in routes:
                    route_flow = route.get('flow', [])
                    if route_flow:
                        extract_modules_recursive(route_flow)
                
                # Check if this module has error handlers (onerror flows)
                onerror = module.get('onerror', [])
                if onerror:
                    extract_modules_recursive(onerror)
        
        # Extract modules from main execution flow
        extract_modules_recursive(top_level_flow)
        
        # Optionally extract modules from orphaned flows  
        if include_orphans:
            orphans = blueprint_data.get('metadata', {}).get('designer', {}).get('orphans', [])
            for orphan_group in orphans:
                if isinstance(orphan_group, list):
                    extract_modules_recursive(orphan_group)
        
        return all_modules