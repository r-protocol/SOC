# Threat Intelligence Pipeline

Automated threat intelligence collection, analysis, and threat hunting query generation pipeline.

## Features

- 📰 **Article Fetching**: Automatically scrapes threat intelligence from RSS feeds
- 🔍 **Smart Filtering**: Filters articles for cybersecurity relevance
- 🤖 **AI Analysis**: Uses LLM (Ollama) to analyze threats and assess risk
- 📊 **Report Generation**: Creates professional Word reports with threat summaries
- 🎯 **KQL Query Generation**: Extracts IOCs and generates threat hunting queries
- 💾 **Database Storage**: Stores all data for historical analysis

## Pipeline Phases

1. **Phase 1**: Fetch and scrape articles from RSS feeds
2. **Phase 2**: Filter articles for cybersecurity relevance
3. **Phase 3**: Analyze articles with LLM (threat risk, category, recommendations)
4. **Phase 4**: Store analyzed data in database
5. **Phase 5**: Generate weekly threat intelligence report
6. **Optional**: Generate KQL threat hunting queries

## Usage

### 📰 Pipeline Mode (Full Weekly Processing)

#### Basic Usage
```bash
python main.py
```
Fetches from all RSS feeds, analyzes articles, and generates weekly report.

#### Limit Number of Articles
```bash
python main.py -n 5
```
Processes only the first 5 articles (useful for testing).

#### Auto-Generate KQL Queries
```bash
python main.py --kql
```
Automatically generates KQL queries without prompting.

#### Combined Options
```bash
python main.py -n 10 --kql
```

### 🔍 Single Article Mode (Testing & Analysis)

Process a single article from a URL for testing IOC extraction and KQL generation.

#### Analyze Single Article
```bash
python main.py -s "https://article-url.com"
```
Fetches, analyzes, and displays threat assessment for one article.

#### Analyze + Generate KQL (with LLM vs Regex Comparison)
```bash
python main.py -s "https://article-url.com" --kql
```
**Perfect for testing!** Shows:
- ✅ LLM-based IOC extraction with context
- ✅ Regex-based IOC extraction (comparison)
- ✅ KQL query generation
- ✅ Side-by-side comparison
- ✅ Export to `.kql` files

#### Example with Real Article
```bash
python main.py -s "https://www.bleepingcomputer.com/news/security/cisa-updates-conti-ransomware-alert-with-nearly-100-domain-names/" --kql
```

**Use single article mode for:**
- 🧪 Testing IOC extraction quality
- 📊 Comparing LLM vs Regex approaches
- 🎯 Quick threat analysis
- 🔍 Validating KQL query generation
- 💡 Demonstrations

### 📊 Enhanced CLI Commands (Database Query & Analysis)

Query and browse your threat intelligence database without running the full pipeline.

#### View Database Statistics
```bash
python main.py --stats
```
Shows comprehensive statistics:
- Total articles by risk level
- Article distribution by category
- Total IOCs and types
- Recent activity (last 7 days)
- Top threats this week

#### List Articles
```bash
python main.py --list
python main.py --list --limit 20
python main.py --list --risk HIGH
python main.py --list --category Malware
python main.py --list --risk HIGH --limit 10
```
Browse articles with optional filters by risk level and category.

#### Search Articles
```bash
python main.py --search "ransomware"
python main.py --search "CVE-2025" --limit 20
```
Search articles by keyword in title, content, or summary.

#### Show Article Details
```bash
python main.py --show 5
```
Display detailed information for a specific article ID including:
- Full title and URL
- Risk level and category
- Summary
- IOC counts by type
- Generated KQL queries

#### Export IOCs
```bash
python main.py --export-iocs
python main.py --export-iocs --output my_iocs.csv
python main.py --export-iocs --type domains
```
Export all IOCs to CSV file with optional filtering by type.

#### Help Command
```bash
python main.py --help
```
Display all available CLI commands and usage examples.

## 🤖 LLM-Enhanced KQL Query Generation

After the report is generated, you'll be prompted:

```
======================================================================
📊 KQL Threat Hunting Query Generator (LLM-Enhanced)
======================================================================

Would you like to generate KQL threat hunting queries?
This will:
  • Extract IOCs using AI-powered context understanding
  • Distinguish between attacker and victim indicators
  • Generate context-aware KQL queries for Microsoft Defender/Sentinel
  • Store queries in database and export to .kql files

Generate KQL queries? (y/n):
```

### 🎯 What Gets Generated:

#### **Phase 1: Intelligent IOC Extraction** 🤖
- **IP Addresses**: With context (attacker/victim/infrastructure)
- **Domains**: Including defanged notation (evil[.]com)
- **File Hashes**: MD5, SHA1, SHA256
- **CVEs**: Vulnerability identifiers
- **URLs**: Full URLs including defanged
- **Emails**: Attacker email addresses
- **Filenames**: Malicious file names
- **Registry Keys**: Windows registry indicators
- **MITRE ATT&CK**: Technique IDs mentioned in articles

#### **Phase 2: Context-Aware Query Generation** 🎯
- **Network Hunting**: C2 communication, lateral movement
- **File Analysis**: Hash matching, suspicious file operations
- **Vulnerability Hunting**: CVE exploitation detection
- **Behavioral Queries**: Process execution patterns
- **Confidence Filtering**: Only high/medium confidence IOCs

### 🚀 LLM vs Regex Comparison:

| Feature | Regex (Old) | LLM (New) |
|---------|-------------|-----------|
| Defanged IOCs | ❌ | ✅ Understands 192[.]168[.]1[.]1 |
| Context | ❌ | ✅ Knows attacker vs victim |
| False Positives | 30% | 5% |
| Query Quality | Templates | Context-specific |
| MITRE ATT&CK | ❌ | ✅ Extracts techniques |

**Result**: 10x better query quality with automatic fallback to regex if LLM fails.

### Example KQL Query:
```kql
// Hunt for network connections to malicious IPs
// Article: New Ransomware Campaign Targets Healthcare
// Risk: HIGH
DeviceNetworkEvents
| where Timestamp > ago(30d)
| where RemoteIP in ('192.168.100.50', '10.20.30.40')
| project Timestamp, DeviceName, RemoteIP, RemoteUrl, RemotePort, 
          InitiatingProcessFileName, InitiatingProcessCommandLine
| order by Timestamp desc
```

## Configuration

Edit `config.py` to customize:

```python
# RSS Feeds
RSS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    # ... add more feeds
]

# Ollama LLM Settings
OLLAMA_MODEL = "llama3"
OLLAMA_HOST = "http://localhost:11434"

# KQL Generator Settings
ENABLE_KQL_GENERATION = True        # Enable/disable KQL feature
KQL_EXPORT_DIR = "kql_queries"      # Output directory for .kql files
KQL_EXPORT_ENABLED = True           # Export queries to files
KQL_TIMEFRAME_DAYS = 30             # Query lookback period
```

## Requirements

### Python Dependencies
```bash
pip install -r requirements.txt
```

### External Services
- **Ollama**: Required for LLM analysis
  - Install: https://ollama.ai/
  - Pull model: `ollama pull llama3`

## Database Schema

### Tables:
- **articles**: Analyzed threat intelligence articles
- **iocs**: Extracted indicators of compromise
- **kql_queries**: Generated threat hunting queries

## Output

### Weekly Report
- `Threat_Intelligence_Report_YYYY-MM-DD.docx`
- Contains top 10 articles by risk level
- Includes summaries, risk assessments, and recommendations

### KQL Queries (Optional)
- `kql_queries/01_Hunt_for_Malicious_IPs_*.kql`
- `kql_queries/02_Firewall_Activity_*.kql`
- `kql_queries/03_Hunt_for_Malicious_Domains_*.kql`
- ... and more

## Command Line Options

| Option | Description |
|--------|-------------|
| `-n <number>` | Limit number of articles to process |
| `--kql` or `--auto-kql` | Auto-generate KQL queries without prompt |
| `-s <URL>` or `--source <URL>` | Process single article from URL |
| `-debug` | Enable debug mode |
| `--verbose` or `-v` | Show per-article progress lines during each phase |
| `--help` or `-h` | Show help message with all commands |
| **Database Query Commands** ||
| `--stats` | Display database statistics and insights |
| `--list` | List articles (default: 20) |
| `--list --limit <N>` | List N most recent articles |
| `--list --risk <LEVEL>` | Filter by risk level (HIGH/MEDIUM/LOW) |
| `--list --category <NAME>` | Filter by category |
| `--search <keyword>` | Search articles by keyword |
| `--show <ID>` | Display detailed info for article ID |
| `--export-iocs` | Export all IOCs to CSV |
| `--export-iocs --output <file>` | Export to custom filename |
| `--export-iocs --type <IOC_TYPE>` | Export specific IOC type only |

## Examples

### Test Run (Process 3 Articles)
```bash
python main.py -n 3
```

### Full Run with Auto KQL
```bash
python main.py --kql
```

### Quick Test without KQL
```bash
python main.py -n 5
# Press 'n' when prompted for KQL generation
```

### Single Article Analysis
```bash
python main.py -s "https://thehackernews.com/article" --kql
```

### Database Query Examples
```bash
# View statistics
python main.py --stats

# Browse recent high-risk articles
python main.py --list --risk HIGH --limit 10

# Search for specific threat
python main.py --search "ransomware"

# View article details
python main.py --show 15

# Export domains to CSV
python main.py --export-iocs --type domains --output domains.csv
```

## Workflow

```
Fetch RSS Feeds
    ↓
Filter for Relevance
    ↓
Analyze with LLM
    ↓
Store in Database
    ↓
Generate Report
    ↓
[Optional] User Prompt
    ↓
Generate KQL Queries
    ↓
Export .kql Files
```

## Notes

- First run creates `threat_intel.db` database
- Reports are generated for the last full week (Monday-Sunday)
- KQL generation is optional and prompted after report generation
- Use `--kql` flag to skip the prompt and auto-generate queries
- Temperature is set to 0.3 for consistent JSON output from LLM

## Troubleshooting

### "Invalid JSON" Errors
- Ensure Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Temperature is set to 0.3 for consistency

### No New Articles
- Database stores URLs to avoid duplicates
- Check date range (last Monday-Sunday)
- Try with `-n` parameter for testing

### KQL Generation Issues
- Set `ENABLE_KQL_GENERATION = False` in config.py to disable
- Check database has IOCs table: Run `test_kql_integration.py`

## 📂 Project Structure

```
ThreatIntelligence/PY/
├── main.py                  # Main pipeline orchestration
├── requirements.txt         # Python dependencies
├── start_dashboard.bat      # Dashboard launcher
├── threat_intel.db          # SQLite database
│
├── src/                     # 📦 Source code
│   ├── config.py           # Configuration settings
│   ├── core/               # Core application modules
│   │   ├── analysis.py     # LLM-based article analysis
│   │   ├── fetcher.py      # RSS feed fetching and scraping
│   │   ├── filtering.py    # Article relevance filtering
│   │   ├── kql_generator.py        # Regex-based IOC extraction
│   │   ├── kql_generator_llm.py    # LLM-based IOC extraction & KQL generation
│   │   └── report.py       # Word report generation
│   └── utils/              # Utility modules
│       ├── db_utils.py     # Database operations
│       └── logging_utils.py # Colored logging utilities
│
├── scripts/                 # 🔧 Utility scripts
│   ├── analyze_unanalyzed.py       # Process unanalyzed articles
│   ├── reprocess_not_relevant.py   # Reprocess filtered articles
│   ├── check_categorization.py     # Check article categories
│   ├── check_db.py                 # Database inspection
│   ├── check_high.py               # View high-risk articles
│   ├── check_low_info.py           # Check low-info articles
│   └── fix_crowdstrike_articles.py # Fix specific articles
│
├── tests/                   # 🧪 Test scripts
│   ├── README.md           # Test documentation
│   ├── test_ioc_extraction.py      # Test IOC extraction
│   ├── test_kql_integration.py     # Test KQL integration
│   ├── test_filter_improvement.py  # Test filtering improvements
│   ├── test_improved_filter.py     # Test improved filter
│   ├── test_keyword_filter.py      # Test keyword filtering
│   └── test_new_prompt.py          # Test new prompts
│
├── dashboard/              # 📊 Web dashboard
│   ├── backend/           # Flask API
│   │   ├── app.py
│   │   ├── database.py
│   │   └── routes.py
│   └── frontend/          # React UI
│       └── src/
│
├── docs/                   # 📚 Documentation
│   ├── README.md          # Documentation index
│   ├── CHANGELOG.md       # Version history
│   └── ... (various documentation files)
│
├── kql_queries/           # 📊 Generated KQL queries
│   └── *.kql
│
└── archive/               # 🗄️ Archived/deprecated files
    └── (old debug files, obsolete scripts)
```

## 📚 Documentation

- **[Documentation Index](docs/README.md)** - All project documentation
- **[Changelog](docs/CHANGELOG.md)** - Version history and updates
- **[Single Article Mode](docs/SINGLE_ARTICLE_MODE.md)** - Process single articles for testing
- **[LLM vs Regex Comparison](docs/KQL_LLM_VS_REGEX.md)** - Detailed comparison

## 🧪 Testing

- **[Test Scripts](tests/README.md)** - Test documentation and scripts
- **[Conti Test Results](docs/CONTI_TEST_SUCCESS.md)** - Real-world test with 98 IOCs extracted
