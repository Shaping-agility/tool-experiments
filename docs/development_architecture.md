# Development Architecture & Approach

## Project Overview

This project implements a Python-based Excel spreadsheet analysis system with three main classes:
- `SpreadsheetManager`: Core Excel file operations
- `SalesLeadAnalyzer`: Sales leads analysis from "Leads.xlsx"
- `SalesAnalyzer`: Confirmed sales analysis from "Business.xlsm"

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

## Error Handling Strategy

### 1. File System Errors
- `FileNotFoundError` for missing files
- Graceful handling with descriptive error messages

### 2. Data Validation
- Date range validation (start ≤ end)
- Sheet existence validation
- Column structure validation

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

### 3. Documentation
- Living documentation through test structure
- Clear separation of primary vs. coverage tests
- Performance metrics and optimization notes

## Performance Characteristics

### File Loading Times
- **Leads.xlsx**: Fast (< 1 second)
- **Business.xlsm**: Slow initial load (~11.5 seconds)
- **Cached access**: Near-instant

### Test Execution Times
- **Primary tests only**: ~7 seconds
- **All tests**: ~23 seconds
- **Before optimization**: ~244 seconds

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

## Development Roadmap

### Phase 1: Core Infrastructure ✅
- Core class implementations
- Test-driven development approach
- Performance optimization
- Code refactoring
- Test organization with primary/coverage separation
- Comprehensive error handling
- Documentation structure

### Phase 2: Data Enhancement ✅
- Added ClientStatus and Ongoing columns from Excel sheets
- Implemented derived columns logic (ExistingClient, New)
- Added new business filtering logic
- Updated all tests to reflect new data structure
- Generated new golden answers for filtered output

### Phase 3: Product Standardization 🔄
**Next Priority**: Handle 'expert.id' product reference standardization

**Current Issue**: The data contains inconsistent product naming:
- Some entries use 'expert.id'
- Others use 'profile.id', 'atlas.id', 'economy.id', etc.
- Need to standardize product references for consistent reporting

**Proposed Solution**:
1. **Product Mapping System**: Create a mapping dictionary to standardize product names
2. **Normalization Method**: Add `_normalize_product_names()` method to SalesAnalyzer
3. **Configuration-Driven**: Store product mappings in configuration for easy maintenance
4. **Backward Compatibility**: Ensure existing functionality continues to work
5. **Test Updates**: Update tests to reflect standardized product names

**Implementation Plan**:
```python
# Example product mapping configuration
PRODUCT_MAPPINGS = {
    'expert.id': 'expert.id',
    'profile.id': 'profile.id', 
    'atlas.id': 'atlas.id',
    'economy.id': 'economy.id',
    'views.id': 'views.id',
    'forecast.id': 'forecast.id',
    'Forecast (SAFi)': 'forecast.id',
    # Add more mappings as needed
}
```

**Benefits**:
- Consistent product reporting across all outputs
- Easier data analysis and aggregation
- Improved data quality for business intelligence
- Foundation for future product categorization features

### Phase 4: Renewal vs New Sales Analysis 📋
**Priority**: Distinguish between renewals and straight new sales in summaries

**Current Issue**: The current summary logic treats all business equally, but there's a business need to distinguish between:
- **Renewals**: Existing clients with ongoing business (ExistingClient=True, Ongoing='Yes')
- **Straight New Sales**: Truly new business (ExistingClient=False OR Ongoing='No')

**Proposed Solution**:
1. **Enhanced Summary Methods**: Add renewal/new sales flags to client summaries
2. **Separate Reporting**: Create distinct summary methods for renewals vs new sales
3. **Business Intelligence**: Provide insights into renewal rates and new business acquisition
4. **Configuration Options**: Allow filtering by business type in summary methods

**Implementation Plan**:
```python
# Enhanced client summary with business type classification
def getClientSummaryWithType(self, client_name: str, client_type: str, start_date: date, end_date: date) -> dict:
    """Get client summary with business type classification."""
    summary = self.getClientSummary(client_name, client_type, start_date, end_date)
    
    # Determine business type based on derived columns
    data = self._ensureUnderlyingDataLoaded(client_type, start_date, end_date)
    client_data = self._filter_data_by_client(data, client_name)
    
    # Classify business type
    if client_data['ExistingClient'].any() and not (client_data['Ongoing'].str.lower() == 'no').any():
        business_type = 'renewal'
    else:
        business_type = 'new_sale'
    
    summary['business_type'] = business_type
    return summary

# Separate summary methods for different business types
def getRenewalSummary(self, client_type: str, start_date: date, end_date: date) -> str:
    """Generate markdown summary of renewal business only."""
    
def getNewSalesSummary(self, client_type: str, start_date: date, end_date: date) -> str:
    """Generate markdown summary of new sales only."""
```

**Benefits**:
- Better business intelligence and reporting
- Ability to track renewal rates vs new business acquisition
- More granular analysis for strategic decision making
- Foundation for advanced business metrics and KPIs

### Phase 5: Teams Message Processing & Email Analysis 📋
**Priority**: Process email contents from Teams channel messages to extract structured information for LLM consumption

**Business Context**: Employees share success messages in Teams channels, which are forwarded as email messages. Each email encapsulates one message thread. The goal is to process these and render them into structured markdown format for easy LLM information extraction.

**Use Case Example**: Taking information about a new sale (e.g., Blue Mountains) and looking for corresponding Teams discussions to extract commentary and insights.

**Current Issue**: Need to build capability to model message threads from emails as structured data objects for analysis and reporting.

**Proposed Solution**:
1. **ChatThread Class**: Create abstraction layer for message thread processing
2. **Email Processing**: Parse .eml files to extract Teams message content
3. **Structured Output**: Generate JSON objects representing message threads
4. **Markdown Rendering**: Convert structured data to LLM-friendly markdown format
5. **Future Integration**: Prepare for GraphAPI integration (currently using sample .eml files)

**Implementation Plan**:
```python
# Proposed ChatThread class structure (interface to be determined)
class ChatThread:
    """Represents a single chat thread from Teams channel messages."""
    
    def __init__(self, email_file_path: Path):
        """Initialize from .eml file."""
        
    def get_messages(self) -> list[Message]:
        """Get all messages in the thread."""
        
    def get_participants(self) -> list[str]:
        """Get all participants in the thread."""
        
    def get_thread_summary(self) -> dict:
        """Get structured summary of the thread."""
        
    def to_markdown(self) -> str:
        """Render thread as LLM-friendly markdown."""
```

**Phase 5a: Interface Discovery** 🔄
**Next Priority**: Explore .eml file contents to determine optimal ChatThread interface

**Current Issue**: Need to understand the structure and content of sample .eml files to design appropriate interface for ChatThread class.

**Implementation Plan**:
1. **File Analysis**: Examine sample .eml files in data/raw folder
2. **Content Mapping**: Identify key data elements (participants, timestamps, messages, attachments)
3. **Interface Design**: Work collaboratively to determine ChatThread class interface
4. **Prototype Development**: Create initial implementation based on discovered structure
5. **Test Development**: Establish test patterns for email processing functionality

**Benefits**:
- Foundation for Teams message analysis and reporting
- Structured data extraction for business intelligence
- LLM-friendly format for automated information processing
- Integration capability with existing sales analysis system

### Phase 6: Future Enhancements 📋
- Additional business logic features
- Enhanced caching strategies
- Performance regression testing
- Advanced filtering and reporting capabilities
- GraphAPI integration for real-time Teams data
- Advanced LLM processing and analysis features

## Current Status

✅ **Completed**:
- Core class implementations
- Test-driven development approach
- Performance optimization
- Code refactoring
- Test organization with primary/coverage separation
- Comprehensive error handling
- Documentation structure
- New business filtering logic
- ClientStatus and Ongoing column integration

🔄 **In Progress**:
- Performance monitoring and optimization
- Test execution time improvements
- **NEW**: Teams message processing interface discovery and design

📋 **Planned**:
- Product standardization (expert.id handling)
- ChatThread class implementation and email processing
- Teams message analysis and markdown rendering
- Additional business logic features
- Enhanced caching strategies
- Performance regression testing
- GraphAPI integration for Teams data

---

*Last Updated: December 2024*
*Project: Tool Experiments - Excel Analysis System* 