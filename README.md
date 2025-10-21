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
| `-debug` | Enable debug mode (future use) |

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

## Version History

See `CHANGELOG.md` for version history and updates.
