# Development Architecture & Approach

## Project Overview

This project implements a Python-based business intelligence system with four main components:
- `SpreadsheetManager`: Core Excel file operations
- `SalesLeadAnalyzer`: Sales leads analysis from "Leads.xlsx"
- `SalesAnalyzer`: Confirmed sales analysis from "Business.xlsm"
- `ChatThread` & `EmailChatThreadLoader`: Teams message processing from .eml files

## Current Architecture

### Core Classes

#### 1. SpreadsheetManager
**Purpose**: Foundation class for Excel file operations
**Key Features**:
- File opening/closing with context manager support
- Cell reading (by reference and coordinates)
- DataFrame reading with auto-detection
- DataFrame writing with positioning
- New spreadsheet creation
- Sheet name enumeration
- Empty cell detection

**File**: `src/tool_experiments/spreadsheet_manager.py`

#### 2. SalesLeadAnalyzer
**Purpose**: Analyze sales leads data with business logic
**Key Features**:
- Loads data from "Leads.xlsx" → "All deals" sheet
- Calculates "Sector" field based on "Deal owner" business rules
- Filtering methods: `getSummaryLeads()`, `getSummaryTotal()`, `getSummaryText()`
- Context manager support for resource management

**Business Logic**:
- Industry owners: ["Hamish Bignell", "Paul Tardio", "Beth Reeve", "Katie King"]
- All other owners → Government sector

**File**: `src/tool_experiments/sales_lead_analyzer.py`

#### 3. SalesAnalyzer
**Purpose**: Analyze confirmed sales data with performance optimization
**Key Features**:
- Loads data from "Business.xlsm" → "LD-Business" and "LG-Business" sheets
- Date range filtering for both industry and government data
- Caching system for performance optimization
- Client extraction methods: `getNewIndustryClients()`, `getNewGovClients()`
- Refactored to use configuration-driven approach

**Performance Optimizations**:
- Caching of underlying data to avoid repeated file loads
- Setup/teardown pattern in tests for single instance reuse
- Initial load: ~11.5 seconds, subsequent accesses: near-instant

**File**: `src/tool_experiments/sales_analyzer.py`

#### 4. ChatThread & Message Classes
**Purpose**: Model Teams conversation threads from email data
**Key Features**:
- `ChatThread`: Represents a single Teams conversation thread
- `Message`: Represents individual messages within threads
- Metadata storage: subject, date, thread_topic, message_id
- Participant tracking with order preservation
- Attachment metadata management
- LLM-friendly markdown rendering

**File**: `src/tool_experiments/chat_thread.py`

#### 5. EmailChatThreadLoader
**Purpose**: Parse .eml files and populate ChatThread objects
**Key Features**:
- Robust .eml file parsing with error handling
- Teams content detection and extraction
- Message parsing with participant, timestamp, and content
- Attachment reference extraction
- Batch loading with `load_threadList()` method
- Empty message filtering and content cleaning

**File**: `src/tool_experiments/chat_thread_loader.py`

## Development Approach

### 1. Test-Driven Development (TDD)
**Philosophy**: All features must have passing tests before being considered complete

**Test Organization**:
- **Primary Tests** (`@pytest.mark.primary`): Core functional behavior
- **Coverage Tests**: Edge cases, error handling, resilience

**Test Structure**:
```python
# ============================================================================
# PRIMARY TESTS - Core Functional Behavior
# ============================================================================
@pytest.mark.primary
def test_core_functionality():
    """Primary test: Shows main capability."""
    # Core functionality demonstration

# ============================================================================
# COVERAGE TESTS - Resilience & Edge Cases
# ============================================================================
def test_edge_case():
    """Coverage test: Edge case handling."""
    # Edge case validation
```

**Running Tests**:
```bash
# Primary tests only (fast development)
python -m pytest tests/ -m primary

# All tests (comprehensive validation)
python -m pytest tests/
```

### 2. Performance Optimization Strategy
**Problem**: Large Excel files (Business.xlsm) cause slow test execution
**Solution**: Setup/teardown pattern with single instance reuse

**Before**: ~244 seconds for full test suite
**After**: ~23 seconds for full test suite

**Implementation**:
```python
@classmethod
def setup_class(cls):
    """Set up analyzer once for all tests."""
    cls.analyzer = SalesAnalyzer(file_path)
    cls.analyzer.spreadsheet_manager.open()

@classmethod
def teardown_class(cls):
    """Clean up after all tests."""
    if cls.analyzer:
        cls.analyzer.close()
```

### 3. Caching Strategy
**Problem**: Repeated data loading from large files
**Solution**: Intelligent caching with range validation

**Implementation**:
- `_cached_data` dictionary stores loaded data
- `_ensureUnderlyingDataLoaded()` checks if cached data covers requested range
- Automatic cache refresh when larger ranges are requested

### 4. Code Refactoring Approach
**Philosophy**: Comments are a hint for refactoring. Method-level docstrings are required for all public and private methods, but inline comments should be avoided in favor of extracting code blocks into well-named private methods. This ensures that code intent is always clear from the method structure itself, improving readability and maintainability.

**Current Status**:
- This approach has been fully applied to `SalesAnalyzer`.
- The same refactoring is planned for `SalesLeadAnalyzer` and `SpreadsheetManager` as the next development steps.

**Before**:
```python
# ... code with inline comments and long methods ...
```
**After**:
```python
def _select_and_rename_required_columns(...):
    """Select and rename required columns, and convert Date column to datetime."""
    ...

def _filter_result_by_date_range(...):
    """Filter DataFrame by date range and reset index."""
    ...
```

## Data Sources

### 1. Leads.xlsx
**Sheet**: "All deals"
**Structure**: 52 rows, 12 columns + calculated "Sector" column
**Key Columns**:
- Record ID, Deal Name, Deal Stage, Deal owner
- Amount, Product or service, Sale Conviction
- Engagement Type, Joined, $, Type
- **Sector** (calculated field)

### 2. Business.xlsm
**Sheets**: "LD-Business" (Industry), "LG-Business" (Government)
**Structure**: Large files with date-based filtering
**Key Columns**:
- Client, Category, Product, Date, Total, Description

### 3. Teams Message Data (.eml files)
**Source**: Email forwards from Teams channel messages
**Structure**: Individual .eml files containing Teams conversation threads
**Key Elements**:
- Email headers (subject, date, thread_topic, message_id)
- Teams message content with participants and timestamps
- Attachment references and metadata
- LLM-friendly markdown rendering

## Error Handling Strategy

### 1. File System Errors
- `FileNotFoundError` for missing files
- Graceful handling with descriptive error messages

### 2. Data Validation
- Date range validation (start ≤ end)
- Sheet existence validation
- Column structure validation
- Teams content detection in .eml files

### 3. State Management
- RuntimeError for operations before data loading
- Context manager ensures proper cleanup

## Development Standards

### 1. Code Quality
- All code must pass linting and type checking
- Black formatting (88 character line length)
- Comprehensive docstrings
- **Refactoring Standard**: Avoid inline comments in implementation code. If a comment is needed, consider extracting the code to a well-named private method with a clear docstring instead. This is required for all new and refactored code.

### 2. Testing Requirements
- All features must have passing tests
- Primary tests demonstrate core functionality
- Coverage tests validate edge cases and error handling
- Performance considerations for large file operations
- Golden example tests for markdown output validation

### 3. Documentation
- Living documentation through test structure
- Clear separation of primary vs. coverage tests
- Performance metrics and optimization notes

## Performance Characteristics

### File Loading Times
- **Leads.xlsx**: Fast (< 1 second)
- **Business.xlsm**: Slow initial load (~11.5 seconds)
- **Cached access**: Near-instant
- **.eml files**: Fast individual processing, batch loading supported

### Test Execution Times
- **Primary tests only**: ~7 seconds
- **All tests**: ~23 seconds
- **Before optimization**: ~244 seconds

## Current Status

✅ **Completed**:
- Core class implementations (SpreadsheetManager, SalesLeadAnalyzer, SalesAnalyzer)
- Test-driven development approach
- Performance optimization
- Code refactoring
- Test organization with primary/coverage separation
- Comprehensive error handling
- Documentation structure
- New business filtering logic
- ClientStatus and Ongoing column integration
- **ChatThread and Message classes with comprehensive test coverage**
- **EmailChatThreadLoader with robust .eml parsing**
- **Markdown rendering for LLM-friendly output**
- **Batch processing of multiple .eml files**
- **Golden example tests for output validation**

🎯 **Current Focus**:
- **Business Intelligence Report Generation**: Combining processed Teams data with sales analysis
- **Real Test Case Development**: Creating scenarios using actual business data
- **Prompt Engineering**: Developing prompts for actionable business reports
- **Data Integration**: Merging chat threads with existing sales data

📋 **Planned**:
- GraphAPI integration for real-time Teams data access
- Advanced analytics and trend analysis
- Automated report scheduling and delivery
- Performance optimization for large datasets
- User interface for report generation
- Security and access control implementation

## Future Considerations

### 1. Scalability
- Consider database migration for very large datasets
- Implement incremental loading for partial data access
- Explore parallel processing for independent operations

### 2. Maintainability
- Monitor test execution times as data grows
- Consider test data fixtures for faster development
- Implement automated performance regression testing

### 3. Feature Extensions
- Additional business logic for sector classification
- More sophisticated caching strategies
- Integration with external data sources
- Advanced LLM processing and analysis features

---

*Last Updated: December 2024*
*Project: Tool Experiments - Business Intelligence System* 