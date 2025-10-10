"""
Report generation and formatting
"""
from typing import List, Dict, Any


class Reporter:
    """Handles formatting and output of analysis results."""
    
    def generate_report(self, results: List[Dict[str, Any]]) -> None:
        """
        Generate and print analysis report to stdout.
        
        Args:
            results: List of analysis result dictionaries
        """
        print("=" * 60)
        print("WORKFRONT FUSION BLUEPRINT ANALYSIS REPORT")
        print("=" * 60)
        print()
        
        total_scenarios = len(results)
        total_modules = sum(r['module_count'] for r in results)
        all_module_types = set()
        all_de_fields = set()
        
        # Print individual scenario details
        for result in results:
            print(f"Scenario: {result['scenario_name']}")
            print(f"File: {result['filename']}.json")
            print(f"Modules: {result['module_count']}")
            
            if result['module_types']:
                print("Module Types:")
                for module_type in result['module_types']:
                    print(f"  - {module_type}")
                    all_module_types.add(module_type)
            
            if result['workfront_fields']:
                print("Workfront Fields:")
                for field in sorted(result['workfront_fields']):
                    print(f"  - {field}")
                    all_de_fields.add(field)
            
            print("-" * 40)
            print()
        
        # Print summary
        print("SUMMARY")
        print("-" * 20)
        print(f"Total Scenarios: {total_scenarios}")
        print(f"Total Modules: {total_modules}")
        print(f"Unique Module Types: {len(all_module_types)}")
        print(f"Unique Workfront Fields: {len(all_de_fields)}")
        
        if all_module_types:
            print(f"\nAll Module Types Found:")
            for module_type in sorted(all_module_types):
                print(f"  - {module_type}")
        
        if all_de_fields:
            print(f"\nAll Workfront Fields Found:")
            for field in sorted(all_de_fields):
                print(f"  - {field}")