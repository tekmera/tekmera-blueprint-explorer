"""Make.com module text content extraction."""

import json

from .....meta.types import Module, ModuleResult, Platform, create_module_result


def text_content(module: Module) -> ModuleResult[str]:
    """Extract text content from Make.com module."""
    # Convert entire module to JSON string for text searching
    module_text = json.dumps(module, sort_keys=True)

    return create_module_result(
        module=module,
        platform=Platform.MAKE_COM,
        function_name="modules.content.text_content",
        data=module_text,
    )
