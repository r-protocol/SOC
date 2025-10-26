# Project Refactoring - October 2025

## Overview

This document describes the refactoring performed to organize the Threat Intelligence Pipeline project into a cleaner, more maintainable structure.

## Changes Made

### 1. New Folder Structure

Created a logical hierarchy:
- **src/** - All source code
  - **src/core/** - Core application modules (analysis, fetcher, filtering, report, KQL generators)
  - **src/utils/** - Utility modules (db_utils, logging_utils)
  - **src/config.py** - Configuration file
- **scripts/** - Utility and maintenance scripts
- **tests/** - All test files consolidated here
- **archive/** - Deprecated and debug files

### 2. Files Reorganized

#### Moved to `src/core/`:
- `analysis.py`
- `fetcher.py`
- `filtering.py`
- `report.py`
- `kql_generator.py`
- `kql_generator_llm.py`

#### Moved to `src/utils/`:
- `db_utils.py`
- `logging_utils.py`

#### Moved to `src/`:
- `config.py`

#### Moved to `scripts/`:
- `analyze_unanalyzed.py`
- `reprocess_not_relevant.py`
- `check_*.py` (all check scripts)
- `fix_crowdstrike_articles.py`

#### Moved to `tests/`:
- `test_*.py` (all test files consolidated)

#### Moved to `archive/`:
- `failed_json_debug.txt`
- `high_risk_articles.csv`
- `prompt_improvements.md`

### 3. Import Path Updates

All Python files were updated with new import paths:

**Before:**
```python
from config import OLLAMA_MODEL
from db_utils import initialize_database
from analysis import analyze_articles_sequential
```

**After:**
```python
from src.config import OLLAMA_MODEL
from src.utils.db_utils import initialize_database
from src.core.analysis import analyze_articles_sequential
```

**Scripts and tests** include path manipulation to work correctly:
```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```

### 4. Main Entry Point

`main.py` remains in the root directory as the primary entry point but now imports from the new structure.

## Benefits

1. **Better Organization**: Clear separation of concerns with core modules, utilities, and scripts
2. **Easier Navigation**: Related files are grouped together logically
3. **Improved Maintainability**: Easier to find and modify specific functionality
4. **Cleaner Root**: Root directory is no longer cluttered with many Python files
5. **Professional Structure**: Follows Python project best practices

## Running the Project

### Main Pipeline
```bash
python main.py
```

### Scripts
```bash
python scripts/analyze_unanalyzed.py
python scripts/check_high.py
```

### Tests
```bash
python tests/test_ioc_extraction.py
python tests/test_kql_integration.py
```

## Backwards Compatibility

The refactoring maintains full backwards compatibility:
- Database location unchanged (`threat_intel.db` in root)
- Configuration files location unchanged
- Output directories unchanged
- Dashboard structure unchanged
- All functionality works exactly as before

## Future Improvements

Consider for future:
1. Package the `src/` as an installable Python package
2. Add `setup.py` for proper installation
3. Use relative imports within `src/` modules
4. Add CI/CD configuration
5. Add `.gitignore` if using version control

## Migration Notes

If you have any custom scripts that import from the old structure, update them to use the new import paths as shown above.
