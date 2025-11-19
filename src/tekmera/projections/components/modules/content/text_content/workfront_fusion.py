"""Workfront Fusion module text content extraction."""

import json

from .....meta.types import Module, ModuleResult, Platform, create_module_result


def text_content(module: Module) -> ModuleResult[str]:
    """Extract text content from Workfront Fusion module."""
    # Convert entire module to JSON string for text searching
    module_text = json.dumps(module, sort_keys=True)

    return create_module_result(
        module=module,
        platform=Platform.WORKFRONT_FUSION,
        function_name="modules.content.text_content",
        data=module_text,
    )
