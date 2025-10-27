# Project Structure

Updated and cleaned project organization for the Threat Intelligence system.

## Root Directory
```
PY/
├── main.py                          # Main entry point
├── README.md                        # Project documentation
├── requirements.txt                 # Python dependencies
├── template.docx                    # Report template
├── start_dashboard.bat             # Dashboard launcher
├── threat_intel.db                 # SQLite database (gitignored)
└── .gitignore                      # Git ignore patterns
```

## Core Application (`src/`)
```
src/
├── __init__.py
├── config.py                       # Configuration settings
├── core/
│   ├── __init__.py
│   ├── analysis.py                # LLM analysis and JSON parsing
│   ├── fetcher.py                 # RSS feed fetching
│   ├── filtering.py               # Article relevance filtering
│   ├── kql_generator.py           # Regex-based KQL generation
│   ├── kql_generator_llm.py       # LLM-based KQL generation
│   └── report.py                  # Report generation
└── utils/
    ├── __init__.py
    ├── db_utils.py                # Database operations
    └── logging_utils.py           # Logging and colors
```

## Scripts (`scripts/`)
Organized into functional subdirectories:

### 📁 `maintenance/`
Scripts for database maintenance and article reprocessing.
- `reprocess_articles.py` - Unified reprocessing tool (replaces 4 old scripts)
- `analyze_unanalyzed.py` - Process unanalyzed articles
- `fix_crowdstrike_articles.py` - Fix vendor-specific issues

### 📁 `analysis/`
Scripts for data quality checks and validation.
- `check_db.py` - Database statistics and overview
- `check_categorization.py` - Validate categorization logic
- `check_high.py` - Review HIGH risk classifications
- `check_low_info.py` - Review LOW/INFORMATIONAL classifications

### 📁 `utilities/`
General utility scripts for data access.
- `list_not_relevant.py` - List NOT_RELEVANT articles
- `list_unanalyzed.py` - List unanalyzed articles
- `extract_iocs_from_existing.py` - IOC extraction tool

See `scripts/README.md` for detailed usage instructions.

## Dashboard (`dashboard/`)
```
dashboard/
├── README.md
├── TESTING_GUIDE.md
├── backend/
│   ├── app.py                     # Flask API server
│   ├── database.py                # Database layer
│   ├── routes.py                  # API endpoints
│   └── requirements.txt
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── public/
    │   └── index.html
    └── src/
        ├── main.jsx               # React entry point
        ├── App.jsx                # Main app component
        └── components/            # React components
```

## Documentation (`docs/`)
Comprehensive project documentation:
- Change logs and feature documentation
- Implementation guides (KQL, IOC extraction, etc.)
- Testing and debugging guides
- Project cleanup and refactoring notes

## Exports (`exports/`)
Generated IOC exports (per-article):
- `article_<id>_iocs.json` - JSON format IOCs
- `article_<id>_domains.txt` - Plain text domain lists

## KQL Queries (`kql_queries/`)
Generated threat hunting queries:
- `01_*.kql` - High priority detections
- `02_*.kql` - Medium priority detections
- etc.

## Archive (`archive/`)
Historical files and deprecated content:
- Old documentation
- Deprecated scripts
- Test files
- Debug outputs

## Tests (`tests/`)
Unit and integration tests:
- Feature tests
- Filtering tests
- IOC extraction tests
- KQL generation tests

## Removed/Consolidated

### ❌ Removed Files
- `failed_json_debug.txt` → moved to archive
- `test_api.html` → moved to archive
- Multiple duplicate reprocessing scripts → replaced by `reprocess_articles.py`

### ✅ Consolidated Scripts
The following scripts were merged into `scripts/maintenance/reprocess_articles.py`:
- `reprocess_misclassified.py`
- `reprocess_all_not_relevant.py`
- `reprocess_not_relevant.py`
- `revert_gptoss_misclassifications.py`

## Best Practices

### File Naming
- Use snake_case for Python files
- Prefix test files with `test_`
- Use descriptive names indicating purpose

### Organization
- Keep scripts organized by function (maintenance/analysis/utilities)
- Place temporary files in archive/
- Use .gitignore for generated files

### Documentation
- Update README.md when adding new features
- Document complex scripts with usage examples
- Keep CHANGELOG updated for significant changes
