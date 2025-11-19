"""
AI-powered landscape analysis for cross-blueprint queries
Production-ready version with improved token management, error handling, and configurability
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..services.openai_service import get_openai_service


@dataclass
class BlueprintSummary:
    """Condensed blueprint information for AI analysis"""

    name: str
    filename: str
    modules: List[Dict[str, Any]]
    connections: List[str]
    module_count: int
    app_types: List[str]


class AILandscapeAnalyzer:
    """Production-ready analyzer for cross-blueprint AI queries"""

    def __init__(
        self, blueprints: Dict[str, Any], detail_level: str = "balanced", model_type: str = "auto"
    ):
        self.blueprints = blueprints
        self.detail_level = detail_level  # "minimal", "balanced", "detailed"
        self.model_type = model_type  # "auto", "fast", "standard", "thinking"
        self.max_context_tokens = self._get_token_limit()
        self.token_divisor = 3.3
        self.max_retries = 2  # Faster failure
        self.retry_delay = 0.5
        self.deterministic = True  # Default to consistent results
        self.openai_service = get_openai_service()

    def _get_token_limit(self) -> int:
        """Adjust token limits based on detail level"""
        limits = {
            "minimal": 8000,  # Aggressive compression
            "balanced": 12000,  # Moderate detail
            "detailed": 16000,  # Maximum detail before chunking
        }
        return limits.get(self.detail_level, 12000)

    def _extract_blueprint_summary(self, blueprint_data: Dict[str, Any]) -> BlueprintSummary:
        """Extract key information from a blueprint - optimized for context efficiency"""
        from ..core.parser import BlueprintParser

        scenario_name = blueprint_data.get("scenario_name", "Unknown")
        filename = blueprint_data.get("filename", "Unknown")
        raw_data = blueprint_data.get("data", {})

        # Reuse existing parser
        parser = BlueprintParser()
        all_modules = parser.get_modules(raw_data, include_orphans=True)

        # 🔧 OPTIMIZATION: Cap module detail to essential fields only
        modules = []
        connections = set()
        app_types = set()

        for module in all_modules:
            # Adaptive detail based on setting
            if self.detail_level == "minimal":
                # Minimal info for large datasets
                module_info = {
                    "module": module.get("module", "unknown"),
                    "label": (module.get("metadata", {}).get("label", "") or "")[:30],
                }
            elif self.detail_level == "detailed":
                # Maximum detail for thorough analysis
                module_info = {
                    "id": module.get("id", "unknown"),
                    "module": module.get("module", "unknown"),
                    "label": (module.get("metadata", {}).get("label", "") or "")[:100],
                    "parameters": self._extract_key_parameters(module),
                    "routes": len(module.get("routes", [])),
                    "has_error_handler": bool(module.get("onerror", [])),
                }
            else:  # balanced
                # Standard detail level
                module_info = {
                    "id": module.get("id", "unknown"),
                    "module": module.get("module", "unknown"),
                    "label": (module.get("metadata", {}).get("label", "") or "")[:70],
                }

            modules.append(module_info)

            # Extract app type from module name
            module_name = module_info["module"]
            if ":" in module_name:
                app_type = module_name.split(":")[0]
                app_types.add(app_type)

            # Extract connection info with more detail if needed
            connection = module.get("connection")
            if connection:
                if self.detail_level == "detailed":
                    connections.add(str(connection)[:50])
                else:
                    connections.add(str(connection)[:20])

        # Adaptive capping based on detail level
        name_limit = {"minimal": 50, "balanced": 100, "detailed": 150}
        filename_limit = {"minimal": 30, "balanced": 50, "detailed": 80}

        return BlueprintSummary(
            name=scenario_name[: name_limit[self.detail_level]],
            filename=filename[: filename_limit[self.detail_level]],
            modules=modules,
            connections=list(connections),
            module_count=len(modules),
            app_types=list(app_types),
        )

    def _extract_key_parameters(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key parameters that provide business context"""
        parameters = {}

        # Look for common business-relevant parameters
        module_params = module.get("parameters", {})
        if isinstance(module_params, dict):
            # Extract fields that often contain business context
            business_keys = [
                "filter",
                "condition",
                "status",
                "assignee",
                "priority",
                "project",
                "task",
                "document",
                "proof",
                "approval",
                "notification",
                "email",
                "message",
                "subject",
            ]

            for key, value in module_params.items():
                key_lower = str(key).lower()
                if any(biz_key in key_lower for biz_key in business_keys):
                    # Truncate long values but keep business context
                    if isinstance(value, str) and len(value) > 100:
                        parameters[key] = value[:100] + "..."
                    else:
                        parameters[key] = value

        return parameters

    def _chunk_data_adaptively(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Adaptive chunking with progressive module detail reduction"""
        context_json = json.dumps(context_data, indent=2)
        estimated_tokens = self.openai_service.estimate_tokens(context_json)

        if estimated_tokens <= self.max_context_tokens:
            return [context_data]

        # If too large, progressively reduce detail
        scenarios = context_data["scenarios"]

        # First attempt: Remove module metadata but keep counts
        if estimated_tokens > self.max_context_tokens * 1.5:
            for scenario in scenarios:
                # Keep only essential module info for large datasets
                scenario["modules"] = [
                    {"module": m["module"], "label": m["label"][:20]}
                    for m in scenario["modules"][:20]  # Cap to 20 modules per scenario
                ]
                # Add truncation indicator
                if len(scenario["modules"]) == 20:
                    scenario["modules"].append(
                        {
                            "module": "...",
                            "label": f"(+{scenario['module_count'] - 20} more modules)",
                        }
                    )

        # Chunk scenarios
        chunk_size = max(1, len(scenarios) // ((estimated_tokens // self.max_context_tokens) + 1))

        chunks = []
        for i in range(0, len(scenarios), chunk_size):
            chunk_scenarios = scenarios[i : i + chunk_size]
            chunk = {
                "total_scenarios": context_data["total_scenarios"],
                "chunk_info": f"Chunk {len(chunks) + 1}: {len(chunk_scenarios)} of {len(scenarios)} scenarios",
                "scenarios": chunk_scenarios,
                "summary_stats": context_data["summary_stats"],
            }
            chunks.append(chunk)

        return chunks

    def _load_system_prompt(self) -> str:
        """Load system prompt from configurable template"""
        prompt_file = Path(__file__).parent / "prompts" / "business_analysis.txt"

        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")

        # Fallback to embedded prompt
        return """You are a business automation consultant specializing in Workfront Fusion impact analysis.

ANALYSIS FRAMEWORK:
- Identify which scenarios use specific apps, modules, or features
- Assess business impact of system changes (field renames, deprecations, etc.)
- Map integration dependencies and risk levels
- Categorize usage patterns across automation landscape

OUTPUT FORMAT:
1. **Executive Summary**: 2-3 key findings with impact scope
2. **Affected Scenarios**: List with module counts and criticality
3. **Business Impact**: Immediate vs. downstream effects
4. **Action Plan**: Prioritized steps with risk assessment

BUSINESS TAXONOMY:
- Critical: Customer-facing, revenue-impacting, compliance-required
- Important: Internal processes, reporting, notifications
- Optional: Convenience features, non-essential integrations

ANALYSIS PRINCIPLES:
- Quantify scope: "X scenarios affected, Y modules need updates"
- Prioritize by business criticality, not technical complexity
- Flag potential cascade failures and dependencies
- Provide actionable recommendations with effort estimates

Always include specific scenario names, module counts, and risk-based prioritization."""

    def _call_ai_with_retry(
        self, messages: List[Dict], max_tokens: int = 1500, model: str = None
    ) -> Optional[str]:
        """Call OpenAI API using centralized service with retry logic"""
        temperature = 0.1 if self.deterministic else 0.3

        response = self.openai_service.create_completion(
            messages=messages,
            model=model,
            task_type="analysis",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=60,
        )

        if response and response.choices:
            return response.choices[0].message.content
        else:
            return "⚠️ Analysis failed - please check your OpenAI API key and try again"

    def _call_ai_with_tools(self, messages, tools, model, needs_search, console):
        """Call AI with tool support and handle tool execution"""
        try:
            # Call OpenAI API with tool support using centralized service
            response = self.openai_service.create_completion(
                messages=messages,
                model=model,
                task_type="analysis",
                temperature=0.2,
                max_tokens=1500,
                tools=tools,
                tool_choice="required" if needs_search else "auto",
            )

            message = response.choices[0].message

            if message.tool_calls:
                # AI wants to use search tools
                tool_responses = []

                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the search function across all scenarios
                    with console.status(
                        f"[dim]Searching across scenarios for {function_args}...[/dim]"
                    ):
                        tool_result = self._execute_cross_blueprint_search(
                            function_name, function_args
                        )
                    tool_responses.append(f"Search '{function_name}': {tool_result}")

                # Add tool results to conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": f"I'll search across all scenarios for that information.",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                },
                                "type": tool_call.type,
                            }
                            for tool_call in message.tool_calls
                        ],
                    }
                )

                for i, tool_call in enumerate(message.tool_calls):
                    messages.append(
                        {"role": "tool", "tool_call_id": tool_call.id, "content": tool_responses[i]}
                    )

                # Get AI's final response using search results
                final_response = self.openai_service.create_completion(
                    messages=messages,
                    model=model,
                    task_type="analysis",
                    max_tokens=1500,
                    temperature=0.2,
                )

                return final_response.choices[0].message.content
            else:
                # Regular response without tools
                return message.content or "No response generated."

        except Exception as e:
            return f"⚠️ Analysis failed: {str(e)[:100]}..."

    def _execute_cross_blueprint_search(self, function_name: str, function_args: dict) -> str:
        """Execute search across all scenarios in the blueprint collection"""
        try:
            # Import the corpus analyzer
            # Create temporary directory with all scenarios
            import tempfile

            from ..analysis.corpus_analyzer import CorpusAnalyzer

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Write all scenarios to temp files
                for key, blueprint in self.blueprints.items():
                    temp_file = temp_path / f"{blueprint['filename']}.json"
                    data_to_write = blueprint["data"]

                    # Normalize data structure
                    if "blueprint" in data_to_write:
                        inner_data = data_to_write["blueprint"].copy()
                        if "name" not in inner_data:
                            inner_data["name"] = blueprint["scenario_name"]
                        data_to_write = inner_data

                    with open(temp_file, "w") as f:
                        json.dump(data_to_write, f, indent=2)

                # Initialize analyzer and load all scenarios
                analyzer = CorpusAnalyzer()
                analyzer.load_corpus(temp_path)

                # Execute the requested search function
                if function_name == "search_text":
                    results = analyzer.search_text(
                        function_args["search_text"], function_args.get("case_sensitive", False)
                    )
                elif function_name == "search_module_types":
                    results = analyzer.search_module_types(
                        function_args["type_pattern"], function_args.get("exact_match", False)
                    )
                elif function_name == "search_workfront_fields":
                    results = analyzer.search_de_fields(
                        function_args["field_pattern"], function_args.get("exact_match", False)
                    )
                else:
                    return f"Unknown search function: {function_name}"

                # Format results for AI with scenario grouping
                if not results:
                    return f"No results found for {function_args}"

                # Group by scenario for cleaner output
                by_scenario = {}
                for result in results:
                    scenario = result.get("scenario_name", "Unknown")
                    if scenario not in by_scenario:
                        by_scenario[scenario] = []
                    by_scenario[scenario].append(result)

                formatted_results = {
                    "total_matches": len(results),
                    "scenarios_affected": len(by_scenario),
                    "search_params": function_args,
                    "results_by_scenario": {},
                }

                # Limit to top 20 scenarios to avoid token overflow
                for scenario, scenario_results in list(by_scenario.items())[:20]:
                    formatted_results["results_by_scenario"][scenario] = {
                        "match_count": len(scenario_results),
                        "sample_matches": scenario_results[:5],  # Show first 5 matches per scenario
                    }

                return json.dumps(formatted_results, indent=2)

        except Exception as e:
            return f"Search error: {str(e)}"

    def analyze_with_ai(self, user_question: str, console) -> str:
        """Production-ready AI analysis with error resilience"""
        try:
            # Check if OpenAI service is available
            if not self.openai_service.is_available():
                raise ValueError(
                    "OpenAI API key not found. Please run 'tekmera init' to configure your API key."
                )

            # Prepare context data with adaptive chunking
            context_data = self._prepare_context_data()
            data_chunks = self._chunk_data_adaptively(context_data)

            # Select optimal model based on task complexity
            task_type = "analysis" if len(data_chunks) > 1 else "simple_question"
            query_length = len(user_question) + sum(len(chunk) for chunk in data_chunks)
            complexity = "complex" if len(data_chunks) > 3 else "medium"

            selected_model = self.openai_service.select_model_for_task(
                task_type, query_length, complexity
            )

            if len(data_chunks) > 1:
                console.print(
                    f"[yellow]📦 Large dataset: Processing in {len(data_chunks)} chunks with {selected_model}[/yellow]"
                )
            else:
                console.print(f"[blue]🤖 Using {selected_model} for optimal analysis[/blue]")

            # Load configurable system prompt and enhance it with search instructions
            base_prompt = self._load_system_prompt()
            enhanced_prompt = f"""{base_prompt}

MANDATORY SEARCH USAGE:
When users ask about specific apps, modules, fields, or scenarios, you MUST use search tools to find detailed information. Do NOT give vague answers.

SEARCH TOOLS (USE THESE ACTIVELY):
- search_text: Find specific text/strings across all scenarios
- search_module_types: Find specific types of modules across scenarios
- search_workfront_fields: Find Workfront DE fields across scenarios

EXAMPLES OF REQUIRED SEARCHES:
- "Which scenarios use proof?" → MUST run search_module_types("proof") AND search_text("proof")
- "What uses Salesforce?" → MUST run search_module_types("salesforce")
- "Any status fields?" → MUST run search_workfront_fields("status") AND search_text("status")
- "Impact of changing X?" → MUST run search_text("X") to find all usages

RESPONSE RULES:
- ALWAYS search first for specific topics, then analyze results
- Include specific scenario names and module counts from search results
- If search finds nothing, say "Search found no matches for [term]"
- Quantify impact: "X scenarios affected, Y modules need updates"
- Never say "details not available" - search for them!"""

            # Define search tools for AI to use
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "search_text",
                        "description": "Search for specific text strings across all scenarios in the collection",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_text": {
                                    "type": "string",
                                    "description": "Text to search for (e.g., 'approved', 'rejected', 'status')",
                                },
                                "case_sensitive": {
                                    "type": "boolean",
                                    "description": "Whether to use case-sensitive search",
                                    "default": False,
                                },
                            },
                            "required": ["search_text"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "search_module_types",
                        "description": "Search for specific module types across all scenarios",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "type_pattern": {
                                    "type": "string",
                                    "description": "Module type to search for (e.g., 'workfront-proof', 'salesforce', 'slack')",
                                },
                                "exact_match": {
                                    "type": "boolean",
                                    "description": "Whether to require exact match",
                                    "default": False,
                                },
                            },
                            "required": ["type_pattern"],
                        },
                    },
                },
                {
                    "type": "function",
                    "function": {
                        "name": "search_workfront_fields",
                        "description": "Search for Workfront DE fields across all scenarios",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "field_pattern": {
                                    "type": "string",
                                    "description": "Field pattern to search for (e.g., 'DE:status', 'client_id')",
                                },
                                "exact_match": {
                                    "type": "boolean",
                                    "description": "Whether to require exact match",
                                    "default": False,
                                },
                            },
                            "required": ["field_pattern"],
                        },
                    },
                },
            ]

            # Process chunks with error aggregation and search capability
            successful_responses = []
            failed_chunks = []

            for chunk_idx, chunk in enumerate(data_chunks):
                chunk_prefix = (
                    f"(Chunk {chunk_idx + 1}/{len(data_chunks)}) " if len(data_chunks) > 1 else ""
                )

                with console.status(f"[bold green]{chunk_prefix}Analyzing blueprints with AI..."):

                    chunk_info = ""
                    if len(data_chunks) > 1:
                        chunk_info = (
                            f"\n\nNote: This is chunk {chunk_idx + 1} of {len(data_chunks)}. "
                        )
                        if chunk_idx == 0:
                            chunk_info += (
                                "I will analyze all chunks and provide a comprehensive answer."
                            )
                        else:
                            chunk_info += "This is additional data for the same question."

                    user_prompt = f"""User Question: {user_question}

Blueprint Collection Data: {json.dumps(chunk, indent=2)}{chunk_info}"""

                    messages = [
                        {"role": "system", "content": enhanced_prompt},
                        {"role": "user", "content": user_prompt},
                    ]

                    # Detect if question needs search tools
                    question_lower = user_question.lower()
                    search_triggers = [
                        "which scenarios",
                        "what scenarios",
                        "how many",
                        "uses",
                        "impact",
                        "affected",
                        "proof",
                        "salesforce",
                        "slack",
                        "workfront",
                        "status",
                        "field",
                        "module",
                        "specific",
                        "find",
                        "search",
                        "list",
                    ]
                    needs_search = any(trigger in question_lower for trigger in search_triggers)

                    # Call with retry logic using selected model and search tools
                    response = self._call_ai_with_tools(
                        messages, tools, selected_model, needs_search, console
                    )

                    if response and not response.startswith("⚠️"):
                        successful_responses.append(response)
                    else:
                        failed_chunks.append(f"Chunk {chunk_idx + 1}: {response or 'No response'}")

            # Handle results based on success/failure mix
            if not successful_responses:
                return f"❌ Analysis failed for all chunks:\n" + "\n".join(failed_chunks)

            # Combine successful responses
            if len(successful_responses) == 1:
                final_response = successful_responses[0]
            else:
                # Synthesize multiple responses
                combined_prompt = f"""Synthesize these analyses for: "{user_question}"

{chr(10).join([f"Analysis {i+1}:\n{response}\n" for i, response in enumerate(successful_responses)])}

Provide a unified comprehensive report that combines all insights."""

                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert at synthesizing multiple analyses into a comprehensive report.",
                    },
                    {"role": "user", "content": combined_prompt},
                ]

                with console.status("[bold green]Synthesizing results..."):
                    # Use reasoning model for complex synthesis
                    synthesis_model = (
                        "gpt-5.1-codex" if len(successful_responses) > 2 else selected_model
                    )
                    final_response = self._call_ai_with_retry(
                        messages, max_tokens=2000, model=synthesis_model
                    )

            # Append failure warnings if any chunks failed
            if failed_chunks:
                final_response += f"\n\n⚠️ **Note**: {len(failed_chunks)} chunk(s) failed analysis. Results may be incomplete."

            return final_response or "❌ Unable to generate analysis"

        except Exception as e:
            return f"❌ Analysis system error: {str(e)}"

    def _prepare_context_data(self) -> Dict[str, Any]:
        """Prepare summarized data from all blueprints for AI analysis"""
        summaries = []

        for key, blueprint in self.blueprints.items():
            summary = self._extract_blueprint_summary(blueprint)
            summaries.append(
                {
                    "scenario_name": summary.name,
                    "filename": summary.filename,
                    "module_count": summary.module_count,
                    "app_types": summary.app_types,
                    "connections": summary.connections,
                    "modules": summary.modules,
                }
            )

        return {
            "total_scenarios": len(summaries),
            "scenarios": summaries,
            "summary_stats": self._calculate_folder_stats(summaries),
        }

    def _calculate_folder_stats(self, summaries: List[Dict]) -> Dict[str, Any]:
        """Calculate overall statistics for the folder"""
        all_apps = set()
        all_connections = set()
        total_modules = 0

        for summary in summaries:
            all_apps.update(summary["app_types"])
            all_connections.update(summary["connections"])
            total_modules += summary["module_count"]

        return {
            "total_modules": total_modules,
            "unique_apps": len(all_apps),
            "unique_connections": len(all_connections),
            "app_types": list(all_apps),
            "average_modules_per_scenario": (
                round(total_modules / len(summaries), 1) if summaries else 0
            ),
        }
