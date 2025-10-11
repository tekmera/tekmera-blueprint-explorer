"""
Blueprint analysis functionality
"""

from typing import Any, Dict, List, Set


class BlueprintAnalyzer:
    """Analyzes blueprint data to extract metrics and information."""

    def analyze_blueprint(
        self, blueprint_data: Dict[str, Any], filename: str, parser=None
    ) -> Dict[str, Any]:
        """
        Perform complete analysis of a blueprint.

        Args:
            blueprint_data: Parsed blueprint JSON
            filename: Filename without extension
            parser: Parser instance for recursive module extraction

        Returns:
            Dict containing analysis results
        """
        if parser:
            # Use recursive parsing to get ALL modules
            modules = parser.get_modules(blueprint_data, include_orphans=False)
        else:
            # Fallback to top-level flow only
            modules = blueprint_data.get("flow", [])

        return {
            "filename": filename,
            "scenario_name": blueprint_data.get("name", filename),
            "module_count": len(modules),
            "module_types": self._get_unique_module_types(modules),
            "workfront_fields": self._find_workfront_fields(blueprint_data),
        }

    def _get_unique_module_types(self, modules: List[Dict[str, Any]]) -> List[str]:
        """
        Extract unique module types from modules list.

        Args:
            modules: List of module dictionaries

        Returns:
            Sorted list of unique module type strings
        """
        module_types = set()
        for module in modules:
            try:
                module_type = module.get("module", "UNKNOWN")
                if module_type != "UNKNOWN":
                    module_types.add(module_type)
            except (AttributeError, TypeError):
                # Skip malformed module entries
                continue
        return sorted(list(module_types))

    def _find_workfront_fields(self, data: Any) -> Set[str]:
        """
        Recursively find all Workfront field keys (starting with 'DE:').

        Args:
            data: JSON data to search through

        Returns:
            Set of unique DE: field keys
        """
        de_fields = set()

        def _recursive_search(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(key, str) and key.startswith("DE:"):
                        de_fields.add(key)
                    if isinstance(value, str) and value.startswith("DE:"):
                        de_fields.add(value)
                    _recursive_search(value)
            elif isinstance(obj, list):
                for item in obj:
                    _recursive_search(item)

        _recursive_search(data)
        return de_fields

    def get_detailed_module_info(self, module: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Extract detailed information about a single module.

        Args:
            module: Single module dictionary
            index: Module index number

        Returns:
            Dict containing detailed module information
        """
        module_type = module.get("module", "UNKNOWN")
        module_id = module.get("id", f"module_{index}")

        # Get module name from metadata or use type as fallback
        metadata = module.get("metadata", {})
        designer = metadata.get("designer", {})
        module_name = designer.get("name", module_type)

        # Extract parameters and mapper data
        parameters = module.get("parameters", {}) or {}
        mapper = module.get("mapper", {}) or {}

        # Find DE fields in this specific module
        module_de_fields = self._find_workfront_fields(module)

        # Generate summary based on module type
        summary = self._generate_module_summary(module_type, parameters, mapper)

        return {
            "index": index,
            "id": module_id,
            "name": module_name,
            "type": module_type,
            "summary": summary,
            "parameters": parameters,
            "mapper": mapper,
            "metadata": metadata,
            "de_fields": sorted(list(module_de_fields)),
            "raw_data": module,
        }

    def _generate_module_summary(self, module_type: str, parameters: Dict, mapper: Dict) -> str:
        """
        Generate a brief summary of what the module does.

        Args:
            module_type: The module type string
            parameters: Module parameters
            mapper: Module mapper data

        Returns:
            Brief summary string
        """
        if "http" in module_type.lower():
            method = mapper.get("method", "GET")
            url = mapper.get("url", "Unknown URL")
            return f"{method} → {url}"
        elif "workfront" in module_type.lower():
            if "search" in module_type.lower():
                obj_code = mapper.get("object_code", "Unknown")
                return f"Search {obj_code} objects"
            elif "create" in module_type.lower():
                obj_code = mapper.get("object_code", "Unknown")
                return f"Create {obj_code} object"
            elif "update" in module_type.lower():
                obj_code = mapper.get("object_code", "Unknown")
                return f"Update {obj_code} object"
            elif "watch" in module_type.lower():
                return "Watch for events"
            else:
                return "Workfront operation"
        elif "router" in module_type.lower():
            return "Route data flow"
        elif "util" in module_type.lower() or "builtin" in module_type.lower():
            return "Utility operation"
        elif "datastore" in module_type.lower():
            return "Data storage operation"
        else:
            return f"{module_type} operation"
