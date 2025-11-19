"""
Centralized OpenAI API service for Tekmera Fusion Explorer.

This module provides a unified interface for all OpenAI interactions,
including model selection, API calls, and error handling.
"""

import logging
from typing import Any, Dict, List, Optional

import tiktoken
from openai import OpenAI

from ..config.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class OpenAIService:
    """Centralized OpenAI API service with intelligent model selection."""

    # Updated model definitions
    MODELS = {
        "gpt-5.1": {
            "name": "gpt-5.1",
            "description": "Latest model for everyday coding tasks",
            "max_tokens": 200000,
            "context_window": 2000000,
            "use_case": "everyday_coding",
        },
        "gpt-5.1-codex": {
            "name": "gpt-5.1-codex",
            "description": "Advanced model for complex, long-running agentic coding",
            "max_tokens": 200000,
            "context_window": 2000000,
            "use_case": "complex_coding",
        },
        "gpt-5.1-codex-mini": {
            "name": "gpt-5.1-codex-mini",
            "description": "Cost-efficient model for edits and simple changes",
            "max_tokens": 100000,
            "context_window": 1000000,
            "use_case": "simple_edits",
        },
        # Legacy models for fallback
        "gpt-4o": {
            "name": "gpt-4o",
            "description": "GPT-4 Optimized for complex analysis",
            "max_tokens": 16384,
            "context_window": 128000,
            "use_case": "complex_analysis",
        },
        "gpt-4o-mini": {
            "name": "gpt-4o-mini",
            "description": "GPT-4 mini for simple tasks",
            "max_tokens": 16384,
            "context_window": 128000,
            "use_case": "simple_tasks",
        },
        "gpt-4": {
            "name": "gpt-4",
            "description": "GPT-4 for complex reasoning",
            "max_tokens": 8192,
            "context_window": 32768,
            "use_case": "complex_reasoning",
        },
    }

    def __init__(self):
        self.client: Optional[OpenAI] = None
        self.config_manager = ConfigManager()
        self._initialize_client()

    def _initialize_client(self) -> bool:
        """Initialize OpenAI client with API key from config or environment."""
        try:
            api_key = self.config_manager.get_openai_api_key()
            if not api_key:
                logger.warning("No OpenAI API key found")
                return False

            self.client = OpenAI(api_key=api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False

    def is_available(self) -> bool:
        """Check if OpenAI service is available."""
        return self.client is not None

    def select_model_for_task(
        self, task_type: str, query_length: int = 0, complexity: str = "medium"
    ) -> str:
        """
        Intelligently select the best model for a given task.

        Args:
            task_type: Type of task (coding, analysis, editing, description)
            query_length: Length of input query/data
            complexity: Task complexity (simple, medium, complex)

        Returns:
            Model name to use
        """
        # Coding tasks
        if task_type in ["coding", "code_generation", "code_analysis"]:
            if complexity == "simple" or query_length < 1000:
                return "gpt-5.1-codex-mini"
            elif complexity == "complex" or query_length > 10000:
                return "gpt-5.1-codex"
            else:
                return "gpt-5.1"

        # Editing and simple changes
        elif task_type in ["editing", "simple_edit", "format", "cleanup"]:
            return "gpt-5.1-codex-mini"

        # Complex analysis
        elif task_type in ["analysis", "cross_blueprint", "complex_reasoning"]:
            if complexity == "complex" or query_length > 20000:
                return "gpt-5.1-codex"
            else:
                return "gpt-5.1"

        # Simple descriptions and summaries
        elif task_type in ["description", "summary", "simple_question"]:
            return "gpt-5.1-codex-mini"

        # Default to standard model
        else:
            return "gpt-5.1"

    def estimate_tokens(self, text: str, model: str = "gpt-5.1") -> int:
        """Estimate token count for text using tiktoken."""
        try:
            # Use gpt-4 encoding for new models (closest approximation)
            encoding = tiktoken.encoding_for_model("gpt-4")
            return len(encoding.encode(text))
        except Exception:
            # Fallback estimation: roughly 4 characters per token
            return len(text) // 4

    def create_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        task_type: str = "analysis",
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        timeout: int = 60,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a chat completion with intelligent model selection.

        Args:
            messages: List of message dicts
            model: Specific model to use (optional, will auto-select if None)
            task_type: Type of task for model selection
            temperature: Randomness (0-2)
            max_tokens: Maximum tokens to generate
            tools: Function tools to provide
            tool_choice: How to use tools
            timeout: Request timeout in seconds
            **kwargs: Additional OpenAI parameters

        Returns:
            OpenAI completion response or None if failed
        """
        if not self.is_available():
            logger.error("OpenAI service not available")
            return None

        try:
            # Auto-select model if not specified
            if model is None:
                query_text = " ".join([msg.get("content", "") for msg in messages])
                query_length = len(query_text)
                model = self.select_model_for_task(task_type, query_length)

            # Validate model exists
            if model not in self.MODELS:
                logger.warning(f"Unknown model {model}, falling back to gpt-5.1")
                model = "gpt-5.1"

            # Set max_tokens based on model if not specified
            if max_tokens is None:
                max_tokens = min(4096, self.MODELS[model]["max_tokens"])

            # Prepare request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timeout": timeout,
                **kwargs,
            }

            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = tool_choice

            logger.info(f"Making OpenAI request with model: {model}")

            # Make the API call
            response = self.client.chat.completions.create(**request_params)

            logger.info(f"OpenAI request successful, usage: {response.usage}")
            return response

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return None

    def create_business_analysis(self, blueprint_data: str, scenario_name: str) -> Optional[str]:
        """Create business process analysis for a blueprint."""
        prompt = self._load_business_analysis_prompt()

        messages = [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": f"Analyze this Workfront Fusion scenario: '{scenario_name}'\n\n{blueprint_data}",
            },
        ]

        response = self.create_completion(
            messages=messages, task_type="description", temperature=0.1, max_tokens=1000
        )

        if response and response.choices:
            return response.choices[0].message.content
        return None

    def create_cross_blueprint_analysis(
        self, query: str, search_results: List[Dict], tools: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """Create cross-blueprint analysis with tool support."""
        system_prompt = """You are an expert Workfront Fusion analyst. Analyze blueprint data to answer user questions about business processes, integrations, and workflows. Use the provided search tool to find relevant information when needed."""

        # Format search results context
        context = "Search Results:\n"
        for result in search_results[:5]:  # Limit to top 5 results
            context += f"- {result.get('summary', 'No summary')}\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Query: {query}\n\nContext from previous search:\n{context}\n\nPlease provide a comprehensive analysis.",
            },
        ]

        response = self.create_completion(
            messages=messages, task_type="analysis", tools=tools, temperature=0.1, max_tokens=2000
        )

        if response and response.choices:
            return response.choices[0].message.content
        return None

    def _load_business_analysis_prompt(self) -> str:
        """Load the business analysis system prompt."""
        try:
            from pathlib import Path

            prompt_path = (
                Path(__file__).parent.parent / "analysis" / "prompts" / "business_analysis.txt"
            )
            if prompt_path.exists():
                return prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Could not load business analysis prompt: {e}")

        # Fallback prompt
        return """You are an expert business process analyst specializing in Workfront Fusion integrations.
        Analyze the provided blueprint data and describe the business process in plain English.
        Focus on what the process accomplishes, not technical implementation details."""

    def get_available_models(self) -> List[Dict[str, str]]:
        """Get list of available models with descriptions."""
        return [
            {
                "name": model_info["name"],
                "description": model_info["description"],
                "use_case": model_info["use_case"],
            }
            for model_info in self.MODELS.values()
        ]

    def validate_api_key(self) -> bool:
        """Validate that the API key works by making a simple test call."""
        if not self.is_available():
            return False

        try:
            response = self.create_completion(
                messages=[{"role": "user", "content": "Hello"}],
                task_type="simple_question",
                max_tokens=5,
                timeout=10,
            )
            return response is not None
        except Exception:
            return False


# Global service instance
_openai_service = None


def get_openai_service() -> OpenAIService:
    """Get the global OpenAI service instance."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
