"""
Cross-blueprint analysis functionality for corpus-wide insights
"""

import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..core.analyzer import BlueprintAnalyzer
from ..core.parser import BlueprintParser
from .connections import ConnectionAnalyzer


class CorpusAnalyzer:
    """Analyzes multiple blueprints together for patterns and insights."""

    def __init__(self):
        self.parser = BlueprintParser()
        self.analyzer = BlueprintAnalyzer()
        self.corpus_data = {}  # filename -> blueprint data
        self.all_modules = []  # All modules across all blueprints with metadata
        self.loaded = False

    def load_corpus(self, directory: Path):
        """Load all blueprint files and their modules."""
        self.corpus_data = {}
        self.all_modules = []

        # Recursively find all JSON files
        json_files = list(directory.rglob("*.json"))

        for json_file in json_files:
            try:
                blueprint_data = self.parser.load_blueprint(json_file)

                # Handle both direct flow and blueprint.flow structures
                data = blueprint_data
                if "blueprint" in data:
                    data = data["blueprint"]

                modules = self.parser.get_modules(data, include_orphans=True)

                # Create a unique key that includes relative path
                relative_path = json_file.relative_to(directory)
                blueprint_key = str(relative_path.with_suffix(""))  # Remove .json extension

                # Extract scenario name correctly for both structures
                if "blueprint" in blueprint_data:
                    scenario_name = blueprint_data["blueprint"].get("name", json_file.stem)
                else:
                    scenario_name = blueprint_data.get("name", json_file.stem)

                self.corpus_data[blueprint_key] = {
                    "filepath": json_file,
                    "data": blueprint_data,
                    "scenario_name": scenario_name,
                    "modules": modules,
                    "relative_path": relative_path,
                }

                # Add modules with corpus metadata
                for i, module in enumerate(modules):
                    module_with_metadata = {
                        "module_data": module,
                        "blueprint_file": blueprint_key,
                        "scenario_name": scenario_name,
                        "module_index": i,
                        "module_id": module.get("id", f"module_{i}"),
                        "module_type": module.get("module", "UNKNOWN"),
                    }
                    self.all_modules.append(module_with_metadata)

            except Exception as e:
                print(f"Warning: Could not load {json_file.name}: {e}")

        self.loaded = True

    def search_de_fields(self, field_pattern: str, exact_match: bool = False) -> List[Dict]:
        """
        Search for Workfront DE fields across all blueprints.

        Args:
            field_pattern: Field to search for (e.g., "DE:client_id")
            exact_match: If True, require exact match; if False, allow partial matches

        Returns:
            List of matches with module and blueprint context
        """
        if not self.loaded:
            raise ValueError("Corpus not loaded. Call load_corpus() first.")

        matches = []

        for module_info in self.all_modules:
            module = module_info["module_data"]
            de_fields = self.analyzer._find_workfront_fields(module)

            for field in de_fields:
                if exact_match:
                    if field == field_pattern:
                        matches.append(
                            {
                                "field": field,
                                "blueprint_file": module_info["blueprint_file"],
                                "scenario_name": module_info["scenario_name"],
                                "module_type": module_info["module_type"],
                                "module_id": module_info["module_id"],
                                "module_index": module_info["module_index"],
                            }
                        )
                else:
                    if field_pattern.lower() in field.lower():
                        matches.append(
                            {
                                "field": field,
                                "blueprint_file": module_info["blueprint_file"],
                                "scenario_name": module_info["scenario_name"],
                                "module_type": module_info["module_type"],
                                "module_id": module_info["module_id"],
                                "module_index": module_info["module_index"],
                            }
                        )

        return matches

    def search_module_types(self, type_pattern: str, exact_match: bool = False) -> List[Dict]:
        """
        Search for modules by type across all blueprints.

        Args:
            type_pattern: Module type to search for (e.g., "workfront" or "workfront-workfront:searchv3")
            exact_match: If True, require exact match; if False, allow partial matches

        Returns:
            List of matching modules with context
        """
        if not self.loaded:
            raise ValueError("Corpus not loaded. Call load_corpus() first.")

        matches = []

        for module_info in self.all_modules:
            module_type = module_info["module_type"]

            if exact_match:
                if module_type == type_pattern:
                    matches.append(self._create_module_match(module_info))
            else:
                if type_pattern.lower() in module_type.lower():
                    matches.append(self._create_module_match(module_info))

        return matches

    def search_text(self, search_text: str, case_sensitive: bool = False) -> List[Dict]:
        """
        Search for arbitrary text across all module data.

        Args:
            search_text: Text to search for
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            List of matches with context and location information
        """
        if not self.loaded:
            raise ValueError("Corpus not loaded. Call load_corpus() first.")

        matches = []

        for module_info in self.all_modules:
            module = module_info["module_data"]
            module_json = json.dumps(module)

            if case_sensitive:
                if search_text in module_json:
                    matches.append(self._create_text_match(module_info, search_text, module_json))
            else:
                if search_text.lower() in module_json.lower():
                    matches.append(self._create_text_match(module_info, search_text, module_json))

        return matches

    def get_de_field_rankings(self) -> List[Tuple[str, int, List[Dict]]]:
        """
        Get ranked list of DE fields by usage frequency.

        Returns:
            List of tuples: (field_name, count, usage_details)
        """
        if not self.loaded:
            raise ValueError("Corpus not loaded. Call load_corpus() first.")

        field_usage = defaultdict(list)

        for module_info in self.all_modules:
            module = module_info["module_data"]
            de_fields = self.analyzer._find_workfront_fields(module)

            for field in de_fields:
                # Handle comma-separated fields
                individual_fields = [f.strip() for f in field.split(",")]
                for individual_field in individual_fields:
                    if individual_field.startswith("DE:"):
                        field_usage[individual_field].append(
                            {
                                "blueprint_file": module_info["blueprint_file"],
                                "scenario_name": module_info["scenario_name"],
                                "module_type": module_info["module_type"],
                                "module_id": module_info["module_id"],
                            }
                        )

        # Sort by usage count (descending)
        ranked_fields = [(field, len(usages), usages) for field, usages in field_usage.items()]
        ranked_fields.sort(key=lambda x: x[1], reverse=True)

        return ranked_fields

    def get_module_type_rankings(self) -> List[Tuple[str, int, List[Dict]]]:
        """
        Get ranked list of module types by usage frequency.

        Returns:
            List of tuples: (module_type, count, usage_details)
        """
        if not self.loaded:
            raise ValueError("Corpus not loaded. Call load_corpus() first.")

        type_usage = defaultdict(list)

        for module_info in self.all_modules:
            module_type = module_info["module_type"]
            if module_type != "UNKNOWN":
                type_usage[module_type].append(
                    {
                        "blueprint_file": module_info["blueprint_file"],
                        "scenario_name": module_info["scenario_name"],
                        "module_id": module_info["module_id"],
                    }
                )

        # Sort by usage count (descending)
        ranked_types = [
            (module_type, len(usages), usages) for module_type, usages in type_usage.items()
        ]
        ranked_types.sort(key=lambda x: x[1], reverse=True)

        return ranked_types

    def detect_inconsistent_field_naming(self, similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Detect DE fields that might be variations of the same concept.

        Args:
            similarity_threshold: Similarity threshold for detecting variations (0.0-1.0)

        Returns:
            List of potential field naming inconsistencies
        """
        if not self.loaded:
            raise ValueError("Corpus not loaded. Call load_corpus() first.")

        # Get all unique DE fields
        all_fields = set()
        for module_info in self.all_modules:
            module = module_info["module_data"]
            de_fields = self.analyzer._find_workfront_fields(module)
            for field in de_fields:
                individual_fields = [f.strip() for f in field.split(",")]
                for individual_field in individual_fields:
                    if individual_field.startswith("DE:"):
                        all_fields.add(individual_field)

        all_fields = sorted(list(all_fields))
        inconsistencies = []
        processed = set()

        for i, field1 in enumerate(all_fields):
            if field1 in processed:
                continue

            similar_fields = [field1]
            processed.add(field1)

            for j, field2 in enumerate(all_fields[i + 1 :], i + 1):
                if field2 in processed:
                    continue

                # Calculate similarity (case-insensitive, ignoring DE: prefix)
                clean_field1 = field1[3:].lower()  # Remove DE: prefix
                clean_field2 = field2[3:].lower()  # Remove DE: prefix

                similarity = SequenceMatcher(None, clean_field1, clean_field2).ratio()

                if similarity >= similarity_threshold:
                    similar_fields.append(field2)
                    processed.add(field2)

            if len(similar_fields) > 1:
                inconsistencies.append(
                    {
                        "similar_fields": similar_fields,
                        "base_field": similar_fields[0],
                        "variations": similar_fields[1:],
                        "similarity_scores": [
                            SequenceMatcher(
                                None, similar_fields[0][3:].lower(), field[3:].lower()
                            ).ratio()
                            for field in similar_fields[1:]
                        ],
                    }
                )

        return inconsistencies

    def analyze_connections(self) -> Dict[str, Any]:
        """
        Analyze all connections used across blueprints using centralized ConnectionAnalyzer.

        Returns:
            Dictionary with connection analysis and environment warnings
        """
        if not self.loaded:
            raise ValueError("Corpus not loaded. Call load_corpus() first.")

        # Use centralized connection analyzer
        analyzer = ConnectionAnalyzer()

        # Aggregate data from all blueprints
        all_connections = defaultdict(list)
        all_connection_labels = {}
        all_connection_types = defaultdict(set)

        # Analyze each blueprint
        for blueprint_file, blueprint_data in self.corpus_data.items():
            scenario_name = blueprint_data.get("name", blueprint_file)

            # Get connection analysis for this blueprint
            blueprint_analysis = analyzer.analyze_blueprint_connections(
                blueprint_data, scenario_name
            )

            # Merge results
            for conn_id, usages in blueprint_analysis["connections"].items():
                for usage in usages:
                    # Convert to expected format for backward compatibility
                    connection_info = {
                        "blueprint_file": blueprint_file,
                        "scenario_name": usage["scenario_name"],
                        "module_type": usage["module_type"],
                        "module_id": f"module_{len(all_connections[conn_id])}",  # Generate simple ID
                        "connection_context": usage["context"],
                        "connection_type": usage["connection_type"],
                        "connection_label": blueprint_analysis["connection_labels"].get(
                            conn_id, f"Connection {conn_id}"
                        ),
                        "is_orphan": usage["is_orphan"],
                    }
                    all_connections[conn_id].append(connection_info)

            # Merge connection labels and types
            all_connection_labels.update(blueprint_analysis["connection_labels"])
            for conn_type, conn_ids in blueprint_analysis["connection_types"].items():
                all_connection_types[conn_type].update(conn_ids)

        # Generate environment warnings
        warnings = self._generate_connection_warnings(all_connection_types, all_connection_labels)

        return {
            "connections": dict(all_connections),
            "warnings": warnings,
            "connection_types": {k: list(v) for k, v in all_connection_types.items()},
            "connection_labels": all_connection_labels,
        }

    def _generate_connection_warnings(
        self, connection_types: Dict[str, Set[int]], connection_labels: Dict[int, str]
    ) -> List[Dict[str, Any]]:
        """
        Generate warnings for connection types with multiple instances.

        Args:
            connection_types: Dictionary mapping connection types to sets of connection IDs
            connection_labels: Dictionary mapping connection IDs to human-readable labels

        Returns:
            List of warning dictionaries
        """
        warnings = []

        for conn_type, connection_ids in connection_types.items():
            if len(connection_ids) > 1:
                # Include connection labels in the warning
                connection_details = []
                for conn_id in sorted(connection_ids):
                    label = connection_labels.get(conn_id, f"Connection {conn_id}")
                    connection_details.append(f"{label} (ID: {conn_id})")

                warnings.append(
                    {
                        "type": "multiple_connections",
                        "connection_type": conn_type,
                        "connection_count": len(connection_ids),
                        "connection_ids": sorted(list(connection_ids)),
                        "connection_details": connection_details,
                        "severity": "high" if conn_type == "Workfront" else "medium",
                        "message": f"Found {len(connection_ids)} different {conn_type} connections: {', '.join(connection_details)}. This may indicate multiple environments (dev/test/prod).",
                        "recommendation": f"Review {conn_type} connections to ensure they point to the correct environment for each scenario.",
                    }
                )

        return warnings

    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get overall corpus statistics."""
        if not self.loaded:
            raise ValueError("Corpus not loaded. Call load_corpus() first.")

        total_modules = len(self.all_modules)
        unique_module_types = len(set(m["module_type"] for m in self.all_modules))

        # Count unique DE fields
        all_de_fields = set()
        for module_info in self.all_modules:
            module = module_info["module_data"]
            de_fields = self.analyzer._find_workfront_fields(module)
            for field in de_fields:
                individual_fields = [f.strip() for f in field.split(",")]
                for individual_field in individual_fields:
                    if individual_field.startswith("DE:"):
                        all_de_fields.add(individual_field)

        return {
            "total_blueprints": len(self.corpus_data),
            "total_modules": total_modules,
            "unique_module_types": unique_module_types,
            "unique_de_fields": len(all_de_fields),
            "scenarios": [
                {
                    "filename": filename,
                    "scenario_name": info["scenario_name"],
                    "module_count": len(info["modules"]),
                }
                for filename, info in self.corpus_data.items()
            ],
        }

    def _create_module_match(self, module_info: Dict) -> Dict:
        """Create a standardized module match result."""
        return {
            "blueprint_file": module_info["blueprint_file"],
            "scenario_name": module_info["scenario_name"],
            "module_type": module_info["module_type"],
            "module_id": module_info["module_id"],
            "module_index": module_info["module_index"],
            "module_data": module_info["module_data"],
        }

    def _create_text_match(self, module_info: Dict, search_text: str, module_json: str) -> Dict:
        """Create a standardized text match result."""
        # Find the context around the match
        search_pos = module_json.lower().find(search_text.lower())
        context_start = max(0, search_pos - 50)
        context_end = min(len(module_json), search_pos + len(search_text) + 50)
        context = module_json[context_start:context_end]

        return {
            "blueprint_file": module_info["blueprint_file"],
            "scenario_name": module_info["scenario_name"],
            "module_type": module_info["module_type"],
            "module_id": module_info["module_id"],
            "module_index": module_info["module_index"],
            "search_text": search_text,
            "context": context,
            "match_position": search_pos,
        }
