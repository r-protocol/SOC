# 📝 Single Article Processing Feature

## ✅ Feature Implemented

Added `-s` or `--source` parameter to process a single article URL for testing.

## 🚀 Usage

### **Basic Syntax:**
```powershell
python main.py -s "<URL>"
```

### **With KQL Generation:**
```powershell
python main.py -s "<URL>" --kql
```

Or using long form:
```powershell
python main.py --source "<URL>" --kql
```

## 📋 Examples

### **Example 1: Analyze Single Article**
```powershell
python main.py -s "https://www.bleepingcomputer.com/news/security/cisa-updates-conti-ransomware-alert-with-nearly-100-domain-names/"
```

**Output:**
- ✅ Fetches article content
- ✅ Checks cybersecurity relevance
- ✅ Analyzes with LLM (category, risk, summary)
- ✅ Displays results

### **Example 2: Analyze + Generate KQL**
```powershell
python main.py -s "https://www.bleepingcomputer.com/news/security/cisa-updates-conti-ransomware-alert-with-nearly-100-domain-names/" --kql
```

**Output:**
- ✅ Everything from Example 1
- ✅ LLM-based IOC extraction with context
- ✅ Regex-based IOC extraction (comparison)
- ✅ KQL query generation
- ✅ Side-by-side comparison
- ✅ Export to `.kql` files

## 🎯 What It Does

### **Phase 1: Fetch Article**
```
[INFO] Fetching article from: https://...
[SUCCESS] Successfully fetched: [Title]
[INFO] Content length: X characters
```

### **Phase 2: Check Relevance**
```
[RELEVANT] [Article Title]
[SUCCESS] Article is relevant: [Title]
```

### **Phase 3: LLM Analysis**
```
[ANALYZED] [Title] (Risk: HIGH/MEDIUM/LOW)

📊 Analysis Results
==================
Title: [Title]
Category: Ransomware/Malware/etc.
Threat Risk: HIGH/MEDIUM/LOW
Summary: [AI-generated summary]
```

### **Phase 4: KQL Generation** (if `--kql` flag used)

#### **4.1: LLM-Based Extraction**
```
🤖 LLM-Based IOC Extraction & KQL Generation
============================================

✅ LLM Extracted X IOCs:

  IPS: (5)
    • 192.168.1.1
      Context: attacker | Confidence: high
      Description: C2 server mentioned in article...
    
  DOMAINS: (10)
    • evil-domain.com
      Context: infrastructure | Confidence: high
      Description: Malware distribution domain...

✅ LLM Generated 4 KQL Queries:

  Query 1: Hunt for C2 Communication
    Type: IOC_Hunt
    Platform: Microsoft Defender
    Description: Detect network connections to attacker infrastructure
    Tables: DeviceNetworkEvents, CommonSecurityLog
```

#### **4.2: Regex-Based Extraction** (comparison)
```
⚡ Regex-Based IOC Extraction (for comparison)
==============================================

✅ Regex Extracted X IOCs:
  ips: 5
    • 192.168.1.1
    • 10.0.0.1
    ... and 3 more
  
  domains: 10
    • evil-domain.com
    • malicious.net
    ... and 8 more
```

#### **4.3: Comparison Summary**
```
📊 LLM vs Regex Comparison
==========================
LLM: 15 IOCs with context | 4 queries
Regex: 15 IOCs (no context) | Template-based
```

## 🎨 Features

### **LLM-Based IOC Extraction:**
- ✅ Context-aware (attacker/victim/infrastructure)
- ✅ Confidence scoring (high/medium/low)
- ✅ Descriptions from article
- ✅ Handles defanged IOCs (192[.]168[.]1[.]1)
- ✅ 9 IOC types: IPs, domains, URLs, hashes, CVEs, emails, filenames, registry keys, MITRE techniques

### **Regex-Based IOC Extraction:**
- ✅ Fast pattern matching
- ✅ Reliable fallback
- ✅ No LLM dependency
- ❌ No context understanding
- ❌ Can't handle defanged IOCs well

### **Query Generation:**
- ✅ Threat-specific KQL queries
- ✅ Context-aware filtering (excludes victim IPs)
- ✅ Multiple query types (IOC Hunt, Behavior Hunt, Vulnerability Hunt)
- ✅ Proper KQL syntax with comments
- ✅ Time filters and aggregations

## 📊 Command Line Options

| Parameter | Description | Example |
|-----------|-------------|---------|
| `-s <URL>` | Process single article URL | `-s "https://..."` |
| `--source <URL>` | Same as `-s` (long form) | `--source "https://..."` |
| `--kql` | Generate KQL queries | `--kql` |
| `-n <NUM>` | Limit articles (pipeline mode) | `-n 5` |
| `-debug` | Enable debug mode | `-debug` |

## 🔄 Comparison: Pipeline vs Single Article Mode

### **Pipeline Mode** (default):
```powershell
python main.py
```
- Fetches from all RSS feeds
- Processes weekly articles
- Generates report
- Optionally generates KQL

### **Single Article Mode**:
```powershell
python main.py -s "<URL>" --kql
```
- Fetches ONE specific article
- Perfect for testing
- Shows detailed IOC extraction comparison
- No report generation
- Directly shows results

## 💡 Use Cases

### **1. Test IOC Extraction**
Test if LLM can extract IOCs from a specific article:
```powershell
python main.py -s "https://article-with-iocs.com" --kql
```

### **2. Compare LLM vs Regex**
See side-by-side comparison:
```powershell
python main.py -s "https://article-url.com" --kql
```

### **3. Quick Analysis**
Get quick threat assessment:
```powershell
python main.py -s "https://latest-breach.com"
```

### **4. Validate Query Quality**
Check if generated queries are good:
```powershell
python main.py -s "https://ransomware-attack.com" --kql
# Check kql_queries/ folder for exported queries
```

## 📁 Output Files

When using `--kql` flag, queries are exported to:
```
kql_queries/
├── query_1_[timestamp].kql
├── query_2_[timestamp].kql
└── ...
```

## ⚠️ Notes

1. **Article must be publicly accessible** - No paywall
2. **Content extraction may vary** - Depends on website structure
3. **LLM requires Ollama running** - Falls back to regex if fails
4. **IOCs must be in visible text** - Can't extract from images/PDFs

## 🎯 Perfect For

- ✅ Testing new IOC extraction
- ✅ Validating LLM vs Regex
- ✅ Quick article analysis
- ✅ KQL query testing
- ✅ Demonstration/presentation
- ✅ Debugging IOC patterns

## 🚫 Not For

- ❌ Bulk processing (use pipeline mode)
- ❌ Report generation (use pipeline mode)
- ❌ Historical analysis (use pipeline mode)
- ❌ Database storage (single mode doesn't save)

## 📝 Example Session

```powershell
PS> python main.py -s "https://bleepingcomputer.com/conti-ransomware" --kql

======================================================================
🔍 Single Article Processing Mode
======================================================================

--- PHASE 1: Fetching Article ---
[SUCCESS] Successfully fetched: Conti Ransomware Analysis
[INFO] Content length: 5234 characters

--- PHASE 2: Checking Cybersecurity Relevance ---
[SUCCESS] Article is relevant: Conti Ransomware Analysis

--- PHASE 3: Analyzing Article with LLM ---
[ANALYZED] Conti Ransomware Analysis (Risk: HIGH)

📊 Analysis Results
==================
Title: Conti Ransomware Analysis
Category: Ransomware
Threat Risk: HIGH
Summary: Conti ransomware group targets healthcare...

--- PHASE 4: Generating KQL Queries (LLM + Regex) ---

🤖 LLM-Based IOC Extraction & KQL Generation
============================================

✅ LLM Extracted 23 IOCs:
  IPS: (3)
    • 45.67.89.10 | Context: attacker | Confidence: high
  
  DOMAINS: (15)
    • conti-payment[.]com | Context: infrastructure | Confidence: high
    ...

✅ LLM Generated 3 KQL Queries:
  Query 1: Hunt for Conti C2 Communication
  Query 2: Detect Conti File Hash
  Query 3: Hunt for Ransom Note Creation

⚡ Regex Extracted 25 IOCs:
  ips: 3
  domains: 18
  ...

📊 LLM vs Regex Comparison
==========================
LLM: 23 IOCs with context | 3 queries
Regex: 25 IOCs (no context) | Template-based

[SUCCESS] Exported 3 queries to 'kql_queries/' directory
[SUCCESS] Single article processing complete!
```

## 🎉 Summary

**Single article mode** is perfect for:
- 🧪 Testing and validation
- 📊 Comparing LLM vs Regex
- 🎯 Quick threat analysis
- 🔍 IOC extraction testing
- 💡 Demonstrations

**Use pipeline mode** for:
- 📰 Daily/weekly processing
- 📊 Report generation
- 💾 Database storage
- 📈 Historical tracking
