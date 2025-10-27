# IOC Extraction Improvements

## Problem Identified
You had 360 articles in your database but **0 IOCs extracted**. This happened because IOC extraction was only performed when you explicitly enabled KQL generation (which requires user confirmation or `--kql` flag).

## Root Cause
In the original pipeline:
1. Articles were fetched and analyzed ✅
2. IOCs were **only** extracted if you confirmed KQL generation ❌
3. The dashboard showed empty IOC stats because no IOCs were stored

## Solutions Implemented

### 1. **Automatic IOC Extraction During Analysis**
IOCs are now automatically extracted when articles are analyzed, without requiring KQL generation.

**New Config Settings** (`config.py`):
```python
# IOC Extraction Settings
AUTO_EXTRACT_IOCS = True  # Automatically extract IOCs during analysis
EXTRACT_IOCS_FOR_RISK_LEVELS = ['HIGH', 'MEDIUM']  # Only extract for these risk levels
```

**Behavior:**
- When enabled, IOCs are extracted automatically during the main pipeline
- Works for both `python main.py` (full pipeline) and `python main.py --analyze` (analyze existing articles)
- You can configure which risk levels should have IOCs extracted (default: HIGH and MEDIUM only)
- To extract IOCs from all articles, set `EXTRACT_IOCS_FOR_RISK_LEVELS = []`

### 2. **Dedicated IOC Extraction Script**
Created a new utility script to extract IOCs from existing articles in your database.

**Script:** `scripts/extract_iocs_from_existing.py`

**Usage Examples:**

```bash
# Extract IOCs from ALL articles (with KQL generation)
python scripts/extract_iocs_from_existing.py

# Extract IOCs from first 50 articles (testing)
python scripts/extract_iocs_from_existing.py -n 50

# Extract IOCs from HIGH risk articles only
python scripts/extract_iocs_from_existing.py --high-only

# Extract IOCs by specific risk level
python scripts/extract_iocs_from_existing.py --risk HIGH
python scripts/extract_iocs_from_existing.py --risk MEDIUM

# Extract IOCs only (skip KQL generation - faster)
python scripts/extract_iocs_from_existing.py --no-kql

# Combine filters
python scripts/extract_iocs_from_existing.py -n 100 --risk HIGH --no-kql
```

**Features:**
- Processes articles that have already been analyzed
- Skips articles marked as "Not Cybersecurity Related" or "NOT_RELEVANT"
- Shows real-time progress with IOC breakdown by type
- Generates KQL queries by default (can be disabled with `--no-kql`)
- Handles failures gracefully and continues processing

### 3. **Improved LLM IOC Extraction**
Enhanced the LLM-based IOC extractor to be more reliable:

**Improvements:**
- **Validation:** Removes hallucinated IPs (private/reserved ranges like 192.168.x.x, 203.0.113.x)
- **Confidence filtering:** Only stores medium/high confidence IOCs
- **Better prompts:** Explicitly instructs LLM not to invent example IOCs
- **Fallback:** Uses regex-based extraction if LLM fails
- **More IOC types:** Extracts IPs, domains, URLs, hashes, CVEs, emails, filenames, registry keys, MITRE ATT&CK techniques

## Recommended Workflow

### For New Articles (Going Forward)
Just run the normal pipeline with auto-extraction enabled:
```bash
python main.py
```

IOCs will be extracted automatically from HIGH and MEDIUM risk articles.

### For Existing 360 Articles (One-Time)
Extract IOCs from your existing articles:

**Option 1: Extract from all 360 articles**
```bash
python scripts/extract_iocs_from_existing.py
```
⏱️ **Time estimate:** ~30-60 minutes (depends on LLM speed)

**Option 2: Start with HIGH risk only (faster)**
```bash
python scripts/extract_iocs_from_existing.py --high-only
```
⏱️ **Time estimate:** ~5-15 minutes

**Option 3: Test with 20 articles first**
```bash
python scripts/extract_iocs_from_existing.py -n 20
```
⏱️ **Time estimate:** ~2-5 minutes

### For Custom Extraction
If you want to disable auto-extraction or change risk levels:

**Disable auto-extraction:**
```python
# In config.py
AUTO_EXTRACT_IOCS = False
```

**Extract from all risk levels:**
```python
# In config.py
EXTRACT_IOCS_FOR_RISK_LEVELS = []  # Empty = extract from all
```

**Extract from HIGH, MEDIUM, and LOW:**
```python
# In config.py
EXTRACT_IOCS_FOR_RISK_LEVELS = ['HIGH', 'MEDIUM', 'LOW']
```

## Expected Results

After running IOC extraction on your 360 articles, you should see:

**Dashboard Stats:**
- **IOC Types:** Domains, IPs, Hashes, CVEs, URLs, Emails
- **IOC Counts:** Varies by article content (some articles have many IOCs, others have none)
- **Recent Threats:** Will show IOC counts per article

**Typical IOC Distribution:**
- Articles about malware campaigns: 10-100+ IOCs (domains, hashes, C2 infrastructure)
- Articles about vulnerabilities: 1-10 IOCs (CVEs, affected URLs)
- Articles about breaches: 5-50 IOCs (domains, IPs, email addresses)
- Articles about general security news: 0-5 IOCs (may be informational only)

## Verification

Check IOC extraction results:

```bash
# Show overall stats
python main.py --stats

# List HIGH risk articles with IOC counts
python main.py --list --risk HIGH --limit 50

# Export all extracted IOCs
python main.py --export-iocs

# Show detailed article with IOCs
python main.py --show <article_id>
```

## Performance Notes

**IOC Extraction Speed:**
- With LLM (deepseek-coder-v2:16b): ~5-10 seconds per article
- With regex fallback: ~1 second per article
- For 360 articles: Approximately 30-60 minutes total

**Tips for Faster Processing:**
1. Use `--no-kql` flag to skip KQL generation (just extract IOCs)
2. Process in batches: `-n 50` at a time
3. Filter by risk level: `--high-only` or `--risk MEDIUM`
4. Run during off-hours to avoid blocking Ollama

## Troubleshooting

**Problem:** "No IOCs found in analyzed articles"
- Check if articles actually contain IOCs (many security news articles are just informational)
- Verify LLM is running: `curl http://localhost:11434/api/tags`
- Try with regex fallback enabled: `KQL_FALLBACK_TO_REGEX = True` in config

**Problem:** "LLM extraction failed"
- Ollama might be overloaded or not responding
- Check Ollama logs
- The script will automatically fall back to regex-based extraction

**Problem:** Script is too slow
- Use `--no-kql` to skip query generation
- Process in smaller batches: `-n 20`
- Filter to specific risk levels only

## Configuration Summary

**Key Settings in `config.py`:**

```python
# Enable/disable automatic IOC extraction
AUTO_EXTRACT_IOCS = True

# Risk levels to extract IOCs from (empty = all)
EXTRACT_IOCS_FOR_RISK_LEVELS = ['HIGH', 'MEDIUM']

# LLM settings (affects IOC extraction quality)
KQL_USE_LLM = True  # Use LLM for better context-aware extraction
KQL_FALLBACK_TO_REGEX = True  # Use regex if LLM fails
KQL_CONFIDENCE_THRESHOLD = 'medium'  # Filter IOCs by confidence
```

## Next Steps

1. **Extract IOCs from existing articles:**
   ```bash
   python scripts/extract_iocs_from_existing.py --high-only
   ```

2. **Verify results in dashboard:**
   - Start dashboard: `start_dashboard.bat`
   - Check IOC Stats widget
   - View articles with IOC counts

3. **Configure auto-extraction for future:**
   - Keep `AUTO_EXTRACT_IOCS = True` in config
   - Adjust `EXTRACT_IOCS_FOR_RISK_LEVELS` as needed

4. **Optional: Generate KQL queries:**
   ```bash
   python main.py --analyze --kql  # For existing articles
   python main.py --kql  # For new articles
   ```

## Summary

✅ **Before:** IOCs only extracted with manual KQL generation confirmation  
✅ **After:** IOCs automatically extracted during analysis  
✅ **Bonus:** Script to extract IOCs from existing 360 articles  
✅ **Result:** Dashboard will show real IOC statistics

Your next command should be:
```bash
python scripts/extract_iocs_from_existing.py --high-only
```

This will extract IOCs from all HIGH risk articles (fastest way to see results in dashboard).
