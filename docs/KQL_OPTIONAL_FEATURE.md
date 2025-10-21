# KQL Generation - Now Optional with User Prompt! 🎯

## What Changed?

KQL query generation is now **optional** and happens **after** the report is generated, giving you control over when to run it.

---

## How It Works Now

### 🔄 New Workflow:

```
Phase 1: Fetch Articles
         ↓
Phase 2: Filter Articles
         ↓
Phase 3: Analyze with LLM
         ↓
Phase 4: Store to Database
         ↓
Phase 5: Generate Report ✅
         ↓
    [USER PROMPT] ← NEW!
         ↓
Phase 6: Generate KQL (Optional)
```

---

## Usage Options

### Option 1: Interactive Prompt (Default)

```bash
python main.py
```

**What happens:**
1. Pipeline runs phases 1-5 normally
2. Report is generated ✅
3. **You see this prompt:**

```
======================================================================
📊 KQL Threat Hunting Query Generator
======================================================================

Would you like to generate KQL threat hunting queries?
This will:
  • Extract IOCs (IPs, domains, hashes, CVEs, URLs) from analyzed articles
  • Generate KQL queries for Microsoft Defender/Sentinel
  • Store queries in database and export to .kql files

Generate KQL queries? (y/n): _
```

4. **Type `y`** → KQL queries are generated
5. **Type `n`** → Skip KQL generation, pipeline ends

---

### Option 2: Auto-Generate (No Prompt)

```bash
python main.py --kql
```

or

```bash
python main.py --auto-kql
```

**What happens:**
- Pipeline runs all phases including KQL generation
- No prompt, automatically generates queries
- Useful for automation/scheduled runs

---

### Option 3: Test with Limited Articles

```bash
python main.py -n 5
```

**What happens:**
- Processes only 5 articles
- Still prompts for KQL generation
- Useful for testing

---

### Option 4: Combined (Test + Auto KQL)

```bash
python main.py -n 3 --kql
```

**What happens:**
- Processes 3 articles
- Automatically generates KQL without prompt
- Best for quick testing

---

## When to Use Each Option

| Scenario | Command | Why |
|----------|---------|-----|
| **Production Run** | `python main.py` | Review report first, decide on KQL |
| **Automated/Scheduled** | `python main.py --kql` | No manual intervention needed |
| **Testing Changes** | `python main.py -n 5` | Quick test, decide on KQL later |
| **Quick Full Test** | `python main.py -n 3 --kql` | Fast end-to-end validation |

---

## Configuration

You can still disable KQL entirely in `config.py`:

```python
ENABLE_KQL_GENERATION = False  # Disables KQL feature completely
```

When disabled:
- No prompt will appear
- KQL generation is skipped
- Useful if you don't use Microsoft Defender/Sentinel

---

## Benefits of This Approach

✅ **Flexibility**: Choose when to generate KQL queries
✅ **Review First**: Check the report before committing to KQL generation
✅ **Save Time**: Skip KQL if not needed for a particular run
✅ **Automation Friendly**: Use `--kql` flag for scheduled runs
✅ **Testing**: Use `-n` to test without processing all articles

---

## Example Session

### Interactive Mode:
```bash
PS> python main.py -n 3

[SUCCESS] Database initialized successfully.

--- PHASE 1: Fetching and Scraping New Articles ---
[SUCCESS] Found 3 new articles

--- PHASE 2: Filtering New Articles for Cybersecurity Relevance ---
[SUCCESS] Found 2 relevant articles

--- PHASE 3: Analyzing New Relevant Articles with LLM ---
[ANALYZED] Article 1 (Risk: HIGH)
[ANALYZED] Article 2 (Risk: MEDIUM)

--- PHASE 4: Storing New Data in Database ---
[SUCCESS] Stored 2 new articles

--- PHASE 5: Generating Weekly Report ---
[SUCCESS] Report generated: Threat_Intelligence_Report_2025-10-22.docx
[SUCCESS] Pipeline finished successfully!

======================================================================
📊 KQL Threat Hunting Query Generator
======================================================================

Would you like to generate KQL threat hunting queries?
This will:
  • Extract IOCs (IPs, domains, hashes, CVEs, URLs) from analyzed articles
  • Generate KQL queries for Microsoft Defender/Sentinel
  • Store queries in database and export to .kql files

Generate KQL queries? (y/n): y

--- KQL: Generating KQL Threat Hunting Queries ---
[INFO] Generated 3 queries for 'Article 1'
[INFO] Generated 2 queries for 'Article 2'
[SUCCESS] Exported 5 queries to 'kql_queries/' directory
[SUCCESS] KQL Generation complete: 45 IOCs, 5 queries stored
```

### Auto Mode:
```bash
PS> python main.py -n 3 --kql

[... phases 1-5 run ...]
[SUCCESS] Pipeline finished successfully!

--- KQL: Generating KQL Threat Hunting Queries ---
[INFO] Generated 3 queries for 'Article 1'
[SUCCESS] KQL Generation complete: 45 IOCs, 5 queries stored
```

---

## Technical Details

### Code Changes:

1. **Extracted KQL logic** into `generate_kql_for_articles()` function
2. **Added prompt function** `prompt_kql_generation()` with colored output
3. **Modified main pipeline**:
   - Report is always Phase 5
   - KQL generation happens after report (if enabled)
   - Checks for `--kql` or `--auto-kql` flags
4. **Updated phase numbering** to be consistent

### Command Line Flags:

| Flag | Purpose |
|------|---------|
| `-n <number>` | Limit articles processed |
| `--kql` | Auto-generate KQL (skip prompt) |
| `--auto-kql` | Same as `--kql` |

---

## Backwards Compatibility

✅ **Old behavior**: KQL always ran if enabled in config
✅ **New behavior**: Prompts user, but can use `--kql` for old behavior
✅ **Config still works**: `ENABLE_KQL_GENERATION = False` disables entirely

---

## What's Next?

The KQL generator is now user-friendly and flexible. Future enhancements could include:

- Add `--no-kql` flag to explicitly skip (with prompt)
- Save user preference (always generate / never generate)
- Add KQL queries to the Word report
- MITRE ATT&CK mapping (Phase 2)

---

## Files Modified

- ✅ `main.py` - Refactored KQL generation to be optional
- ✅ `README.md` - Updated with new usage options
- ✅ Documentation - This guide

---

**You're now in full control of when KQL queries are generated!** 🎉
