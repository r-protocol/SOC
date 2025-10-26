# --analyze Feature Documentation

## Overview

The `--analyze` feature allows you to analyze articles that are already stored in the database but haven't been analyzed yet. This is particularly useful when:

1. You've used `--fetch` to download articles for later processing
2. Previous analysis runs failed or were interrupted
3. You want to separate fetching from analysis (e.g., fetch during work hours, analyze overnight)

## Usage

### Basic Usage

```bash
python main.py --analyze
```

This will:
1. Find all articles in the database with `threat_risk = 'UNANALYZED'` or `category = 'Pending Analysis'`
2. Filter them for cybersecurity relevance
3. Analyze relevant articles with LLM
4. Update the database with analysis results
5. Display a summary of analyzed articles

### With Article Limit

```bash
python main.py --analyze -n 50
```

Analyze only the 50 most recent unanalyzed articles (useful for large backlogs).

### With KQL Generation

```bash
python main.py --analyze --kql
```

Analyze unanalyzed articles and automatically generate KQL queries for IOC extraction.

## Workflow Examples

### Workflow 1: Fetch Now, Analyze Later

```bash
# During work hours - just fetch articles (quick)
python main.py --fetch -t 30

# Later (evening/weekend) - analyze them (slower)
python main.py --analyze --kql
```

### Workflow 2: Batch Processing

```bash
# Fetch a large batch
python main.py --fetch -t 60

# Process in smaller chunks
python main.py --analyze -n 20
python main.py --analyze -n 20
python main.py --analyze -n 20
```

### Workflow 3: Recovery from Failed Analysis

If your analysis was interrupted:

```bash
# Check how many are unanalyzed
python main.py --stats

# Continue where you left off
python main.py --analyze
```

## Database States

Articles go through these states:

1. **Not in DB** → Initial state
2. **UNANALYZED** → After `--fetch` (stored but not analyzed)
3. **Analyzed** → After `--analyze` or full pipeline (has threat_risk, category, summary)
4. **NOT_RELEVANT** → Filtered out as not cybersecurity-related

## Checking Unanalyzed Articles

You can check for unanalyzed articles using:

```bash
# View database statistics (includes unanalyzed count)
python main.py --stats

# List unanalyzed articles
python main.py --list --risk UNANALYZED
```

## Benefits

- **Separation of Concerns**: Fetch during low-usage times, analyze when resources are available
- **Resource Management**: Analysis uses LLM heavily, fetching does not
- **Flexibility**: Process articles in chunks, pause/resume as needed
- **Error Recovery**: Re-run analysis on failed articles without re-fetching
- **Time Management**: Schedule fetching during work hours, analysis overnight

## Technical Details

### What Gets Analyzed

The `--analyze` feature queries for articles where:
- `threat_risk = 'UNANALYZED'` OR
- `category = 'Pending Analysis'`

### Processing Steps

1. **Find Unanalyzed**: Query database for unanalyzed articles
2. **Filter**: Apply cybersecurity relevance filtering
3. **Analyze**: Use LLM to analyze each article
4. **Update**: Store analysis results back in database
5. **Optional KQL**: Generate threat hunting queries if `--kql` flag is used

### Non-Relevant Articles

If articles are filtered out as not cybersecurity-related, they are marked with:
- `threat_risk = 'NOT_RELEVANT'`
- `category = 'Not Cybersecurity Related'`
- `summary = 'Filtered out - not relevant to cybersecurity'`

This prevents them from being re-processed in future `--analyze` runs.

## See Also

- `--fetch`: Fetch articles without analysis
- `--stats`: View database statistics
- `--list`: List articles in database
- Full pipeline: `python main.py` (fetch + analyze in one run)
