# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-10-20

### Added
- Command line argument `-n` to limit the number of articles processed
- Single progress bar per phase showing 0-100% progress in 50-character width
- Clean status message display above progress bars during processing
- Improved terminal output control with proper cursor management

### Changed
- Refactored progress bar implementation in `fetcher.py` for Phase 1 (Fetching)
- Refactored progress bar implementation in `filtering.py` for Phase 2 (Filtering)
- Refactored progress bar implementation in `analysis.py` for Phase 3 (Analysis)
- Updated `main.py` to support article limit parameter

### Fixed
- Multiple progress bars appearing during article processing
- Progress bar interference with status messages
- Progress bar not properly updating from 0-100%
- Terminal output flickering and duplication issues

## [1.0.0] - Initial Release

### Added
- Threat intelligence article fetching from multiple sources
- Article filtering based on relevance and keywords
- AI-powered article analysis for threat detection
- Report generation functionality
- Database utilities for storing threat data
- Logging system for tracking operations
- Configuration management
- Multi-phase processing pipeline

### Features
- Phase 1: Fetch articles from threat intelligence sources
- Phase 2: Filter articles based on configured criteria
- Phase 3: Analyze articles for threat indicators
- Phase 4: Generate comprehensive threat reports

---

## Version History

- **1.1.0** - Progress bar improvements and article limit feature
- **1.0.0** - Initial working version with core functionality
