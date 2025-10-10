"""
Flow tracer for Workfront Fusion blueprints - traces execution paths through scenarios
"""
import re
import json
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.tree import Tree
from rich.text import Text


@dataclass
class TraceStep:
    """Represents a single step in the execution trace."""
    module_id: int
    module_type: str
    label: str
    de_fields: List[str]
    variables_set: List[str]
    variables_read: List[str]
    external_calls: List[str]
    dynamic_values: List[str]
    filter_condition: Optional[str] = None
    route_name: Optional[str] = None
    depth: int = 0


class FlowTracer:
    """Traces execution flow through Workfront Fusion blueprint scenarios."""
    
    def __init__(self):
        self.console = Console()
        self.modules_by_id = {}  # id -> module data
        self.visited_modules = set()  # Track visited modules to prevent infinite loops
        self.trace_steps = []  # Complete trace history
        
    def trace_scenario(self, blueprint_data: Dict[str, Any], output_format: str = "tree") -> List[TraceStep]:
        """
        Trace the execution flow of a scenario.
        
        Args:
            blueprint_data: Parsed blueprint JSON
            output_format: "tree", "linear", or "json"
            
        Returns:
            List of TraceStep objects representing the execution flow
        """
        self.modules_by_id = {}
        self.visited_modules = set()
        self.trace_steps = []
        
        # Build module lookup by ID (including nested routes)
        self._build_module_index(blueprint_data)
        
        # Find the starting module (first in main flow)
        main_flow = blueprint_data.get('flow', [])
        if not main_flow:
            self.console.print("[red]No main flow found in blueprint[/red]")
            return []
        
        scenario_name = blueprint_data.get('name', 'Unknown Scenario')
        self.console.print(f"\n🔄 [bold blue]Tracing Execution Flow: {scenario_name}[/bold blue]\n")
        
        # Start tracing from first module
        starting_module = main_flow[0]
        self._trace_from_module(starting_module, main_flow, depth=0)
        
        # Output the trace
        if output_format == "tree":
            self._display_tree_trace()
        elif output_format == "linear":
            self._display_linear_trace()
        elif output_format == "json":
            self._display_json_trace()
        
        return self.trace_steps
    
    def _build_module_index(self, blueprint_data: Dict[str, Any]):
        """Build a lookup index of all modules by ID."""
        
        def index_modules(modules_list):
            for module in modules_list:
                module_id = module.get('id')
                if module_id:
                    self.modules_by_id[module_id] = module
                
                # Index nested route modules
                routes = module.get('routes', [])
                for route in routes:
                    route_flow = route.get('flow', [])
                    index_modules(route_flow)
                
                # Index error handler modules
                onerror = module.get('onerror', [])
                index_modules(onerror)
        
        main_flow = blueprint_data.get('flow', [])
        index_modules(main_flow)
    
    def _trace_from_module(self, module: Dict[str, Any], flow_context: List[Dict], depth: int = 0, route_name: Optional[str] = None, filter_condition: Optional[str] = None):
        """
        Recursively trace execution from a given module.
        
        Args:
            module: Current module to trace
            flow_context: The flow array this module belongs to
            depth: Nesting depth for display formatting
            route_name: Name of the route (for router branches)
            filter_condition: Filter condition (for conditional branches)
        """
        module_id = module.get('id')
        
        # Prevent infinite loops
        if module_id in self.visited_modules:
            return
        
        self.visited_modules.add(module_id)
        
        # Analyze the module
        trace_step = self._analyze_module(module, depth, route_name, filter_condition)
        self.trace_steps.append(trace_step)
        
        # Handle different module types
        module_type = module.get('module', 'unknown')
        
        if 'router' in module_type.lower():
            self._trace_router_branches(module, depth)
        else:
            # Find and trace next module in the current flow
            self._trace_next_module(module, flow_context, depth)
    
    def _analyze_module(self, module: Dict[str, Any], depth: int, route_name: Optional[str], filter_condition: Optional[str]) -> TraceStep:
        """Analyze a module and extract relevant information."""
        module_id = module.get('id', 0)
        module_type = module.get('module', 'unknown')
        
        # Get module label
        metadata = module.get('metadata', {})
        designer = metadata.get('designer', {})
        label = designer.get('name', module_type)
        
        # Find DE fields
        de_fields = self._find_de_fields(module)
        
        # Find variable operations
        variables_set, variables_read = self._find_variable_operations(module)
        
        # Find external calls
        external_calls = self._find_external_calls(module)
        
        # Find dynamic values
        dynamic_values = self._find_dynamic_values(module)
        
        return TraceStep(
            module_id=module_id,
            module_type=module_type,
            label=label,
            de_fields=de_fields,
            variables_set=variables_set,
            variables_read=variables_read,
            external_calls=external_calls,
            dynamic_values=dynamic_values,
            filter_condition=filter_condition,
            route_name=route_name,
            depth=depth
        )
    
    def _find_de_fields(self, module: Dict[str, Any]) -> List[str]:
        """Find all DE: field references in a module."""
        de_fields = set()
        module_json = json.dumps(module)
        
        # Find DE: field patterns
        de_pattern = r'"(DE:[^"]+)"'
        matches = re.findall(de_pattern, module_json)
        de_fields.update(matches)
        
        return sorted(list(de_fields))
    
    def _find_variable_operations(self, module: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Find variable set/read operations."""
        variables_set = []
        variables_read = []
        
        module_type = module.get('module', '')
        
        # Variables being set
        if 'setvariable' in module_type.lower():
            mapper = module.get('mapper', {})
            for key, value in mapper.items():
                if key not in ['__IMTMODULELOGGER__']:
                    variables_set.append(key)
        
        # Variables being read (look for {{variable}} patterns)
        module_json = json.dumps(module)
        var_pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(var_pattern, module_json)
        
        for match in matches:
            if '.' in match:  # Module data reference like {{1.ID}}
                continue
            variables_read.append(match)
        
        return sorted(list(set(variables_set))), sorted(list(set(variables_read)))
    
    def _find_external_calls(self, module: Dict[str, Any]) -> List[str]:
        """Find external HTTP/API calls."""
        external_calls = []
        module_type = module.get('module', '')
        
        if 'http' in module_type.lower():
            mapper = module.get('mapper', {})
            url = mapper.get('url', '')
            method = mapper.get('method', 'GET')
            if url:
                external_calls.append(f"{method} {url}")
        
        if 'email' in module_type.lower():
            external_calls.append("Email service")
        
        if 'workfront' in module_type.lower():
            external_calls.append("Workfront API")
        
        return external_calls
    
    def _find_dynamic_values(self, module: Dict[str, Any]) -> List[str]:
        """Find dynamic value references."""
        dynamic_values = []
        module_json = json.dumps(module)
        
        # Look for module data references
        ref_pattern = r'\{\{(\d+\.[^}]+)\}\}'
        matches = re.findall(ref_pattern, module_json)
        
        return sorted(list(set(matches)))
    
    def _trace_router_branches(self, router_module: Dict[str, Any], depth: int):
        """Trace all branches of a router module."""
        routes = router_module.get('routes', [])
        
        for i, route in enumerate(routes):
            route_flow = route.get('flow', [])
            if not route_flow:
                continue
            
            # Get first module of this route to check for filter
            first_module = route_flow[0]
            filter_condition = None
            route_name = f"Route {i + 1}"
            
            # Check if first module has a filter
            filter_data = first_module.get('filter', {})
            if filter_data:
                filter_name = filter_data.get('name', 'Unnamed condition')
                filter_condition = filter_name
                route_name = f"Route {i + 1}: {filter_name}"
            
            # Trace this route
            for module in route_flow:
                self._trace_from_module(module, route_flow, depth + 1, route_name, filter_condition)
    
    def _trace_next_module(self, current_module: Dict[str, Any], flow_context: List[Dict], depth: int):
        """Find and trace the next module in the flow."""
        current_id = current_module.get('id')
        
        # Find current module position in flow
        current_index = -1
        for i, module in enumerate(flow_context):
            if module.get('id') == current_id:
                current_index = i
                break
        
        # Trace next module if it exists
        if current_index >= 0 and current_index + 1 < len(flow_context):
            next_module = flow_context[current_index + 1]
            self._trace_from_module(next_module, flow_context, depth)
    
    def _display_tree_trace(self):
        """Display trace results in tree format."""
        if not self.trace_steps:
            return
        
        tree = Tree("🚀 [bold]Execution Flow[/bold]")
        current_branch = tree
        branch_stack = [tree]
        last_depth = 0
        
        for step in self.trace_steps:
            # Handle depth changes
            if step.depth > last_depth:
                # Going deeper - current node becomes parent
                pass
            elif step.depth < last_depth:
                # Going back up - pop from stack
                for _ in range(last_depth - step.depth):
                    if len(branch_stack) > 1:
                        branch_stack.pop()
                current_branch = branch_stack[-1]
            
            # Create node text
            node_text = self._format_step_text(step)
            
            # Add the node
            if step.route_name and step.depth > 0:
                # This is a route branch
                route_node = current_branch.add(f"🔀 [yellow]{step.route_name}[/yellow]")
                step_node = route_node.add(node_text)
                branch_stack.append(route_node)
                current_branch = route_node
            else:
                step_node = current_branch.add(node_text)
            
            last_depth = step.depth
        
        self.console.print(tree)
    
    def _display_linear_trace(self):
        """Display trace results in linear format."""
        for i, step in enumerate(self.trace_steps, 1):
            indent = "  " * step.depth
            prefix = f"{i}. " if step.depth == 0 else "└─ "
            
            step_text = self._format_step_text(step, include_emoji=False)
            self.console.print(f"{indent}{prefix}{step_text}")
            
            # Add route info if applicable
            if step.route_name and step.filter_condition:
                self.console.print(f"{indent}   [dim]// {step.filter_condition}[/dim]")
    
    def _display_json_trace(self):
        """Display trace results in JSON format."""
        trace_data = []
        for step in self.trace_steps:
            trace_data.append({
                'module_id': step.module_id,
                'module_type': step.module_type,
                'label': step.label,
                'de_fields': step.de_fields,
                'variables_set': step.variables_set,
                'variables_read': step.variables_read,
                'external_calls': step.external_calls,
                'dynamic_values': step.dynamic_values,
                'filter_condition': step.filter_condition,
                'route_name': step.route_name,
                'depth': step.depth
            })
        
        self.console.print(json.dumps(trace_data, indent=2))
    
    def _format_step_text(self, step: TraceStep, include_emoji: bool = True) -> Text:
        """Format a trace step for display."""
        emoji = "📦 " if include_emoji else ""
        text = Text()
        
        # Main module info
        text.append(f"{emoji}[{step.module_id}] ", style="cyan")
        text.append(f"{step.label}", style="bold")
        text.append(f" ({step.module_type})", style="dim")
        
        # Add annotations
        annotations = []
        
        if step.de_fields:
            annotations.append(f"DE fields: {', '.join(step.de_fields[:2])}{'...' if len(step.de_fields) > 2 else ''}")
        
        if step.variables_set:
            annotations.append(f"Sets: {', '.join(step.variables_set)}")
        
        if step.variables_read:
            annotations.append(f"Reads: {', '.join(step.variables_read)}")
        
        if step.external_calls:
            annotations.append("// external call")
        
        if step.dynamic_values:
            annotations.append("// dynamic value")
        
        if annotations:
            text.append(f"\n    {' | '.join(annotations)}", style="green")
        
        return text