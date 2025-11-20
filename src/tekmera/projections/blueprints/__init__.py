"""
Blueprint-level projection functions.

This package provides analysis functions for one or more automation platform blueprints.
Functions accept Union[Dict, List[Dict]] to handle both single and multiple blueprints uniformly.

Available categories:
- basic: Fundamental blueprint info (name, module count, complexity)
- search: Text, module, and field search within blueprint(s)
- flow: Execution path and connection analysis
- comparison: Blueprint comparison and diff analysis
- corpus: Aggregate analysis across multiple blueprints
"""
