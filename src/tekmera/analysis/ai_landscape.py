"""
AI-powered landscape analysis for cross-blueprint queries
Production-ready version with improved token management, error handling, and configurability
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


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

    def __init__(self, blueprints: Dict[str, Any], detail_level: str = "balanced", model_type: str = "auto"):
        self.blueprints = blueprints
        self.detail_level = detail_level  # "minimal", "balanced", "detailed"
        self.model_type = model_type  # "auto", "fast", "standard", "thinking"
        self.max_context_tokens = self._get_token_limit()
        self.token_divisor = 3.3
        self.max_retries = 3
        self.retry_delay = 1.0

    def _get_token_limit(self) -> int:
        """Adjust token limits based on detail level"""
        limits = {
            "minimal": 8000,    # Aggressive compression
            "balanced": 12000,  # Moderate detail
            "detailed": 16000   # Maximum detail before chunking
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
            name=scenario_name[:name_limit[self.detail_level]],
            filename=filename[:filename_limit[self.detail_level]],
            modules=modules,
            connections=list(connections),
            module_count=len(modules),
            app_types=list(app_types)
        )

    def _extract_key_parameters(self, module: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key parameters that provide business context"""
        parameters = {}
        
        # Look for common business-relevant parameters
        module_params = module.get("parameters", {})
        if isinstance(module_params, dict):
            # Extract fields that often contain business context
            business_keys = [
                "filter", "condition", "status", "assignee", "priority", 
                "project", "task", "document", "proof", "approval",
                "notification", "email", "message", "subject"
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

    def _select_model(self, user_question: str, chunk_count: int) -> str:
        """Intelligently select OpenAI model based on query complexity and data size"""
        if self.model_type != "auto":
            # Manual model selection
            model_map = {
                "fast": "gpt-4o-mini",
                "standard": "gpt-4o", 
                "thinking": "gpt-4"
            }
            return model_map.get(self.model_type, "gpt-4o")
        
        # Auto-selection based on query characteristics
        question_lower = user_question.lower()
        
        # Complex analysis indicators
        complex_keywords = [
            "impact", "relationship", "dependency", "workflow", "process",
            "business", "strategy", "integration", "ecosystem", "architecture"
        ]
        
        # Simple lookup indicators  
        simple_keywords = [
            "list", "count", "how many", "which scenarios", "find", "show me"
        ]
        
        # Multi-step reasoning indicators
        reasoning_keywords = [
            "if we change", "what would happen", "cascade", "downstream",
            "effect", "consequence", "risk", "compare", "analyze differences"
        ]
        
        has_complex = any(keyword in question_lower for keyword in complex_keywords)
        has_simple = any(keyword in question_lower for keyword in simple_keywords)
        has_reasoning = any(keyword in question_lower for keyword in reasoning_keywords)
        
        # Decision logic
        if chunk_count > 3 or has_reasoning or (has_complex and len(user_question) > 100):
            # Complex multi-step analysis with large datasets
            return "gpt-4"
        elif has_simple and not has_complex and chunk_count == 1:
            # Simple lookups with small datasets
            return "gpt-4o-mini"
        elif chunk_count > 1:
            # Multi-chunk synthesis requires standard reasoning
            return "gpt-4o"
        else:
            # Default balanced option
            return "gpt-4o"

    def _estimate_token_count(self, text: str) -> int:
        """More conservative token estimation"""
        # Use tiktoken if available, otherwise conservative heuristic
        try:
            import tiktoken
            encoder = tiktoken.encoding_for_model("gpt-4o")
            return len(encoder.encode(text))
        except ImportError:
            # More conservative divisor for multilingual content and nested JSON
            return int(len(text) / self.token_divisor)

    def _chunk_data_adaptively(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Adaptive chunking with progressive module detail reduction"""
        context_json = json.dumps(context_data, indent=2)
        estimated_tokens = self._estimate_token_count(context_json)

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
                    scenario["modules"].append({"module": "...", "label": f"(+{scenario['module_count'] - 20} more modules)"})

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
            return prompt_file.read_text(encoding='utf-8')
        
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

    def _call_ai_with_retry(self, client, messages: List[Dict], max_tokens: int = 1500, model: str = "gpt-4o") -> Optional[str]:
        """Call OpenAI API with retry logic and error aggregation"""
        for attempt in range(self.max_retries):
            try:
                # Adjust timeout based on model type
                timeout = 30.0
                if "gpt-4" == model:
                    timeout = 120.0  # GPT-4 needs more time for complex reasoning
                elif "mini" in model:
                    timeout = 15.0   # GPT-4o-mini should be quick
                
                # Handle different model capabilities
                call_params = {
                    "model": model,
                    "messages": messages,
                    "temperature": 0.3,
                    "timeout": timeout
                }
                
                # Only add max_tokens if the model supports it
                if not model.startswith("o1"):
                    call_params["max_tokens"] = max_tokens
                
                response = client.chat.completions.create(**call_params)
                return response.choices[0].message.content
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Last attempt failed, return partial error info
                    return f"⚠️ Analysis failed after {self.max_retries} attempts: {str(e)[:100]}..."
                
                # Wait before retry with exponential backoff
                time.sleep(self.retry_delay * (2 ** attempt))
        
        return None

    def analyze_with_ai(self, user_question: str, console) -> str:
        """Production-ready AI analysis with error resilience"""
        try:
            # Get OpenAI API key
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")

            # Import OpenAI client
            try:
                from openai import OpenAI
            except ImportError:
                raise ValueError("OpenAI library not installed. Run: pip install openai")

            client = OpenAI(api_key=api_key)

            # Prepare context data with adaptive chunking
            context_data = self._prepare_context_data()
            data_chunks = self._chunk_data_adaptively(context_data)

            # Select optimal OpenAI model
            selected_model = self._select_model(user_question, len(data_chunks))
            
            if len(data_chunks) > 1:
                console.print(f"[yellow]📦 Large dataset: Processing in {len(data_chunks)} chunks with {selected_model}[/yellow]")
            else:
                console.print(f"[blue]🤖 Using {selected_model} for optimal analysis[/blue]")

            # Load configurable system prompt
            system_prompt = self._load_system_prompt()
            
            # Process chunks with error aggregation
            successful_responses = []
            failed_chunks = []

            for chunk_idx, chunk in enumerate(data_chunks):
                chunk_prefix = f"(Chunk {chunk_idx + 1}/{len(data_chunks)}) " if len(data_chunks) > 1 else ""
                
                with console.status(f"[bold green]{chunk_prefix}Analyzing blueprints with AI..."):
                    
                    chunk_info = ""
                    if len(data_chunks) > 1:
                        chunk_info = f"\n\nNote: This is chunk {chunk_idx + 1} of {len(data_chunks)}. "
                        if chunk_idx == 0:
                            chunk_info += "I will analyze all chunks and provide a comprehensive answer."
                        else:
                            chunk_info += "This is additional data for the same question."

                    user_prompt = f"""User Question: {user_question}

Blueprint Collection Data: {json.dumps(chunk, indent=2)}{chunk_info}"""

                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                    
                    # Call with retry logic using selected model
                    response = self._call_ai_with_retry(client, messages, model=selected_model)
                    
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
                    {"role": "system", "content": "You are an expert at synthesizing multiple analyses into a comprehensive report."},
                    {"role": "user", "content": combined_prompt}
                ]
                
                with console.status("[bold green]Synthesizing results..."):
                    # Use reasoning model for complex synthesis
                    synthesis_model = "gpt-4" if len(successful_responses) > 2 else selected_model
                    final_response = self._call_ai_with_retry(client, messages, max_tokens=2000, model=synthesis_model)

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
            summaries.append({
                "scenario_name": summary.name,
                "filename": summary.filename,
                "module_count": summary.module_count,
                "app_types": summary.app_types,
                "connections": summary.connections,
                "modules": summary.modules,
            })

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
            "average_modules_per_scenario": round(total_modules / len(summaries), 1) if summaries else 0,
        }