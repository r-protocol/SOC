# 🧪 Tests

This folder contains test scripts and examples.

## Test Scripts

### **test_ioc_extraction.py**
Tests IOC extraction from a specific article URL.

**Usage:**
```powershell
cd tests
python test_ioc_extraction.py
```

**Purpose:**
- Tests regex-based IOC extraction
- Validates defanged IOC handling
- Shows extracted domains, IPs, hashes, etc.

---

### **test_kql_integration.py**
Tests the complete KQL generation pipeline.

**Usage:**
```powershell
cd tests
python test_kql_integration.py
```

**Purpose:**
- Tests end-to-end KQL generation
- Validates database storage
- Checks query file exports

## Running Tests

### From Tests Directory:
```powershell
cd tests
python test_ioc_extraction.py
python test_kql_integration.py
```

### From Root Directory:
```powershell
python tests\test_ioc_extraction.py
python tests\test_kql_integration.py
```

## Test with Real Article

The easiest way to test with a real article:
```powershell
python main.py -s "https://article-url.com" --kql
```

See [Single Article Mode documentation](../docs/SINGLE_ARTICLE_MODE.md) for more details.

## Test Results

See [CONTI_TEST_SUCCESS.md](../docs/CONTI_TEST_SUCCESS.md) for an example of successful IOC extraction from a real CISA advisory.

## 📂 Navigation

- **[← Back to Main README](../README.md)** - Project overview
- **[→ Documentation](../docs/)** - Full documentation
