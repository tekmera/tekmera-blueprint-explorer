# Tekmera Architecture Documentation

This document describes the current architecture and package relationships of the Tekmera Explorer codebase.

## Top-Level Package Structure

Tekmera Explorer is organized into four main packages with clear separation of concerns:

```
src/tekmera/
├── clients/           # User interfaces and output formatting
├── functions/         # Pure functional analysis engine  
├── reporting/         # Report generation and visualization
└── meta/              # Cross-cutting concerns (types, utilities)
```

## Package Relationships

### Data Flow Architecture
```
Blueprint JSON → functions/ → reporting/ → clients/ → User Output
```

### Dependency Rules

1. **functions/** - Core analysis engine
   - Pure functional, no side effects
   - Platform-aware with auto-detection
   - No dependencies on other Tekmera packages
   - Contains blueprint and component analysis functions

2. **reporting/** - Report generation
   - Consumes functions/ output
   - Transforms analysis results into structured reports
   - Platform-specific formatting and visualization
   - **Depends on:** functions/, meta/

3. **clients/** - User interfaces
   - CLI commands and output formatting
   - Routes user requests to appropriate systems
   - **Depends on:** functions/, reporting/, meta/

4. **meta/** - Infrastructure
   - Type definitions, platform detection, utilities
   - Used by all other packages
   - No dependencies on other Tekmera packages

## Package Goals and Current Implementation

### clients/ - User Interface Package

**Goal:** Provide clean, user-friendly interfaces for accessing Tekmera functionality.

**Current Implementation:**
- `cli/main.py` - Main CLI entry point with Click commands
- `cli/formatters/` - Output formatting (HTML, table, JSON)
- `cli/single_use/` - Single-use command utilities

**Commands Available:**
- `tekmera search` - Search text content across blueprints
- `tekmera report` - Generate summary reports  
- `tekmera diff` - Compare blueprints
- `tekmera demo` - Generate sample reports

### functions/ - Analysis Engine Package

**Goal:** Pure functional analysis of blueprint data with platform awareness.

**Current Implementation:**
- `blueprints/` - Blueprint-level analysis (flexible input handling)
- `components/` - Component-level analysis (modules, routers, filters, etc.)
- `meta/` - Function registry, types, platform detection

**Key Characteristics:**
- All functions are pure (no side effects)
- Platform auto-detection with manual override
- Standardized ProjectionResult/ModuleResult output
- Supports both Workfront Fusion and Make.com

### reporting/ - Report Generation Package

**Goal:** Transform analysis results into structured, formatted reports.

**Current Implementation:**
- `summary/` - One-page summary reports
- `diff/` - Blueprint comparison reports
- `common/` - Shared reporting utilities

**Features:**
- Multiple output formats (table, JSON, HTML)
- Platform-specific report formatting
- Structured data with .to_text() and .to_dict() methods

### meta/ - Infrastructure Package

**Goal:** Provide shared infrastructure and cross-cutting concerns.

**Current Implementation:**
- Type definitions (Platform, ProjectionResult, etc.)
- Platform detection algorithms  
- Function registry and discovery
- Utility functions for component extraction

## Operational Rules

### System Boundaries
- All user commands route through clients/ → reporting/ → functions/
- Pure functional analysis in functions/ package
- Side effects isolated to clients/ package

### Platform Support  
- Both Workfront Fusion and Make.com supported
- Platform detection is automatic with manual override
- Each platform has dedicated implementation modules

### Code Organization Principles
- **Pure functions** in functions/ package
- **Side effects** isolated to clients/ package  
- **Platform-specific code** clearly separated by file
- **Shared utilities** centralized in meta/ package
- **Consistent naming** with platform suffixes (workfront_fusion.py, make_com.py)

## Current Status

**Active Development:** Pure functional system fully operational
**Commands Available:** search, report, diff, demo  
**Platform Coverage:** Workfront Fusion and Make.com
**Output Formats:** Table, JSON, HTML

The architecture provides a clean separation between analysis (functions), presentation (reporting), and user interface (clients), with shared infrastructure in meta/.