#!/usr/bin/env python3

import json
from datetime import datetime
import random

def load_config(filepath):
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{filepath}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filepath}': {e}")
        return None

def validate_config(config: dict) -> tuple[bool, list[str]]:
    errors = []

    def field_exists_validator(field0, field1, source, number): #reusable validator for ensuring required fields exist
        if field0 not in field1:
            errors.append(f"{source} {number}: missing '{field0}' field")

    def type_validation(Field, item, location, itemtype, number): #reusable validator for different types
            if item in location and not isinstance(location[item], itemtype):
                errors.append(
            f"{Field} {number}: '{item}' must be a {itemtype.__name__}, got {type(location[item]).__name__}"
        )
    def empty_field_validator(field0, field1, number, location): #reusable validator for ensuring required fields contain values
        if field0 in field1 and not field1[field0].strip():
                errors.append(f"{location} {number}: '{field0}' cannot be empty")

    #required field check
    required_fields = ['plan_name', 'sources', 'destination']
    for field in required_fields:
        field_exists_validator(field, config, 'Main', '')
    
    #define types, can be updated as needed for future use
    types_str = ['plan_name', 'version', 'description']
    types_dict = ['destination', 'options']
    types_list = ['sources']

    for item in types_str:
        type_validation('Main', item, config, str, '')
    for item in types_dict:
        type_validation('Main', item, config, dict, '')
    for item in types_list:
        type_validation('Main', item, config, list, '')
    
    # value validation
    if isinstance(config.get('sources'), list):
        if len(config['sources']) == 0:
            errors.append("'sources' list cannot be empty")

        for i, source in enumerate(config['sources']):
            field_exists_validator('name', source, 'Source', i)
            field_exists_validator('path', source, 'Source', i)
            empty_field_validator('path', source, i, 'Source')
            type_validation('Source', 'recursive', source, bool, i)
            type_validation('Source', 'include_patterns', source, list, i)
            type_validation('Source', 'exclude_patterns', source, list, i)

    if isinstance(config.get('destination'), dict):
        dest = config['destination']
        field_exists_validator('base_path', dest, 'Destination', '')
        empty_field_validator('base_path', dest, '', 'Destination')
   
    return len(errors) == 0, errors
    

        
def simulate_backup(config):
    #Generate a dry-run simulation using fake file data.
    operations = []

    for source in config['sources']:
        num_files = random.randint(5, 15)
        files = []

        for i in range(num_files):
            size_mb = round(random.uniform(1, 100), 1)
            name = f"{source['name'].lower().replace(' ', '_')}_{i+1:03d}.log"
            files.append({"name": name, "size_mb": size_mb})

        operations.append({
            "source_name": source['name'],
            "source_path": source['path'],
            "files": files
        })

    total_files = sum(len(op['files']) for op in operations)
    total_size = round(
        sum(f['size_mb'] for op in operations for f in op['files']), 1
    )

    return {
        "plan_name": config['plan_name'],
        "mode": "DRY-RUN",
        "summary": {
            "total_sources": len(operations),
            "total_files": total_files,
            "total_size_mb": total_size
        },
        "operations": operations
    }

def generate_report(report_data):
    """Print formatted dry-run simulation report."""
    report = []
    sep = "=" * 70
    thin = "-" * 70

    report.append(sep)
    report.append(f"{'BACKUP PLAN DRY-RUN SIMULATION':^70}")
    report.append(sep)
    report.append(f"Plan: {report_data['plan_name']}")
    report.append(f"Mode: {report_data['mode']} (no files will be copied)")
    report.append('\n')

    s = report_data['summary']
    report.append("SUMMARY")
    report.append(thin[:7])
    report.append(f"Total Sources:  {s['total_sources']}")
    report.append(f"Total Files:    {s['total_files']}")
    report.append(f"Total Size:     {s['total_size_mb']} MB")
    report.append('\n')

    for i, op in enumerate(report_data['operations'], 1):
        report.append(f"SOURCE {i}: {op['source_name']}")
        report.append(f"Path: {op['source_path']}")
        report.append(f"Files: {len(op['files'])}")
        # Show first 3 files as samples
        for f in op['files'][:3]:
            report.append(f"  -> {f['name']} ({f['size_mb']} MB)")
        remaining = len(op['files']) - 3
        if remaining > 0:
            report.append(f"  ... and {remaining} more files")
        report.append('\n')

    report.append(sep)
    report.append("DRY-RUN complete. No files were copied.")
    report.append(sep)

    return "\n".join(report)

def main():
    #orchestrate backup pipeline
    import sys

    if len(sys.argv) < 1:
        print("Usage: python backup_planner.py ")
        sys.exit(1)

    filepath = sys.argv[1]

    # Step 1: Load
    config = load_config(filepath)
    if config is None:
        sys.exit(1)

    # Step 2: Validate
    is_valid, errors = validate_config(config)
    if not is_valid:
        print(f"Validation FAILED. {len(errors)} error(s) found:")
        for i, err in enumerate(errors, 1):
            print(f"  [{i}] {err}")
        sys.exit(1)

    print("Validation PASSED.")

    # Step 3: Simulate backup
    report_data = simulate_backup(config)

    # Step 4: Generate Report using simulated data
    text_report = generate_report(report_data)
    print (text_report)
    with open('sample_report.txt', 'w', encoding='utf-8') as f:
       f.write(text_report)


if __name__ == "__main__":
    main()