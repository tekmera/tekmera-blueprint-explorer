"""
Table formatter for CLI output.
"""

import json


def format_result(result, format_type="table"):
    """Format projection result for CLI output."""

    if format_type == "json":
        # JSON output for scripting
        output = {
            "blueprint_id": result.blueprint_id,
            "blueprint_name": result.blueprint_name,
            "platform": result.platform.value,
            "data": result.data,
            "metadata": {
                "function": result.metadata.function,
                "version": result.metadata.version,
                "computed_at": result.metadata.computed_at,
                "input_hash": result.metadata.input_hash,
            },
        }
        print(json.dumps(output, indent=2))

    else:
        # Table output for interactive use
        print(f"Blueprint: {result.blueprint_name}")
        print(f"Platform:  {result.platform.value}")
        print(f"Function:  {result.metadata.function}")
        
        # Format result data based on type
        if isinstance(result.data, list):
            print(f"Results:   ({len(result.data)} items)")
            for i, item in enumerate(result.data, 1):
                print(f"  {i:2d}. {item}")
        else:
            print(f"Result:    {result.data}")
            
        print(f"Hash:      {result.metadata.input_hash}")


def format_error(message: str, format_type="table"):
    """Format error message."""
    if format_type == "json":
        print(json.dumps({"error": message}))
    else:
        print(f"Error: {message}")
