# Teams Message Processing Architecture

## Overview

This document outlines the architecture and design approach for processing Teams channel messages that have been forwarded as email (.eml files) to extract structured information for LLM consumption and business intelligence.

## Business Context

### Use Case
Employees share success messages and business updates in Teams channels. These messages are forwarded as email messages, with each email encapsulating one message thread. The goal is to:

1. **Process these email messages** to extract structured data
2. **Render them into markdown format** that's optimized for LLM consumption
3. **Enable business intelligence** by correlating sales data with Teams discussions
4. **Extract insights** about client relationships, project progress, and business opportunities

### Example Scenario
- Sales data shows a new sale to "Blue Mountains"
- Search through Teams discussions to find related conversations
- Extract commentary, insights, and context about the sale
- Generate structured summary for business reporting

## Technical Architecture

### Core Components

#### 1. ChatThread Class
**Purpose**: Primary abstraction for representing a single Teams message thread

**Responsibilities**:
- Parse .eml files to extract Teams message content
- Model message thread as structured data
- Provide interface for accessing thread information
- Generate LLM-friendly markdown output

**Proposed Interface** (to be refined through exploration):
```python
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
        
    def get_metadata(self) -> dict:
        """Get thread metadata (date, channel, subject, etc.)."""
```

#### 2. Message Class
**Purpose**: Represent individual messages within a thread

**Responsibilities**:
- Store message content, sender, timestamp
- Handle different message types (text, reactions, attachments)
- Provide formatted output for different contexts

#### 3. EmailProcessor Class
**Purpose**: Handle .eml file parsing and Teams message extraction

**Responsibilities**:
- Parse .eml file format
- Extract Teams-specific message content
- Handle different email formats and structures
- Provide error handling for malformed emails

### Data Flow

```
.eml file → EmailProcessor → ChatThread → Structured JSON → Markdown Output
```

## Development Approach

### Phase 1: Interface Discovery 🔄
**Current Priority**: Understand .eml file structure to design optimal interface

**Tasks**:
1. **File Analysis**: Examine sample .eml files in data/raw folder
2. **Content Mapping**: Identify key data elements:
   - Message participants and roles
   - Timestamps and threading
   - Message content and formatting
   - Attachments and media
   - Reactions and responses
3. **Interface Design**: Collaborate on ChatThread class interface
4. **Prototype Development**: Create initial implementation
5. **Test Development**: Establish test patterns

### Phase 2: Core Implementation
**Objective**: Implement ChatThread class with basic functionality

**Tasks**:
1. **EmailProcessor Implementation**: Parse .eml files
2. **Message Class Implementation**: Model individual messages
3. **ChatThread Implementation**: Core thread functionality
4. **Basic Markdown Rendering**: Simple text output
5. **Comprehensive Testing**: Primary and coverage tests

### Phase 3: Advanced Features
**Objective**: Enhanced functionality and integration

**Tasks**:
1. **Rich Markdown Rendering**: Optimized for LLM consumption
2. **Search and Filtering**: Find threads by content, participants, dates
3. **Integration with Sales Data**: Correlate with existing business data
4. **Performance Optimization**: Handle large email files efficiently
5. **GraphAPI Preparation**: Design for future real-time data access

## Data Sources

### Current: Sample .eml Files
**Location**: `data/raw/` folder
**Format**: Standard .eml email files containing Teams message threads
**Sample Files**:
- Community Views for City of Armadale in Perth.eml
- Infrastructure WA looks to Community Views to make informed decisions!.eml
- re-engaged by the NSW Night Time Commissioner.eml
- Livingstone Shire Council signs for 3 years of Community Views.eml
- And many more...

### Future: GraphAPI Integration
**Objective**: Access Teams data directly via Microsoft Graph API
**Benefits**: Real-time data, better structure, richer metadata
**Considerations**: Authentication, rate limiting, data permissions

## Integration with Existing System

### Sales Analysis Integration
**Opportunity**: Correlate Teams discussions with sales data

**Potential Features**:
- Search Teams discussions by client name
- Extract insights about sales process and client relationships
- Generate enriched business reports with social context
- Track sentiment and engagement around business opportunities

### Reporting Enhancement
**Opportunity**: Enhanced business intelligence through social data

**Potential Features**:
- Client relationship insights from Teams discussions
- Project progress tracking through message analysis
- Competitive intelligence from internal discussions
- Success story extraction and documentation

## Technical Considerations

### Performance
**Challenge**: Large .eml files with complex message threads
**Solution**: Efficient parsing and caching strategies
**Monitoring**: File size, processing time, memory usage

### Data Quality
**Challenge**: Inconsistent email formats and Teams message structures
**Solution**: Robust parsing with error handling
**Validation**: Data integrity checks and validation

### Scalability
**Challenge**: Processing large volumes of email data
**Solution**: Incremental processing and efficient storage
**Future**: Database storage for large-scale analysis

## Success Criteria

### Phase 1 Success
- [ ] Clear understanding of .eml file structure
- [ ] Well-designed ChatThread interface
- [ ] Initial prototype implementation
- [ ] Test framework established

### Phase 2 Success
- [ ] Basic .eml file parsing working
- [ ] ChatThread class fully implemented
- [ ] Simple markdown output generated
- [ ] Comprehensive test coverage

### Phase 3 Success
- [ ] LLM-optimized markdown output
- [ ] Integration with existing sales data
- [ ] Performance optimization completed
- [ ] Ready for GraphAPI integration

## Next Steps

1. **Immediate**: Begin .eml file analysis and interface design
2. **Short-term**: Implement core ChatThread functionality
3. **Medium-term**: Develop advanced features and integration
4. **Long-term**: GraphAPI integration and enterprise deployment

---

*Last Updated: December 2024*
*Project: Tool Experiments - Teams Message Processing* 