"""
Live Scenario Walkthrough for Workfront Fusion blueprints
Interactive step-by-step exploration of scenario execution paths
"""

import json
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Platform-specific imports
try:
    import termios
    import tty
    KEYBOARD_INPUT_AVAILABLE = True
except ImportError:
    # Windows doesn't have termios
    KEYBOARD_INPUT_AVAILABLE = False

from InquirerPy import inquirer
from InquirerPy.separator import Separator
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from .connections import ConnectionAnalyzer


@dataclass
class FlowStep:
    """Represents a single step in the live scenario walkthrough."""

    module_id: Any  # Can be int for modules or string for filter cards
    module_type: str
    module_name: str
    description: str
    parameters: Dict[str, Any]
    mapper: Dict[str, Any]
    de_fields: List[str]
    next_modules: List[int]
    previous_modules: List[int]
    is_router: bool = False
    is_error_handler: bool = False
    is_filter_card: bool = False  # New flag for filter cards
    router_branches: List[Dict] = None
    depth: int = 0
    raw_module_data: Dict[str, Any] = None
    # Enhanced fields
    connection_info: Dict[str, Any] = None
    input_mappings: List[str] = None
    output_variables: List[str] = None
    filter_conditions: List[str] = None
    key_parameters: Dict[str, Any] = None
    variables_used: List[str] = None
    external_references: List[str] = None
    # Module-specific contextual fields
    search_criteria: Dict[str, Any] = None
    operation_details: Dict[str, Any] = None
    webhook_config: Dict[str, Any] = None
    data_transformation: List[str] = None
    error_handling: Dict[str, Any] = None
    # Filter-specific fields
    filter_details: Dict[str, Any] = None


class FlowWalker:
    """Interactive live scenario walkthrough for step-by-step scenario exploration."""

    def __init__(self):
        self.console = Console()
        self.modules_by_id = {}
        self.flow_steps = []
        self.current_step_index = 0
        self.scenario_name = ""
        self.path_history = []  # Track the path taken through branches
        self.branch_points = {}  # Map step indices to available branches
        self.keyboard_available = True  # Will be set during initialization

    def start_walkthrough(self, blueprint_data: Dict[str, Any]):
        """Start the interactive live scenario walkthrough."""
        self.scenario_name = blueprint_data.get("name", "Unknown Scenario")

        # Build the flow structure
        self._build_flow_structure(blueprint_data)

        if not self.flow_steps:
            self.console.print("[red]No modules found for live walkthrough.[/red]")
            return

        # Welcome message
        self._display_welcome()

        # Start the interactive live walkthrough
        self._interactive_live_walkthrough()

    def _build_flow_structure(self, blueprint_data: Dict[str, Any]):
        """Build the flow structure for live walkthrough."""
        self.modules_by_id = {}
        self.flow_steps = []
        self.branch_points = {}

        # First, index all modules by ID recursively
        self._index_all_modules(blueprint_data.get("flow", []))

        # Build main flow steps (routers will be handled specially)
        self._build_main_flow_steps(blueprint_data.get("flow", []))

    def _index_all_modules(self, flow_modules: List[Dict[str, Any]]):
        """Recursively index all modules by ID."""
        for module in flow_modules:
            module_id = module.get("id")
            if module_id:
                self.modules_by_id[module_id] = module

                # Index nested route modules
                if "routes" in module:
                    for route in module["routes"]:
                        self._index_all_modules(route.get("flow", []))

    def _build_main_flow_steps(self, flow_modules: List[Dict[str, Any]], depth: int = 0):
        """Build the main flow steps, handling routers specially and including filter cards."""
        for i, module in enumerate(flow_modules):
            module_id = module.get("id")
            if not module_id:
                continue

            # Determine next modules (for non-routers)
            next_modules = []
            if i + 1 < len(flow_modules):
                next_id = flow_modules[i + 1].get("id")
                if next_id:
                    next_modules.append(next_id)

            # Determine previous modules
            previous_modules = []
            if i > 0:
                prev_id = flow_modules[i - 1].get("id")
                if prev_id:
                    previous_modules.append(prev_id)

            # Create flow step
            step = self._create_flow_step(module, next_modules, previous_modules, depth)
            current_step_index = len(self.flow_steps)
            self.flow_steps.append(step)

            # Check if this module has significant filter conditions that determine whether the NEXT module executes
            # The filter card should appear AFTER this module but BEFORE the next module
            filter_card = self._create_filter_card_if_needed(module, i)
            if filter_card:
                # Update the filter card to show it controls the next module
                if next_modules:
                    filter_card.next_modules = next_modules
                    filter_card.description = (
                        f"Conditions that must be met for Module {next_modules[0]} to execute"
                    )
                self.flow_steps.append(filter_card)

            # If this is a router, record branch points
            if step.is_router and module.get("routes"):
                self.branch_points[current_step_index] = {"branches": [], "module_data": module}

                # Build branches for this router
                for route in module["routes"]:
                    branch_info = {
                        "name": route.get("name", "Unnamed Route"),
                        "filter": route.get("filter", "No filter"),
                        "modules": route.get("flow", []),
                        "first_module_id": (
                            route.get("flow", [{}])[0].get("id") if route.get("flow") else None
                        ),
                    }
                    self.branch_points[current_step_index]["branches"].append(branch_info)

    def _create_flow_step(
        self,
        module: Dict[str, Any],
        next_modules: List[int],
        previous_modules: List[int],
        depth: int,
    ) -> FlowStep:
        """Create a FlowStep from module data."""
        module_id = module.get("id", 0)
        module_type = module.get("module", "Unknown")

        # Generate module name and description
        module_name = self._generate_module_name(module)
        description = self._generate_module_description(module)

        # Extract parameters and mapper
        parameters = module.get("parameters", {})
        mapper = module.get("mapper", {})

        # Find DE fields
        de_fields = self._extract_de_fields(module)

        # Extract enhanced information
        connection_info = self._extract_connection_info(module)
        input_mappings = self._extract_input_mappings(module)
        output_variables = self._extract_output_variables(module)
        filter_conditions = self._extract_filter_conditions(module)
        key_parameters = self._extract_key_parameters(module)
        variables_used = self._extract_variables_used(module)
        external_references = self._extract_external_references(module)

        # Extract module-specific contextual information
        search_criteria = self._extract_search_criteria(module)
        operation_details = self._extract_operation_details(module)
        webhook_config = self._extract_webhook_config(module)
        data_transformation = self._extract_data_transformation(module)
        error_handling = self._extract_error_handling(module)

        # Check if this is a router
        is_router = "router" in module_type.lower() or bool(module.get("routes"))
        is_error_handler = module.get("type") == "onerror"

        # Extract router branches if applicable
        router_branches = []
        if is_router and module.get("routes"):
            for route in module["routes"]:
                branch_info = {
                    "name": route.get("name", "Unnamed Route"),
                    "filter": route.get("filter", "No filter"),
                    "module_count": len(route.get("flow", [])),
                }
                router_branches.append(branch_info)

        return FlowStep(
            module_id=module_id,
            module_type=module_type,
            module_name=module_name,
            description=description,
            parameters=parameters,
            mapper=mapper,
            de_fields=de_fields,
            next_modules=next_modules,
            previous_modules=previous_modules,
            is_router=is_router,
            is_error_handler=is_error_handler,
            router_branches=router_branches,
            depth=depth,
            raw_module_data=module,
            connection_info=connection_info,
            input_mappings=input_mappings,
            output_variables=output_variables,
            filter_conditions=filter_conditions,
            key_parameters=key_parameters,
            variables_used=variables_used,
            external_references=external_references,
            search_criteria=search_criteria,
            operation_details=operation_details,
            webhook_config=webhook_config,
            data_transformation=data_transformation,
            error_handling=error_handling,
        )

    def _generate_module_name(self, module: Dict[str, Any]) -> str:
        """Generate a readable name for the module."""
        # First check if user has set a custom name in metadata.designer.name
        metadata = module.get("metadata", {})
        designer = metadata.get("designer", {})
        custom_name = designer.get("name")

        if custom_name:
            return custom_name

        # Fall back to generating name from module type
        module_type = module.get("module", "Unknown")

        # Try to get a descriptive name based on module type
        if "workfront" in module_type.lower():
            action = module_type.split(":")[-1] if ":" in module_type else module_type
            return f"Workfront {action.title()}"
        elif "webhook" in module_type.lower():
            return "Webhook Trigger"
        elif "router" in module_type.lower():
            return "Router"
        elif "datastore" in module_type.lower():
            return "Data Store Operation"
        elif "tools" in module_type.lower():
            return "Tools Operation"
        else:
            # Extract service and action
            parts = module_type.split("-")
            if len(parts) >= 2:
                service = parts[0].title()
                action = parts[-1].split(":")[-1] if ":" in parts[-1] else parts[-1]
                return f"{service} {action.title()}"
            return module_type.title()

    def _generate_module_description(self, module: Dict[str, Any]) -> str:
        """Generate a description of what the module does."""
        module_type = module.get("module", "").lower()
        parameters = module.get("parameters", {})

        if "search" in module_type:
            obj_type = parameters.get("objType", {}).get("value", "objects")
            return f"Search for {obj_type} in Workfront"
        elif "create" in module_type:
            obj_type = parameters.get("objType", {}).get("value", "object")
            return f"Create new {obj_type} in Workfront"
        elif "update" in module_type:
            return "Update existing Workfront object"
        elif "webhook" in module_type:
            return "Listen for incoming webhook triggers"
        elif "router" in module_type:
            route_count = len(module.get("routes", []))
            return (
                f"Route execution to {route_count} different path{'s' if route_count != 1 else ''}"
            )
        elif "datastore" in module_type:
            return "Perform data store operation"
        else:
            return f"Execute {module_type} operation"

    def _extract_de_fields(self, module: Dict[str, Any]) -> List[str]:
        """Extract DE fields from module configuration."""
        module_str = json.dumps(module)

        # Find all DE: field references
        import re

        de_pattern = re.compile(r"DE:[a-zA-Z0-9_]+")
        matches = de_pattern.findall(module_str)

        # Remove duplicates and return
        return list(set(matches))

    def _extract_connection_info(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract connection information from module using centralized analyzer."""
        # Use centralized connection analyzer for more comprehensive detection
        analyzer = ConnectionAnalyzer()
        connections = analyzer.find_connections_in_json(module)

        if connections:
            connection_id, context = connections[0]  # Take first connection found
            module_type = module.get("module", "")
            connection_type = analyzer.determine_connection_type(module_type, "", context)

            return {
                "connection_id": connection_id,
                "connection_type": connection_type,
                "context": context,
            }

        return None

    def _extract_input_mappings(self, module: Dict[str, Any]) -> List[str]:
        """Extract key input mappings from module mapper."""
        mappings = []
        mapper = module.get("mapper", {})

        if not mapper:
            return mappings

        # Extract top-level mappings (limit to most important ones)
        for key, value in list(mapper.items())[:5]:  # Limit to first 5
            if isinstance(value, dict):
                # Look for mapped values
                if "value" in value:
                    mappings.append(
                        f"{key}: {str(value['value'])[:30]}{'...' if len(str(value['value'])) > 30 else ''}"
                    )
                elif "name" in value:
                    mappings.append(f"{key}: {{{{value['name']}}}}")
            elif isinstance(value, str) and value:
                mappings.append(f"{key}: {value[:30]}{'...' if len(value) > 30 else ''}")

        return mappings

    def _extract_output_variables(self, module: Dict[str, Any]) -> List[str]:
        """Extract output variables that this module creates."""
        variables = []

        # Look in metadata for output variables
        metadata = module.get("metadata", {})
        if "expect" in metadata:
            for expect_item in metadata["expect"]:
                if isinstance(expect_item, dict) and "name" in expect_item:
                    variables.append(expect_item["name"])

        # Also look for common output patterns in module type
        module_type = module.get("module", "").lower()
        if "create" in module_type:
            variables.append("Created object ID")
        elif "search" in module_type:
            variables.append("Search results")
        elif "update" in module_type:
            variables.append("Updated object data")

        return variables[:3]  # Limit to 3 most important

    def _extract_filter_conditions(self, module: Dict[str, Any]) -> List[str]:
        """Extract filter conditions from module."""
        conditions = []

        # Check for filter in parameters
        parameters = module.get("parameters", {})
        if "filter" in parameters:
            filter_value = parameters["filter"]
            if isinstance(filter_value, dict) and "value" in filter_value:
                conditions.append(
                    str(filter_value["value"])[:50] + "..."
                    if len(str(filter_value["value"])) > 50
                    else str(filter_value["value"])
                )
            elif isinstance(filter_value, str):
                conditions.append(
                    filter_value[:50] + "..." if len(filter_value) > 50 else filter_value
                )

        # Check for other conditional parameters
        for key, value in parameters.items():
            if "condition" in key.lower() or "where" in key.lower():
                if isinstance(value, dict) and "value" in value:
                    conditions.append(
                        f"{key}: {str(value['value'])[:40]}{'...' if len(str(value['value'])) > 40 else ''}"
                    )

        return conditions[:2]  # Limit to 2 conditions

    def _extract_key_parameters(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the most important parameters for display."""
        parameters = module.get("parameters", {})
        key_params = {}

        # Define important parameter keys to look for
        important_keys = [
            "objType",
            "objId",
            "action",
            "method",
            "url",
            "query",
            "recordType",
            "operation",
            "value",
            "field",
            "limit",
        ]

        for key in important_keys:
            if key in parameters:
                value = parameters[key]
                if isinstance(value, dict) and "value" in value:
                    key_params[key] = value["value"]
                elif not isinstance(value, dict):
                    key_params[key] = value

                # Limit to 3 key parameters
                if len(key_params) >= 3:
                    break

        return key_params if key_params else None

    def _extract_variables_used(self, module: Dict[str, Any]) -> List[str]:
        """Extract variables referenced in this module."""
        variables = set()
        module_str = json.dumps(module)

        # Find variable references like {{variable_name}}
        var_pattern = re.compile(r"\\{\\{([^}]+)\\}\\}")
        matches = var_pattern.findall(module_str)

        for match in matches:
            # Clean up variable names
            var_name = match.strip()
            if "." in var_name:
                # Take the base variable name before the dot
                var_name = var_name.split(".")[0]
            variables.add(var_name)

            # Limit to 4 variables
            if len(variables) >= 4:
                break

        return list(variables)

    def _extract_external_references(self, module: Dict[str, Any]) -> List[str]:
        """Extract external system references (URLs, APIs, etc.)."""
        references = []
        module_str = json.dumps(module)

        # Look for URLs
        url_pattern = re.compile(r"https?://[^\s\"\\}]+")
        urls = url_pattern.findall(module_str)

        for url in urls[:2]:  # Limit to 2 URLs
            # Shorten long URLs
            if len(url) > 40:
                references.append(url[:37] + "...")
            else:
                references.append(url)

        # Look for API endpoints in parameters
        parameters = module.get("parameters", {})
        for key, value in parameters.items():
            if "endpoint" in key.lower() or "api" in key.lower():
                if isinstance(value, dict) and "value" in value:
                    ref_value = str(value["value"])
                    if ref_value and not ref_value.startswith("http"):
                        references.append(
                            f"API: {ref_value[:30]}{'...' if len(ref_value) > 30 else ''}"
                        )

        return references[:2]  # Limit to 2 references

    def _extract_search_criteria(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract search-specific criteria for search modules."""
        module_type = module.get("module", "").lower()
        if "search" not in module_type:
            return None

        parameters = module.get("parameters", {})
        search_info = {}

        # Object type being searched
        if "objType" in parameters:
            obj_type = parameters["objType"]
            if isinstance(obj_type, dict) and "value" in obj_type:
                search_info["object_type"] = obj_type["value"]
            else:
                search_info["object_type"] = obj_type

        # Search fields/query
        search_fields = []
        for key, value in parameters.items():
            if key.lower() in ["query", "search", "where", "filter"]:
                if isinstance(value, dict) and "value" in value:
                    search_fields.append(
                        f"{key}: {str(value['value'])[:40]}{'...' if len(str(value['value'])) > 40 else ''}"
                    )
                elif isinstance(value, str):
                    search_fields.append(f"{key}: {value[:40]}{'...' if len(value) > 40 else ''}")

        # Limit and ordering
        if "limit" in parameters:
            limit_val = parameters["limit"]
            if isinstance(limit_val, dict) and "value" in limit_val:
                search_info["limit"] = limit_val["value"]
            else:
                search_info["limit"] = limit_val

        if "orderBy" in parameters:
            order_val = parameters["orderBy"]
            if isinstance(order_val, dict) and "value" in order_val:
                search_info["order_by"] = order_val["value"]

        # Fields to return
        if "fields" in parameters:
            fields_val = parameters["fields"]
            if isinstance(fields_val, dict) and "value" in fields_val:
                if isinstance(fields_val["value"], list):
                    search_info["fields"] = ", ".join(fields_val["value"][:5])
                    if len(fields_val["value"]) > 5:
                        search_info["fields"] += f' (+{len(fields_val["value"]) - 5} more)'

        if search_fields:
            search_info["search_fields"] = search_fields

        return search_info if search_info else None

    def _extract_operation_details(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract operation-specific details based on module type."""
        module_type = module.get("module", "").lower()
        parameters = module.get("parameters", {})
        operation_info = {}

        # Create operations
        if "create" in module_type:
            if "objType" in parameters:
                obj_type = parameters["objType"]
                if isinstance(obj_type, dict) and "value" in obj_type:
                    operation_info["creating"] = obj_type["value"]

            # Get mapped fields for creation
            mapper = module.get("mapper", {})
            create_fields = []
            for key, value in list(mapper.items())[:4]:  # First 4 fields
                if isinstance(value, dict) and "value" in value:
                    create_fields.append(
                        f"{key}: {str(value['value'])[:30]}{'...' if len(str(value['value'])) > 30 else ''}"
                    )
                elif isinstance(value, str):
                    create_fields.append(f"{key}: {value[:30]}{'...' if len(value) > 30 else ''}")
            if create_fields:
                operation_info["create_fields"] = create_fields

        # Update operations
        elif "update" in module_type:
            if "objType" in parameters:
                obj_type = parameters["objType"]
                if isinstance(obj_type, dict) and "value" in obj_type:
                    operation_info["updating"] = obj_type["value"]

            if "objId" in parameters:
                obj_id = parameters["objId"]
                if isinstance(obj_id, dict) and "value" in obj_id:
                    operation_info["target_id"] = str(obj_id["value"])[:20]

        # Delete operations
        elif "delete" in module_type:
            if "objType" in parameters:
                obj_type = parameters["objType"]
                if isinstance(obj_type, dict) and "value" in obj_type:
                    operation_info["deleting"] = obj_type["value"]

        # HTTP requests
        elif "http" in module_type:
            if "method" in parameters:
                method = parameters["method"]
                if isinstance(method, dict) and "value" in method:
                    operation_info["http_method"] = method["value"]

            if "url" in parameters:
                url = parameters["url"]
                if isinstance(url, dict) and "value" in url:
                    operation_info["endpoint"] = (
                        str(url["value"])[:50] + "..."
                        if len(str(url["value"])) > 50
                        else str(url["value"])
                    )

        # Data store operations
        elif "datastore" in module_type:
            if "operation" in parameters:
                op = parameters["operation"]
                if isinstance(op, dict) and "value" in op:
                    operation_info["ds_operation"] = op["value"]

            if "recordType" in parameters:
                record_type = parameters["recordType"]
                if isinstance(record_type, dict) and "value" in record_type:
                    operation_info["record_type"] = record_type["value"]

        return operation_info if operation_info else None

    def _extract_webhook_config(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract webhook-specific configuration."""
        module_type = module.get("module", "").lower()
        if "webhook" not in module_type and "trigger" not in module_type:
            return None

        parameters = module.get("parameters", {})
        webhook_info = {}

        # Webhook URL
        if "url" in parameters:
            url = parameters["url"]
            if isinstance(url, dict) and "value" in url:
                webhook_info["webhook_url"] = (
                    str(url["value"])[:40] + "..."
                    if len(str(url["value"])) > 40
                    else str(url["value"])
                )

        # HTTP method
        if "method" in parameters:
            method = parameters["method"]
            if isinstance(method, dict) and "value" in method:
                webhook_info["method"] = method["value"]

        # Headers
        if "headers" in parameters:
            webhook_info["has_headers"] = True

        # Authentication
        if "auth" in parameters or "authentication" in parameters:
            webhook_info["has_auth"] = True

        # Expected structure
        metadata = module.get("metadata", {})
        if "expect" in metadata:
            expected_fields = []
            for expect_item in metadata["expect"][:3]:  # First 3 expected fields
                if isinstance(expect_item, dict) and "name" in expect_item:
                    expected_fields.append(expect_item["name"])
            if expected_fields:
                webhook_info["expects"] = ", ".join(expected_fields)

        return webhook_info if webhook_info else None

    def _extract_data_transformation(self, module: Dict[str, Any]) -> List[str]:
        """Extract data transformation operations."""
        transformations = []
        module_type = module.get("module", "").lower()

        # Look for transformation indicators
        if "transform" in module_type or "tools" in module_type:
            parameters = module.get("parameters", {})

            # Formula or expression
            if "formula" in parameters:
                formula = parameters["formula"]
                if isinstance(formula, dict) and "value" in formula:
                    transformations.append(
                        f"Formula: {str(formula['value'])[:40]}{'...' if len(str(formula['value'])) > 40 else ''}"
                    )

            # Text operations
            if "operation" in parameters:
                op = parameters["operation"]
                if isinstance(op, dict) and "value" in op:
                    transformations.append(f"Operation: {op['value']}")

        # Look for aggregation operations
        mapper = module.get("mapper", {})
        if mapper:
            for key, value in mapper.items():
                if isinstance(value, dict):
                    if "function" in value:
                        transformations.append(f"{key}: {value['function']}")
                    elif "expression" in value:
                        expr = str(value["expression"])[:30]
                        transformations.append(
                            f"{key}: {expr}{'...' if len(str(value['expression'])) > 30 else ''}"
                        )

        return transformations[:3]  # Limit to 3 transformations

    def _extract_error_handling(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract error handling configuration."""
        error_info = {}

        # Check if this is an error handler
        if module.get("type") == "onerror":
            error_info["is_error_handler"] = True

            # Get error handling action
            parameters = module.get("parameters", {})
            if "action" in parameters:
                action = parameters["action"]
                if isinstance(action, dict) and "value" in action:
                    error_info["action"] = action["value"]

        # Check for retry configuration
        if "retry" in str(module):
            error_info["has_retry"] = True

        # Check for fallback configuration
        if "fallback" in str(module):
            error_info["has_fallback"] = True

        return error_info if error_info else None

    def _create_filter_card_if_needed(
        self, module: Dict[str, Any], index: int
    ) -> Optional[FlowStep]:
        """Create a separate filter card if the module has significant filter conditions."""
        filter_details = self._extract_comprehensive_filter_info(module)

        if not filter_details or not self._should_create_filter_card(filter_details):
            return None

        # Create a special filter card step
        return FlowStep(
            module_id=f"filter_{module.get('id', index)}",
            module_type="filter_card",
            module_name="Filter Checkpoint",
            description="Filter conditions that control whether the next module executes",
            parameters={},
            mapper={},
            de_fields=[],
            next_modules=[],  # Will be updated in _build_main_flow_steps
            previous_modules=[],
            is_filter_card=True,
            filter_details=filter_details,
        )

    def _extract_comprehensive_filter_info(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive filter information from a module."""
        filter_info = {}
        parameters = module.get("parameters", {})

        # Check for filter parameter
        if "filter" in parameters:
            filter_value = parameters["filter"]
            if isinstance(filter_value, dict):
                if "value" in filter_value:
                    filter_info["main_condition"] = str(filter_value["value"])
                if "name" in filter_value:
                    filter_info["condition_name"] = filter_value["name"]
            elif isinstance(filter_value, str) and filter_value.strip():
                filter_info["main_condition"] = filter_value

        # Check for where clauses
        if "where" in parameters:
            where_value = parameters["where"]
            if isinstance(where_value, dict) and "value" in where_value:
                filter_info["where_clause"] = str(where_value["value"])
            elif isinstance(where_value, str):
                filter_info["where_clause"] = where_value

        # Check for conditional parameters
        conditional_params = []
        for key, value in parameters.items():
            if any(
                word in key.lower()
                for word in ["condition", "criteria", "constraint", "requirement"]
            ):
                if isinstance(value, dict) and "value" in value:
                    conditional_params.append(f"{key}: {str(value['value'])[:60]}")
                elif isinstance(value, str) and value.strip():
                    conditional_params.append(f"{key}: {value[:60]}")

        if conditional_params:
            filter_info["conditional_parameters"] = conditional_params

        # Extract logical operators and complex conditions
        module_str = json.dumps(module)

        # Look for logical operators
        logical_patterns = ["AND", "OR", "NOT", "&&", "||", "!="]
        found_operators = []
        for op in logical_patterns:
            if op in module_str:
                found_operators.append(op)

        if found_operators:
            filter_info["logical_operators"] = list(set(found_operators))

        # Look for comparison operators
        comparison_patterns = [">=", "<=", ">", "<", "==", "!=", "LIKE", "IN", "CONTAINS"]
        found_comparisons = []
        for comp in comparison_patterns:
            if comp in module_str:
                found_comparisons.append(comp)

        if found_comparisons:
            filter_info["comparison_operators"] = list(set(found_comparisons))

        # Check for date/time filters
        date_keywords = [
            "date",
            "time",
            "created",
            "updated",
            "modified",
            "entryDate",
            "plannedCompletionDate",
        ]
        date_filters = []
        for keyword in date_keywords:
            if keyword in module_str.lower():
                date_filters.append(keyword)

        if date_filters:
            filter_info["date_filters"] = list(set(date_filters))

        # Check for status/state filters
        status_keywords = ["status", "state", "progress", "condition", "approved", "active"]
        status_filters = []
        for keyword in status_keywords:
            if keyword in module_str.lower():
                status_filters.append(keyword)

        if status_filters:
            filter_info["status_filters"] = list(set(status_filters))

        # Extract field-based filters
        field_filters = []
        for field in self._extract_de_fields(module):
            # Check if this DE field appears in filter contexts
            field_str = field.replace("DE:", "")
            filter_content = str(parameters.get("filter", {}).get("value", ""))
            if field in filter_content or field_str in filter_content:
                field_filters.append(field)

        if field_filters:
            filter_info["field_filters"] = field_filters

        return filter_info

    def _should_create_filter_card(self, filter_details: Dict[str, Any]) -> bool:
        """Determine if filter details are significant enough to warrant a separate card."""
        if not filter_details:
            return False

        # Create filter card if any of these conditions are met:
        significant_conditions = [
            "main_condition" in filter_details and len(filter_details["main_condition"]) > 20,
            "where_clause" in filter_details,
            len(filter_details.get("conditional_parameters", [])) > 1,
            len(filter_details.get("logical_operators", [])) > 0,
            len(filter_details.get("comparison_operators", [])) > 2,
            len(filter_details.get("field_filters", [])) > 0,
        ]

        return any(significant_conditions)

    def _display_welcome(self):
        """Display welcome message for the live scenario walkthrough."""
        welcome_text = f"""🎥 [bold blue]Live Scenario Walkthrough: {self.scenario_name}[/bold blue]

You're about to experience this scenario step-by-step, module by module.
At each step, you'll see what the module does and how it's configured.

[bold green]Navigation:[/bold green] Use ← → arrow keys to move between modules
[dim]Or press 'm' for traditional menu, 'd' for details, 'q' to quit[/dim]

[dim]Total modules to explore: {len(self.flow_steps)}[/dim]"""

        panel = Panel(
            welcome_text, title="🎥 Live Scenario Walkthrough", border_style="blue", expand=False
        )

        self.console.print()
        self.console.print(panel)
        self.console.print()

        # Test if keyboard input is available
        self.keyboard_available = self._test_keyboard_input()
        if not self.keyboard_available:
            self.console.print(
                "[yellow]Arrow key navigation not available on this system. Using traditional menu.[/yellow]"
            )

        input("Press Enter to start the live walkthrough...")

    def _interactive_live_walkthrough(self):
        """Main interactive live walkthrough loop."""
        while True:
            try:
                current_step = self.flow_steps[self.current_step_index]

                # Display current step
                self._display_current_step(current_step)

                # Get user action via keyboard input or fallback to menu
                if self.keyboard_available:
                    action = self._handle_keyboard_input()
                else:
                    action = self._get_user_action_fallback()

                if action == "next":
                    # Check if current step is a router with branches
                    if self.current_step_index in self.branch_points:
                        branch_choice = self._handle_router_branching()
                        if branch_choice is not None:
                            self._follow_branch(branch_choice)
                    elif self.current_step_index < len(self.flow_steps) - 1:
                        self.current_step_index += 1
                    else:
                        self._display_live_walkthrough_complete()
                        break
                elif action == "back":
                    if self.current_step_index > 0:
                        self.current_step_index -= 1
                elif action == "jump":
                    new_index = self._select_step_to_jump_to()
                    if new_index is not None:
                        self.current_step_index = new_index
                elif action == "details":
                    self._show_detailed_view(current_step)
                elif action == "restart":
                    self.current_step_index = 0
                elif action == "exit":
                    break

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Live walkthrough interrupted.[/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[red]Error during keyboard input: {e}[/red]")
                # Fall back to menu system if keyboard input fails
                action = self._get_user_action_fallback()
                if action == "exit":
                    break

    def _display_current_step(self, step: FlowStep):
        """Display the current step information."""
        self.console.clear()

        # Progress indicator
        progress = f"Step {self.current_step_index + 1} of {len(self.flow_steps)}"
        progress_bar = "█" * (self.current_step_index + 1) + "░" * (
            len(self.flow_steps) - self.current_step_index - 1
        )

        self.console.print(f"\n[dim]{progress}[/dim]")
        self.console.print(f"[blue]{progress_bar[:50]}[/blue]\n")

        # Handle filter cards differently
        if step.is_filter_card:
            self._display_filter_card(step)
            return

        # Module header
        indent = "  " * step.depth
        step_title = f"{indent}📦 {step.module_name}"
        if step.is_router:
            step_title += " 🔀"
        elif step.is_error_handler:
            step_title += " ⚠️"

        # Main content
        content = f"[bold]{step_title}[/bold]\n\n"
        content += f"[dim]Type:[/dim] {step.module_type}\n"
        content += f"[dim]ID:[/dim] {step.module_id}\n\n"
        content += f"[green]{step.description}[/green]\n"

        # Connection information
        if step.connection_info:
            conn_type = step.connection_info.get("connection_type", "Unknown")
            conn_id = step.connection_info.get("connection_id", "N/A")
            content += f"\n[dim]Connection:[/dim] [blue]{conn_type}[/blue] (ID: {conn_id})\n"

        # Key parameters
        if step.key_parameters:
            content += f"\n[dim]Key Parameters:[/dim]\n"
            for key, value in step.key_parameters.items():
                content += f"  • [cyan]{key}:[/cyan] {str(value)[:30]}{'...' if len(str(value)) > 30 else ''}\n"

        # Input mappings
        if step.input_mappings:
            content += f"\n[dim]Input Mappings:[/dim]\n"
            for mapping in step.input_mappings[:3]:  # Show first 3
                content += f"  • [magenta]{mapping}[/magenta]\n"
            if len(step.input_mappings) > 3:
                content += f"  • [dim]... and {len(step.input_mappings) - 3} more[/dim]\n"

        # Variables used
        if step.variables_used:
            content += f"\n[dim]Variables Used:[/dim] "
            var_display = ", ".join(
                [f"{{{{[bright_yellow]{var}[/bright_yellow]}}}}" for var in step.variables_used[:4]]
            )
            content += f"{var_display}\n"
            if len(step.variables_used) > 4:
                content += f"[dim]... and {len(step.variables_used) - 4} more[/dim]\n"

        # Output variables
        if step.output_variables:
            content += f"\n[dim]Creates:[/dim] [bright_green]{', '.join(step.output_variables)}[/bright_green]\n"

        # Filter conditions
        if step.filter_conditions:
            content += f"\n[dim]Conditions:[/dim]\n"
            for condition in step.filter_conditions:
                content += f"  • [bright_red]{condition}[/bright_red]\n"

        # External references
        if step.external_references:
            content += f"\n[dim]External References:[/dim]\n"
            for ref in step.external_references:
                content += f"  • [blue]{ref}[/blue]\n"

        # Module-specific contextual information

        # Search criteria for search modules
        if step.search_criteria:
            content += f"\n[bold bright_blue]🔍 Search Configuration:[/bold bright_blue]\n"
            if "object_type" in step.search_criteria:
                content += f"  • [bright_cyan]Object Type:[/bright_cyan] {step.search_criteria['object_type']}\n"
            if "search_fields" in step.search_criteria:
                content += f"  • [bright_cyan]Search Criteria:[/bright_cyan]\n"
                for field in step.search_criteria["search_fields"]:
                    content += f"    - {field}\n"
            if "limit" in step.search_criteria:
                content += f"  • [bright_cyan]Limit:[/bright_cyan] {step.search_criteria['limit']} results\n"
            if "order_by" in step.search_criteria:
                content += (
                    f"  • [bright_cyan]Order By:[/bright_cyan] {step.search_criteria['order_by']}\n"
                )
            if "fields" in step.search_criteria:
                content += f"  • [bright_cyan]Return Fields:[/bright_cyan] {step.search_criteria['fields']}\n"

        # Operation details for CRUD operations
        if step.operation_details:
            content += f"\n[bold bright_magenta]⚙️ Operation Details:[/bold bright_magenta]\n"
            if "creating" in step.operation_details:
                content += f"  • [bright_magenta]Creating:[/bright_magenta] {step.operation_details['creating']} object\n"
                if "create_fields" in step.operation_details:
                    content += f"  • [bright_magenta]Fields Being Set:[/bright_magenta]\n"
                    for field in step.operation_details["create_fields"]:
                        content += f"    - {field}\n"
            elif "updating" in step.operation_details:
                content += f"  • [bright_magenta]Updating:[/bright_magenta] {step.operation_details['updating']} object\n"
                if "target_id" in step.operation_details:
                    content += f"  • [bright_magenta]Target ID:[/bright_magenta] {step.operation_details['target_id']}\n"
            elif "deleting" in step.operation_details:
                content += f"  • [bright_magenta]Deleting:[/bright_magenta] {step.operation_details['deleting']} object\n"
            elif "http_method" in step.operation_details:
                content += f"  • [bright_magenta]HTTP Method:[/bright_magenta] {step.operation_details['http_method']}\n"
                if "endpoint" in step.operation_details:
                    content += f"  • [bright_magenta]Endpoint:[/bright_magenta] {step.operation_details['endpoint']}\n"
            elif "ds_operation" in step.operation_details:
                content += f"  • [bright_magenta]Data Store Operation:[/bright_magenta] {step.operation_details['ds_operation']}\n"
                if "record_type" in step.operation_details:
                    content += f"  • [bright_magenta]Record Type:[/bright_magenta] {step.operation_details['record_type']}\n"

        # Webhook configuration
        if step.webhook_config:
            content += f"\n[bold bright_green]🔗 Webhook Configuration:[/bold bright_green]\n"
            if "webhook_url" in step.webhook_config:
                content += (
                    f"  • [bright_green]URL:[/bright_green] {step.webhook_config['webhook_url']}\n"
                )
            if "method" in step.webhook_config:
                content += (
                    f"  • [bright_green]Method:[/bright_green] {step.webhook_config['method']}\n"
                )
            if "expects" in step.webhook_config:
                content += (
                    f"  • [bright_green]Expects:[/bright_green] {step.webhook_config['expects']}\n"
                )
            if step.webhook_config.get("has_headers"):
                content += f"  • [bright_green]Custom Headers:[/bright_green] Configured\n"
            if step.webhook_config.get("has_auth"):
                content += f"  • [bright_green]Authentication:[/bright_green] Configured\n"

        # Data transformation
        if step.data_transformation:
            content += f"\n[bold bright_yellow]🔄 Data Transformations:[/bold bright_yellow]\n"
            for transform in step.data_transformation:
                content += f"  • [bright_yellow]{transform}[/bright_yellow]\n"

        # Error handling
        if step.error_handling:
            content += f"\n[bold red]⚠️ Error Handling:[/bold red]\n"
            if step.error_handling.get("is_error_handler"):
                content += f"  • [red]Error Handler Module[/red]\n"
                if "action" in step.error_handling:
                    content += f"  • [red]Action:[/red] {step.error_handling['action']}\n"
            if step.error_handling.get("has_retry"):
                content += f"  • [red]Retry Configuration:[/red] Enabled\n"
            if step.error_handling.get("has_fallback"):
                content += f"  • [red]Fallback Logic:[/red] Configured\n"

        # DE Fields (moved to end, condensed)
        if step.de_fields:
            de_display = ", ".join(step.de_fields[:4])
            if len(step.de_fields) > 4:
                de_display += f" (+{len(step.de_fields) - 4} more)"
            content += f"\n[dim]Workfront Fields:[/dim] [yellow]{de_display}[/yellow]\n"

        # Router branches - enhanced display
        if step.is_router and self.current_step_index in self.branch_points:
            branch_info = self.branch_points[self.current_step_index]
            branches = branch_info["branches"]
            content += f"\n[bold yellow]🔀 Branching Point - {len(branches)} Path{'s' if len(branches) != 1 else ''}:[/bold yellow]\n"
            for i, branch in enumerate(branches, 1):
                module_count = len(branch["modules"])
                content += f"  {i}. [cyan]{branch['name']}[/cyan] ({module_count} modules)\n"
                if branch["filter"] and branch["filter"] != "No filter":
                    filter_preview = (
                        branch["filter"][:40] + "..."
                        if len(branch["filter"]) > 40
                        else branch["filter"]
                    )
                    content += f"     [dim]Condition: {filter_preview}[/dim]\n"
            content += (
                f"\n[bold green]➡️  Choose 'Next' to select which path to explore![/bold green]"
            )

        # Flow context - enhanced for routers
        if not (step.is_router and self.current_step_index in self.branch_points):
            context_parts = []
            if step.previous_modules:
                context_parts.append(f"← From: {', '.join(map(str, step.previous_modules))}")
            if step.next_modules:
                context_parts.append(f"Next: {', '.join(map(str, step.next_modules))} →")

            if context_parts:
                content += f"\n[dim]Flow: {' | '.join(context_parts)}[/dim]"

        # Show path history if we've made branch choices
        if self.path_history:
            content += f"\n[dim]Path taken:[/dim]"
            for choice in self.path_history[-2:]:  # Show last 2 branch choices
                content += f" → [yellow]{choice['branch_name']}[/yellow]"

        # Choose border style based on module type
        if step.is_router and self.current_step_index in self.branch_points:
            border_style = "yellow"  # Highlight branching points
            title_prefix = "🔀 "
        elif step.is_error_handler:
            border_style = "red"
            title_prefix = "⚠️  "
        else:
            border_style = "green"
            title_prefix = ""

        panel = Panel(
            content,
            title=f"{title_prefix}Module {step.module_id}",
            border_style=border_style,
            expand=False,
        )

        self.console.print(panel)

        # Show navigation instructions
        nav_instructions = self._get_navigation_instructions()
        if nav_instructions:
            self.console.print(f"[dim]{nav_instructions}[/dim]")
        self.console.print()

    def _display_filter_card(self, step: FlowStep):
        """Display a filter card with detailed filter conditions."""
        filter_details = step.filter_details
        if not filter_details:
            return

        # Build filter card content
        content = f"[bold bright_blue]🔍 Filter Conditions[/bold bright_blue]\n\n"

        # Show which module this filter controls
        if step.next_modules:
            content += (
                f"[bright_blue]Controls execution of Module {step.next_modules[0]}[/bright_blue]\n"
            )
            content += f"[bright_blue]These conditions must be satisfied for the next module to execute:[/bright_blue]\n\n"
        else:
            content += f"[bright_blue]These conditions must be satisfied for execution to continue:[/bright_blue]\n\n"

        # Main condition
        if "main_condition" in filter_details:
            content += f"[bold bright_white]Primary Condition:[/bold bright_white]\n"
            condition_text = filter_details["main_condition"]
            # Break long conditions into readable chunks
            if len(condition_text) > 80:
                content += f"[bright_yellow]{condition_text[:80]}[/bright_yellow]\n"
                content += f"[bright_yellow]{condition_text[80:]}[/bright_yellow]\n"
            else:
                content += f"[bright_yellow]{condition_text}[/bright_yellow]\n"
            content += "\n"

        # Condition name if available
        if "condition_name" in filter_details:
            content += (
                f"[dim]Condition Name:[/dim] [cyan]{filter_details['condition_name']}[/cyan]\n\n"
            )

        # Where clause
        if "where_clause" in filter_details:
            content += f"[bold bright_white]Where Clause:[/bold bright_white]\n"
            content += f"[bright_yellow]{filter_details['where_clause']}[/bright_yellow]\n\n"

        # Conditional parameters
        if "conditional_parameters" in filter_details:
            content += f"[bold bright_white]Additional Conditions:[/bold bright_white]\n"
            for param in filter_details["conditional_parameters"]:
                content += f"  • [bright_cyan]{param}[/bright_cyan]\n"
            content += "\n"

        # Logical operators
        if "logical_operators" in filter_details:
            operators = ", ".join(filter_details["logical_operators"])
            content += f"[dim]Logical Operators:[/dim] [magenta]{operators}[/magenta]\n"

        # Comparison operators
        if "comparison_operators" in filter_details:
            comparisons = ", ".join(filter_details["comparison_operators"])
            content += f"[dim]Comparison Operators:[/dim] [magenta]{comparisons}[/magenta]\n"

        # Date filters
        if "date_filters" in filter_details:
            date_fields = ", ".join(filter_details["date_filters"])
            content += f"[dim]Date/Time Fields:[/dim] [green]{date_fields}[/green]\n"

        # Status filters
        if "status_filters" in filter_details:
            status_fields = ", ".join(filter_details["status_filters"])
            content += f"[dim]Status Fields:[/dim] [green]{status_fields}[/green]\n"

        # Field filters
        if "field_filters" in filter_details:
            content += f"\n[bold bright_white]Workfront Fields Used:[/bold bright_white]\n"
            for field in filter_details["field_filters"]:
                content += f"  • [yellow]{field}[/yellow]\n"

        # Add explanation
        if step.next_modules:
            content += f"\n[dim]💡 This filter determines if Module {step.next_modules[0]} will execute.[/dim]\n"
            content += f"[dim]   Only data that meets these conditions will proceed to the next module.[/dim]"
        else:
            content += f"\n[dim]💡 This filter evaluates before the next module executes.[/dim]\n"
            content += f"[dim]   Only data that meets these conditions will proceed.[/dim]"

        # Create panel with special styling for filter cards
        panel = Panel(
            content, title="🔍 Filter Checkpoint", border_style="bright_blue", expand=False
        )

        self.console.print(panel)

        # Show navigation instructions for filter cards
        nav_instructions = self._get_navigation_instructions()
        if nav_instructions:
            self.console.print(f"[dim]{nav_instructions}[/dim]")
        self.console.print()

    def _get_user_action(self) -> str:
        """Get the next action from the user."""
        choices = []
        self.flow_steps[self.current_step_index]

        # Navigation options
        if self.current_step_index in self.branch_points:
            # This is a router - show branching option
            branch_count = len(self.branch_points[self.current_step_index]["branches"])
            choices.append(
                {"name": f"🔀 Choose branch path ({branch_count} options)", "value": "next"}
            )
        elif self.current_step_index < len(self.flow_steps) - 1:
            choices.append({"name": "➡️  Next module", "value": "next"})
        else:
            choices.append({"name": "🏁 Complete live walkthrough", "value": "next"})

        if self.current_step_index > 0:
            choices.append({"name": "⬅️  Previous module", "value": "back"})

        choices.extend(
            [
                {"name": "🔍 Show detailed configuration", "value": "details"},
                {"name": "🦘 Jump to specific module", "value": "jump"},
                Separator(),
                {"name": "🔄 Restart from beginning", "value": "restart"},
                {"name": "❌ Exit live walkthrough", "value": "exit"},
            ]
        )

        return inquirer.select(message="What would you like to do?", choices=choices).execute()

    def _show_detailed_view(self, step: FlowStep):
        """Show detailed configuration for the current step."""
        self.console.print("\n[bold]📋 Detailed Configuration[/bold]\n")

        # Parameters
        if step.parameters:
            self.console.print("[bold]Parameters:[/bold]")
            syntax = Syntax(
                json.dumps(step.parameters, indent=2), "json", theme="monokai", line_numbers=True
            )
            self.console.print(syntax)
            self.console.print()

        # Mapper
        if step.mapper:
            self.console.print("[bold]Input Mappings:[/bold]")
            syntax = Syntax(
                json.dumps(step.mapper, indent=2), "json", theme="monokai", line_numbers=True
            )
            self.console.print(syntax)

        input("\nPress Enter to continue...")

    def _select_step_to_jump_to(self) -> Optional[int]:
        """Allow user to select a specific step to jump to."""
        choices = []

        for i, step in enumerate(self.flow_steps):
            indent = "  " * step.depth
            name = f"{indent}{i + 1}. {step.module_name}"
            if step.is_router:
                name += " 🔀"
            choices.append({"name": name, "value": i})

        choices.append(Separator())
        choices.append({"name": "← Back to current step", "value": None})

        return inquirer.select(message="Jump to which step?", choices=choices).execute()

    def _display_live_walkthrough_complete(self):
        """Display live walkthrough completion message."""
        completion_text = f"""🎉 [bold green]Live Scenario Walkthrough Complete![/bold green]

You've successfully completed the live walkthrough of all {len(self.flow_steps)} modules in:
[bold]{self.scenario_name}[/bold]

[dim]You now have a complete understanding of how this scenario flows from start to finish.[/dim]"""

        panel = Panel(
            completion_text,
            title="✅ Live Scenario Walkthrough Complete",
            border_style="green",
            expand=False,
        )

        self.console.print()
        self.console.print(panel)
        self.console.print()

        # Ask what to do next
        next_action = inquirer.select(
            message="What would you like to do next?",
            choices=[
                {"name": "🔄 Live walkthrough scenario again", "value": "restart"},
                {"name": "❌ Exit", "value": "exit"},
            ],
        ).execute()

        if next_action == "restart":
            self.current_step_index = 0
            self.path_history = []
            self._interactive_live_walkthrough()

    def _handle_router_branching(self) -> Optional[int]:
        """Handle router branching by letting user choose a path."""
        branch_info = self.branch_points[self.current_step_index]
        branches = branch_info["branches"]

        if not branches:
            return None

        self.console.print(f"\n🔀 [bold yellow]Router Branching Point[/bold yellow]")
        self.console.print(
            "This router can send execution down different paths based on conditions.\n"
        )

        # Show available branches
        choices = []
        for i, branch in enumerate(branches):
            module_count = len(branch["modules"])
            name = f"🔀 {branch['name']}"
            if branch["filter"] and branch["filter"] != "No filter":
                name += f" [dim]({branch['filter'][:50]}{'...' if len(branch['filter']) > 50 else ''})[/dim]"
            name += f" - {module_count} module{'s' if module_count != 1 else ''}"

            choices.append({"name": name, "value": i})

        choices.extend(
            [
                Separator(),
                {"name": "🏠 Skip branching (continue main flow)", "value": "skip"},
                {"name": "← Back to router", "value": "back"},
            ]
        )

        selection = inquirer.select(
            message="Which branch would you like to explore?", choices=choices
        ).execute()

        if selection == "back":
            return None
        elif selection == "skip":
            # Continue to next module in main flow
            if self.current_step_index < len(self.flow_steps) - 1:
                self.current_step_index += 1
            return None
        else:
            return selection

    def _follow_branch(self, branch_index: int):
        """Follow a specific branch path."""
        branch_info = self.branch_points[self.current_step_index]
        selected_branch = branch_info["branches"][branch_index]

        # Record this choice in path history
        self.path_history.append(
            {
                "router_step": self.current_step_index,
                "branch_name": selected_branch["name"],
                "branch_index": branch_index,
            }
        )

        # Build steps for this branch
        branch_modules = selected_branch["modules"]
        if not branch_modules:
            self.console.print(
                "[yellow]This branch has no modules. Continuing to next main flow module.[/yellow]"
            )
            input("Press Enter to continue...")
            if self.current_step_index < len(self.flow_steps) - 1:
                self.current_step_index += 1
            return

        # Start branch live walkthrough
        self._live_walkthrough_branch(branch_modules, selected_branch["name"])

    def _live_walkthrough_branch(self, branch_modules: List[Dict[str, Any]], branch_name: str):
        """Live walkthrough modules in a specific branch."""
        self.console.print(f"\n🔀 [bold green]Entering Branch: {branch_name}[/bold green]")
        input("Press Enter to start live walkthrough of this branch...")

        branch_steps = []

        # Build branch steps
        for i, module in enumerate(branch_modules):
            next_modules = []
            if i + 1 < len(branch_modules):
                next_id = branch_modules[i + 1].get("id")
                if next_id:
                    next_modules.append(next_id)

            previous_modules = []
            if i > 0:
                prev_id = branch_modules[i - 1].get("id")
                if prev_id:
                    previous_modules.append(prev_id)

            step = self._create_flow_step(module, next_modules, previous_modules, depth=1)
            branch_steps.append(step)

        # Live walkthrough branch steps
        branch_step_index = 0
        while branch_step_index < len(branch_steps):
            try:
                current_branch_step = branch_steps[branch_step_index]

                # Display branch step
                self._display_branch_step(
                    current_branch_step, branch_step_index, len(branch_steps), branch_name
                )

                # Get branch action via keyboard input or fallback to menu
                if self.keyboard_available:
                    action = self._handle_keyboard_input_branch(
                        branch_step_index, len(branch_steps)
                    )
                else:
                    action = self._get_branch_action(branch_step_index, len(branch_steps))

                if action == "next":
                    branch_step_index += 1
                elif action == "back":
                    if branch_step_index > 0:
                        branch_step_index -= 1
                elif action == "details":
                    self._show_detailed_view(current_branch_step)
                elif action == "exit_branch":
                    break

            except KeyboardInterrupt:
                break

        # Branch completed
        self.console.print(f"\n✅ [bold green]Completed Branch: {branch_name}[/bold green]")

        # Ask what to do next
        next_action = inquirer.select(
            message="Branch live walkthrough complete. What would you like to do?",
            choices=[
                {"name": "↩️ Return to main flow", "value": "return"},
                {"name": "🔄 Live walkthrough branch again", "value": "repeat"},
                {"name": "❌ Exit live walkthrough", "value": "exit"},
            ],
        ).execute()

        if next_action == "repeat":
            self._live_walkthrough_branch(branch_modules, branch_name)
        elif next_action == "return":
            # Continue to next module in main flow
            if self.current_step_index < len(self.flow_steps) - 1:
                self.current_step_index += 1
        # If exit, the main loop will handle it

    def _display_branch_step(
        self, step: FlowStep, step_index: int, total_steps: int, branch_name: str
    ):
        """Display a step within a branch."""
        self.console.clear()

        # Branch progress indicator
        progress = f"Branch Step {step_index + 1} of {total_steps}"
        progress_bar = "█" * (step_index + 1) + "░" * (total_steps - step_index - 1)

        self.console.print(f"\n🔀 [bold cyan]Branch: {branch_name}[/bold cyan]")
        self.console.print(f"[dim]{progress}[/dim]")
        self.console.print(f"[cyan]{progress_bar[:50]}[/cyan]\n")

        # Module content (reuse existing display logic)
        indent = "  " * (step.depth + 1)  # Extra indent for branch
        step_title = f"{indent}📦 {step.module_name}"
        if step.is_router:
            step_title += " 🔀"
        elif step.is_error_handler:
            step_title += " ⚠️"

        content = f"[bold]{step_title}[/bold]\n\n"
        content += f"[dim]Type:[/dim] {step.module_type}\n"
        content += f"[dim]ID:[/dim] {step.module_id}\n\n"
        content += f"[green]{step.description}[/green]\n"

        # DE Fields
        if step.de_fields:
            content += f"\n[dim]Workfront Fields:[/dim]\n"
            for field in step.de_fields[:5]:
                content += f"  • [yellow]{field}[/yellow]\n"
            if len(step.de_fields) > 5:
                content += f"  • [dim]... and {len(step.de_fields) - 5} more[/dim]\n"

        # Flow context within branch
        context_parts = []
        if step.previous_modules:
            context_parts.append(f"← From: {', '.join(map(str, step.previous_modules))}")
        if step.next_modules:
            context_parts.append(f"Next: {', '.join(map(str, step.next_modules))} →")

        if context_parts:
            content += f"\n[dim]Branch Flow: {' | '.join(context_parts)}[/dim]"

        panel = Panel(
            content, title=f"Branch Module {step.module_id}", border_style="cyan", expand=False
        )

        self.console.print(panel)

        # Show navigation instructions for branch
        nav_instructions = self._get_branch_navigation_instructions(step_index, total_steps)
        if nav_instructions:
            self.console.print(f"[dim]{nav_instructions}[/dim]")
        self.console.print()

    def _get_branch_action(self, step_index: int, total_steps: int) -> str:
        """Get user action within a branch."""
        choices = []

        if step_index < total_steps - 1:
            choices.append({"name": "➡️ Next module in branch", "value": "next"})
        else:
            choices.append({"name": "✅ Complete branch", "value": "next"})

        if step_index > 0:
            choices.append({"name": "⬅️ Previous module in branch", "value": "back"})

        choices.extend(
            [
                {"name": "🔍 Show detailed configuration", "value": "details"},
                Separator(),
                {"name": "↩️ Exit branch (return to main flow)", "value": "exit_branch"},
            ]
        )

        return inquirer.select(
            message="What would you like to do in this branch?", choices=choices
        ).execute()

    def _get_navigation_instructions(self) -> str:
        """Get navigation instructions based on current state."""
        instructions = []

        # Arrow key navigation
        if self.current_step_index > 0:
            instructions.append("← Left arrow: Previous module")

        if self.current_step_index in self.branch_points:
            instructions.append("→ Right arrow: Choose branch")
        elif self.current_step_index < len(self.flow_steps) - 1:
            instructions.append("→ Right arrow: Next module")
        else:
            instructions.append("→ Right arrow: Complete walkthrough")

        # Other keys
        instructions.extend(["d: Details", "j: Jump to module", "r: Restart", "m: Menu", "q: Quit"])

        return " | ".join(instructions)

    def _get_keyboard_input(self) -> str:
        """Get a single keyboard input without requiring Enter."""
        if not KEYBOARD_INPUT_AVAILABLE:
            # Fallback for Windows
            return input().lower().strip() or "enter"
            
        try:
            # Save terminal settings
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                # Set terminal to raw mode
                tty.setraw(sys.stdin.fileno())

                # Read a single character
                char = sys.stdin.read(1)

                # Handle special keys (arrow keys send escape sequences)
                if char == "\x1b":  # ESC sequence
                    char += sys.stdin.read(2)  # Read the rest of the escape sequence
                    if char == "\x1b[C":  # Right arrow
                        return "right"
                    elif char == "\x1b[D":  # Left arrow
                        return "left"
                    elif char == "\x1b[A":  # Up arrow
                        return "up"
                    elif char == "\x1b[B":  # Down arrow
                        return "down"

                return char.lower()

            finally:
                # Restore terminal settings
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        except (KeyboardInterrupt, EOFError):
            return "q"  # Treat Ctrl+C or EOF as quit
        except Exception:
            # Fallback for systems that don't support raw input
            return input().lower().strip() or "enter"

    def _handle_keyboard_input(self) -> str:
        """Handle keyboard input and return action."""
        while True:
            key = self._get_keyboard_input()

            # Arrow key navigation
            if key == "right":
                if self.current_step_index in self.branch_points:
                    return "next"  # Will trigger branch selection
                elif self.current_step_index < len(self.flow_steps) - 1:
                    return "next"
                else:
                    return "next"  # Complete walkthrough
            elif key == "left":
                if self.current_step_index > 0:
                    return "back"
                else:
                    self.console.print("[yellow]Already at first module[/yellow]")
                    continue

            # Letter keys
            elif key == "d":
                return "details"
            elif key == "j":
                return "jump"
            elif key == "r":
                return "restart"
            elif key == "q":
                return "exit"
            elif key in ["\r", "\n", "enter"]:  # Enter key
                # Default to next action
                return "next"
            elif key == "m":
                # Show traditional menu
                return self._get_user_action_fallback()
            else:
                # Show help for invalid keys
                self.console.print(
                    f"[yellow]Unknown key '{key}'. Use arrow keys or 'm' for menu.[/yellow]"
                )
                continue

    def _get_branch_navigation_instructions(self, step_index: int, total_steps: int) -> str:
        """Get navigation instructions for branch walkthrough."""
        instructions = []

        # Arrow key navigation
        if step_index > 0:
            instructions.append("← Left arrow: Previous module")

        if step_index < total_steps - 1:
            instructions.append("→ Right arrow: Next module")
        else:
            instructions.append("→ Right arrow: Complete branch")

        # Other keys
        instructions.extend(["d: Details", "m: Menu", "q: Exit branch"])

        return " | ".join(instructions)

    def _handle_keyboard_input_branch(self, step_index: int, total_steps: int) -> str:
        """Handle keyboard input for branch navigation."""
        while True:
            key = self._get_keyboard_input()

            # Arrow key navigation
            if key == "right":
                if step_index < total_steps - 1:
                    return "next"
                else:
                    return "next"  # Complete branch
            elif key == "left":
                if step_index > 0:
                    return "back"
                else:
                    self.console.print("[yellow]Already at first module in branch[/yellow]")
                    continue

            # Letter keys
            elif key == "d":
                return "details"
            elif key == "q":
                return "exit_branch"
            elif key in ["\r", "\n", "enter"]:  # Enter key
                # Default to next action
                return "next"
            elif key == "m":
                # Show traditional menu
                return self._get_branch_action(step_index, total_steps)
            else:
                # Show help for invalid keys
                self.console.print(
                    f"[yellow]Unknown key '{key}'. Use arrow keys, 'd' for details, 'q' to exit branch, or 'm' for menu.[/yellow]"
                )
                continue

    def _get_user_action_fallback(self) -> str:
        """Fallback to traditional menu system."""
        choices = []
        self.flow_steps[self.current_step_index]

        # Navigation options
        if self.current_step_index in self.branch_points:
            # This is a router - show branching option
            branch_count = len(self.branch_points[self.current_step_index]["branches"])
            choices.append(
                {"name": f"🔀 Choose branch path ({branch_count} options)", "value": "next"}
            )
        elif self.current_step_index < len(self.flow_steps) - 1:
            choices.append({"name": "➡️  Next module", "value": "next"})
        else:
            choices.append({"name": "🏁 Complete live walkthrough", "value": "next"})

        if self.current_step_index > 0:
            choices.append({"name": "⬅️  Previous module", "value": "back"})

        choices.extend(
            [
                {"name": "🔍 Show detailed configuration", "value": "details"},
                {"name": "🦘 Jump to specific module", "value": "jump"},
                Separator(),
                {"name": "🔄 Restart from beginning", "value": "restart"},
                {"name": "❌ Exit live walkthrough", "value": "exit"},
            ]
        )

        return inquirer.select(
            message="What would you like to do? (Use arrow keys for quick navigation)",
            choices=choices,
        ).execute()

    def _test_keyboard_input(self) -> bool:
        """Test if keyboard input functionality is available."""
        if not KEYBOARD_INPUT_AVAILABLE:
            return False
        try:
            # Quick test to see if we can access terminal settings
            fd = sys.stdin.fileno()
            termios.tcgetattr(fd)
            return True
        except Exception:
            # Fall back to traditional menu if keyboard input not available
            return False
