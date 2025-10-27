# Scripts Directory

Organized collection of utility, maintenance, and analysis scripts for the Threat Intelligence system.

## Directory Structure

### 📁 maintenance/
Scripts for maintaining and reprocessing articles in the database.

- **`reprocess_articles.py`** - Unified script for reprocessing articles by ID, risk level, or category
  ```bash
  python scripts/maintenance/reprocess_articles.py --ids 210 213 215
  python scripts/maintenance/reprocess_articles.py --risk NOT_RELEVANT
  python scripts/maintenance/reprocess_articles.py --category "Malware" --dry-run
  ```

- **`analyze_unanalyzed.py`** - Find and analyze articles marked as UNANALYZED

- **`fix_crowdstrike_articles.py`** - Fix specific issues with CrowdStrike article processing

### 📁 analysis/
Scripts for checking and analyzing article data quality.

- **`check_db.py`** - Display database statistics and recent articles
- **`check_categorization.py`** - Validate article categorization accuracy
- **`check_high.py`** - Review HIGH risk articles for proper classification
- **`check_low_info.py`** - Review LOW and INFORMATIONAL articles

### 📁 utilities/
General utility scripts for listing and extracting data.

- **`list_not_relevant.py`** - List all NOT_RELEVANT articles with details
- **`list_unanalyzed.py`** - List all unanalyzed articles
- **`extract_iocs_from_existing.py`** - Extract IOCs from existing analyzed articles

## Usage Examples

### Reprocess Misclassified Articles
```bash
# Check what would be reprocessed (dry run)
python scripts/maintenance/reprocess_articles.py --risk NOT_RELEVANT --dry-run

# Actually reprocess them
python scripts/maintenance/reprocess_articles.py --risk NOT_RELEVANT
```

### Check Article Quality
```bash
# View database stats
python scripts/analysis/check_db.py

# Check HIGH risk articles
python scripts/analysis/check_high.py
```

### List Articles
```bash
# List NOT_RELEVANT articles
python scripts/utilities/list_not_relevant.py

# List unanalyzed articles
python scripts/utilities/list_unanalyzed.py
```

## Best Practices

1. **Always use --dry-run first** when reprocessing many articles
2. **Back up the database** before bulk operations
3. **Review results** after reprocessing with check scripts
4. **Use specific IDs** when possible instead of bulk operations

## Maintenance Schedule

- **Daily**: Check for unanalyzed articles
- **Weekly**: Review NOT_RELEVANT articles for misclassifications
- **Monthly**: Validate HIGH risk article classifications
