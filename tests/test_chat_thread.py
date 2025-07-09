# tests/test_chat_thread.py
import pytest
from pathlib import Path
from src.tool_experiments.chat_thread import ChatThread, Message
from src.tool_experiments.chat_thread_loader import EmailChatThreadLoader


class TestChatThread:
    """Test cases for ChatThread class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = EmailChatThreadLoader()
        self.raw_dir = Path("data/raw")
        self.output_dir = Path("data/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Golden example from Whitsunday Win.eml markdown output
    WHITSUNDAY_WIN_GOLDEN = """# Whitsunday Win

**Date:** Wed, 9 Jul 2025 00:27:39 +0000
**Participants:** Greg Bowden, Dan Evans, Dieter Krusic-Golub, Sally Blandy
**Messages:** 4

---

### Message 1: Greg Bowden
**Time:** unknown

Whitsunday Win
A good start to the new FY 🥳

I have just received the signed 60K contract from Whitsunday Regional Council. Economy, profile & Atlas for 3 a Year Term.

WRC moved to REMPLAN 3 years ago so they were an early target for me when I started at id this year.

Keenan Jackson and I provided them with SOR data and me presenting with the Mayor in April at a council event. This coupled with a few past relationships has been key to our success.
This should now be a long term relationship if treated well.

Thanks to all involved. 💪

*Attachments: e2c34f6b-94d2-4934-8681-3caae78862d7*

---

### Message 2: Dan Evans
**Time:** unknown

Absolutely cracking effort here Greg Bowden. Congrats mate. Planted the seed (palm tree) and now bearing the fruit. Unlocks Mackay as well. [🤠]

*Attachments: dd2b1a48-e61e-4282-8eab-1862e67be993*

---

### Message 3: Dieter Krusic-Golub
**Time:** unknown

Fab win GB [🍾]  all the sweeter against the other lot too [💯]

*Attachments: 91ce75b1-1f61-4377-a3b2-de7115d09b71*

---

### Message 4: Sally Blandy
**Time:** unknown

Well done Greg, Keenan and team!

To go with our revenue thermometer I feel we need a map of all LGAs coloured by provider. When we win one we get to colour it orange. So sweet to take one back from Remplan

---"""

    # ============================================================================
    # PRIMARY TESTS - Core Functional Behavior
    # ============================================================================
    
    @pytest.mark.primary
    def test_to_markdown_whitsunday_win_golden(self):
        """Primary test: Verify to_markdown() produces expected output for Whitsunday Win."""
        file_path = self.raw_dir / "Whitsunday Win.eml"
        thread = self.loader.load_thread(file_path)

        actual_markdown = thread.to_markdown()
        # Normalize line endings for robust comparison
        actual_norm = actual_markdown.replace('\r\n', '\n').strip()
        golden_norm = self.WHITSUNDAY_WIN_GOLDEN.replace('\r\n', '\n').strip()
        assert actual_norm == golden_norm, "Markdown output doesn't match golden example"
    
    @pytest.mark.primary
    def test_output_all_threads_to_file(self):
        """Primary test: Load all .eml files and output to all_threads.md."""
        threads = self.loader.load_threadList(str(self.raw_dir / "*.eml"))
        output_file = self.output_dir / "all_threads.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, thread in enumerate(threads):
                if i > 0:
                    f.write("\n\n---\n\n")
                f.write(thread.to_markdown())
        
        # Verify file was created and has content
        assert output_file.exists(), "Output file was not created"
        assert output_file.stat().st_size > 0, "Output file is empty"
        print(f"✓ Successfully wrote {len(threads)} threads to {output_file}")
    
    # ============================================================================
    # COVERAGE TESTS - ChatThread Core Functionality
    # ============================================================================
    
    def test_chat_thread_initialization(self):
        """Coverage test: ChatThread initialization with metadata."""
        thread = ChatThread(
            subject="Test Subject",
            date="2025-01-01",
            thread_topic="Test Topic",
            message_id="test-123"
        )
        
        metadata = thread.get_metadata()
        assert metadata['subject'] == "Test Subject"
        assert metadata['date'] == "2025-01-01"
        assert metadata['thread_topic'] == "Test Topic"
        assert metadata['message_id'] == "test-123"
    
    def test_add_and_get_messages(self):
        """Coverage test: Adding and retrieving messages."""
        thread = ChatThread("Test", "2025-01-01")
        
        # Add messages
        msg1 = Message("Alice", "2 days ago", "Hello there")
        msg2 = Message("Bob", "1 day ago", "Hi Alice")
        
        thread.add_message(msg1)
        thread.add_message(msg2)
        
        messages = thread.get_messages()
        assert len(messages) == 2
        assert messages[0].participant == "Alice"
        assert messages[1].participant == "Bob"
    
    def test_get_participants(self):
        """Coverage test: Participant extraction and deduplication."""
        thread = ChatThread("Test", "2025-01-01")
        
        # Add messages from different participants
        thread.add_message(Message("Alice", "2 days ago", "Hello"))
        thread.add_message(Message("Bob", "1 day ago", "Hi"))
        thread.add_message(Message("Alice", "1 day ago", "How are you?"))  # Duplicate
        
        participants = thread.get_participants()
        assert len(participants) == 2
        assert "Alice" in participants
        assert "Bob" in participants
    
    def test_add_and_get_attachments(self):
        """Coverage test: Adding and retrieving attachment metadata."""
        thread = ChatThread("Test", "2025-01-01")
        
        attachment_data = {
            'filename': 'test.pdf',
            'content_type': 'application/pdf',
            'size': 1024
        }
        
        thread.add_attachment("att-123", attachment_data)
        
        attachments = thread.get_attachments()
        assert "att-123" in attachments
        assert attachments["att-123"]["filename"] == "test.pdf"
        assert attachments["att-123"]["size"] == 1024
    
    def test_get_thread_summary(self):
        """Coverage test: Thread summary generation."""
        thread = ChatThread("Test Subject", "2025-01-01", "Test Topic", "msg-123")
        
        # Add messages and attachments
        thread.add_message(Message("Alice", "2 days ago", "Hello"))
        thread.add_message(Message("Bob", "1 day ago", "Hi"))
        thread.add_attachment("att-1", {'filename': 'test.pdf', 'content_type': 'pdf', 'size': 100})
        
        summary = thread.get_thread_summary()
        
        assert summary['subject'] == "Test Subject"
        assert summary['date'] == "2025-01-01"
        assert summary['thread_topic'] == "Test Topic"
        assert summary['message_id'] == "msg-123"
        assert summary['participant_count'] == 2
        assert summary['message_count'] == 2
        assert summary['attachment_count'] == 1
        assert len(summary['participants']) == 2
        assert "Hello" in summary['first_message']
        assert "Hi" in summary['last_message']
    
    def test_to_markdown_empty_thread(self):
        """Coverage test: Markdown generation for empty thread."""
        thread = ChatThread("Empty Thread", "2025-01-01")
        
        markdown = thread.to_markdown()
        
        assert "# Empty Thread" in markdown
        assert "**Date:** 2025-01-01" in markdown
        assert "**Participants:**" in markdown
        assert "**Messages:** 0" in markdown
    
    def test_to_markdown_with_attachments(self):
        """Coverage test: Markdown generation includes attachment references."""
        thread = ChatThread("Test", "2025-01-01")
        
        # Add message with attachments
        msg = Message("Alice", "2 days ago", "Check this out", ["att-1", "att-2"])
        thread.add_message(msg)
        
        markdown = thread.to_markdown()
        
        assert "*Attachments: att-1, att-2*" in markdown
    
    # ============================================================================
    # COVERAGE TESTS - Message Class
    # ============================================================================
    
    def test_message_initialization(self):
        """Coverage test: Message initialization and validation."""
        msg = Message("Alice", "2 days ago", "Hello world", ["att-1"])
        
        assert msg.participant == "Alice"
        assert msg.timestamp == "2 days ago"
        assert msg.content == "Hello world"
        assert msg.attachments == ["att-1"]
    
    def test_message_validation_empty_participant(self):
        """Coverage test: Message validation - empty participant."""
        with pytest.raises(ValueError, match="Message participant cannot be empty"):
            Message("", "2 days ago", "Hello")
    
    def test_message_validation_empty_content(self):
        """Coverage test: Message validation - empty content."""
        with pytest.raises(ValueError, match="Message content cannot be empty"):
            Message("Alice", "2 days ago", "")
    
    def test_message_default_attachments(self):
        """Coverage test: Message default attachments list."""
        msg = Message("Alice", "2 days ago", "Hello")
        assert msg.attachments == []
    
    # ============================================================================
    # INTEGRATION TESTS - Real Data Processing
    # ============================================================================
    
    def test_real_thread_processing(self):
        """Integration test: Process real .eml file and verify structure."""
        file_path = self.raw_dir / "Westpac.eml"
        thread = self.loader.load_thread(file_path)
        
        # Verify basic structure
        assert isinstance(thread, ChatThread)
        assert thread.get_metadata()['subject'] == "Westpac"
        
        # Verify messages
        messages = thread.get_messages()
        assert len(messages) > 0
        
        for message in messages:
            assert isinstance(message, Message)
            assert message.participant.strip()
            assert message.content.strip()
        
        # Verify participants
        participants = thread.get_participants()
        assert len(participants) > 0
        
        # Verify markdown generation
        markdown = thread.to_markdown()
        assert "# Westpac" in markdown
        assert "**Participants:**" in markdown
        assert "**Messages:**" in markdown
    
    def test_multiple_threads_consistency(self):
        """Integration test: Verify consistency across multiple threads."""
        threads = self.loader.load_threadList(str(self.raw_dir / "*.eml"))
        
        for thread in threads:
            # Each thread should have valid metadata
            metadata = thread.get_metadata()
            assert metadata['subject']
            assert metadata['date']
            
            # Each thread should have messages
            messages = thread.get_messages()
            assert len(messages) > 0
            
            # Each message should have valid content
            for message in messages:
                assert message.participant.strip()
                assert message.content.strip()
            
            # Markdown should be generated without error
            markdown = thread.to_markdown()
            assert markdown.strip() 