"""Make.com module type extraction."""

from .....meta.types import Module, ModuleResult, Platform, create_module_result


def module_type(module: Module) -> ModuleResult[str]:
    """Extract module type from Make.com module."""
    module_type_str = module.get("module", "unknown")

    # Handle empty/null values
    if not module_type_str:
        module_type_str = "unknown"

    return create_module_result(
        module=module,
        platform=Platform.MAKE_COM,
        function_name="modules.metadata.module_type",
        data=module_type_str,
    )
