1. Overview & Purpose

 Reads JSON configuration files defining backup plans, validates configuration structure and values, and simulates backup operations with detailed dry-run reports. 
 
 Designed with configuration-driven programming.
 
 Config-driven programming benefits:
    - Flexibility: Change backup behavior without changing code
    - Reusability: Same script handles dev backups, prod backups, DR backups — different configs
    - Security: Keep sensitive paths and settings separate from source code
    - Collaboration: Non-programmers (sysadmins, managers) can adjust settings via JSON
    - Version Control: Track configuration changes independently from code changes
    - Testing: Swap test config without modifying code
 
2. Usage Instructions

Call from command line:
    python backup_planner.py back_config_file.json

3. Schema Design Decisions
    a. Metadata Section

    plan_name (string): Descriptive name for the backup plan
    version (string): Schema version (e.g., "1.0")
    created_by (string): Creator/team name
    description (string): Optional detailed description

    b. Sources Section (List of Source Objects)

    Each source object must have:
    
        name (string): Descriptive name for this source
        path (string): Source directory path
        recursive (boolean): Whether to scan subdirectories
        include_patterns (list): File patterns to include (e.g., ["*.log", "*.txt"])
        exclude_patterns (list): File patterns to exclude (e.g., ["*.tmp", "debug_*"])

    c. Destination Section (Object)

    base_path (string): Destination directory
    create_timestamped_folders (boolean): Create folders with timestamps
    retention_days (number): Optional retention policy

    d. Options Section (Object - Optional)

    verify_backups (boolean): Whether to verify after backup
    max_file_size_mb (number): Maximum file size to backup


4. Validation Levels

Level 1: Structure Validation

    Load JSON file and parse successfully
    Handle json.JSONDecodeError with helpful message
    Handle FileNotFoundError gracefully

Level 2: Required Fields

    Verify plan_name exists
    Verify sources list exists
    Verify destination object exists
    Error message format: "Missing required field: 'field_name'"

Level 3: Type Validation

    Check plan_name is a string
    Check sources is a list
    Check destination is a dictionary
    Check boolean fields are actually booleans
    Error message format: "'sources' must be a list, got str"

Level 4: Value Validation

    Check sources list is not empty
    Check each source has required path field
    Check path is not empty string
    Check destination.base_path exists and is not empty
    Check pattern lists (if present) are actually lists
    Error message format: "Source 0: missing 'path' field"

5. Simulation Logic

Uses 'random' module to generate simulated file data such as size, number, etc. File names are chosen based on path in source json. 

6. Function Structure

backup_config.json <- json file with config specifications
       │
       ▼
load_config(filepath) <- load config file
  returns: dict | None
       │
       ▼
validate_config(config) <- validate structure and contents of config file
    type_validation(Field, item, location, itemtype, number) <- validates value types for main fields
    field_exists_validator(field0, field1, source, number) <- checks that required field exists
    empty_field_validator(field0, field1, number, location) <- checks that field is not empty
  returns: (bool, [errors])
       │
       ▼
simulate_backup(config) <- dry-run simulation using randomized file data, based on config file
  returns: report_dict
       │
       ▼
generate_report(report_data) <- generates report based on simulation
  prints formatted output
       │
       ▼
main()
  orchestrates all steps and saves report to text file

7. AI Usage

I did not use AI tools.

8. Testing

Created test configs with:
    - missing required fields
    - including/missing optional fields
    - incorrect field types
    - missing required values in required fields
    - incorrect value types
    - invalid json
    - nonexistent file
    - various combinations of the above

9. Challenges

A challenge I faced was the ensuring every type of error was caught. I solved this by thoroughly testing with different types of errors and combinations of nested errors.