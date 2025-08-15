# tests/test_chat_thread_loader.py
import pytest
from pathlib import Path
from src.tool_experiments.chat_thread_loader import EmailChatThreadLoader
from src.tool_experiments.chat_thread import ChatThread, Message


class TestEmailChatThreadLoader:
    """Test cases for EmailChatThreadLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loader = EmailChatThreadLoader()
        self.raw_dir = Path("data/raw")
        self.july_dir = Path( "data/raw/July Messages")
    
    # Golden example of expected subjects (sorted alphabetically)
    EXPECTED_SUBJECTS = [
        'AUR/Foodworks resign',
        'Catchment Report and forecast.id Premium for Bacchus Marsh Grammar',
        'Community Views for City of Armadale in Perth',
        'Competitive RfQ win with South Australian Dept. of State Development',
        'Culture in Action - ur help pls',
        'Infrastructure WA looks to Community Views to make informed\n decisions!',
        'Livingstone Shire Council signs for 3 years of Community Views',
        'Not New Work but FYI - Cairns re-signs for FY26 (economy, profile,\n atlas) ',
        'Stonnington Views 2.0',
        'Western Sydney Uni (Centre for Western Sydney) adds Electoral\n Divisions',
        'Westpac',
        'Whitsunday Win',
        're-engaged by the NSW Night Time Commissioner',
    ]

    @pytest.mark.primary
    def test_load_threadList_subjects(self):
        """Test that load_threadList returns expected ChatThread objects with correct subjects."""
        threads = self.loader.load_threadList(str(self.raw_dir / "*.eml"))
        assert len(threads) == len(self.EXPECTED_SUBJECTS), f"Expected {len(self.EXPECTED_SUBJECTS)} threads, got {len(threads)}"
        actual_subjects = [thread.get_metadata()['subject'] for thread in threads]
        actual_subjects_sorted = sorted(actual_subjects)
        expected_subjects_sorted = sorted(self.EXPECTED_SUBJECTS)
        # Compare subjects, normalizing line breaks
        for actual, expected in zip(actual_subjects_sorted, expected_subjects_sorted):
            actual_normalized = actual.replace('\n', ' ').strip()
            expected_normalized = expected.replace('\n', ' ').strip()
            assert actual_normalized == expected_normalized, f"Subject mismatch: '{actual}' vs '{expected}'"
        # Verify all objects are ChatThread instances with expected methods
        for thread in threads:
            assert hasattr(thread, 'get_metadata')
            assert hasattr(thread, 'get_messages')
            assert hasattr(thread, 'get_participants')
    
    # ============================================================================
    # PRIMARY TESTS - Core Functional Behavior
    # ============================================================================
    
  


    @pytest.mark.primary
    @pytest.mark.parametrize("eml_file,expected_subject,expected_participants,expected_message_count", [
        (
            "Community Views for City of Armadale in Perth.eml",
            "Community Views for City of Armadale in Perth",
            ["Jacquie Norton"],
            1
        ),
        (
            "Whitsunday Win.eml",
            "Whitsunday Win",
            ["Greg Bowden", "Dan Evans", "Dieter Krusic-Golub", "Sally Blandy"],
            4
        ),
        (
            "Competitive RfQ win with South Australian Dept. of State Development.eml",
            "Competitive RfQ win with South Australian Dept. of State Development",
            ["Nenad Petrovic", "Christopher Jones", "Sally Blandy", "Rob Hall", "Daniel Corbett", "Natalie Field", "Penny Bloomberg", "Jacquie Norton"],
            9
        ),
        (
            "Westpac.eml",
            "Westpac",
            ["Paul Tardio", "Dan Evans", "Rob Hall", "Jennifer Knowles", "Chris Thomas"],
            5
        )
    ])
    def test_load_thread_from_eml_files(self, eml_file: str, expected_subject: str, expected_participants: list, expected_message_count: int):
        """Primary test: Demonstrates loading ChatThread from various .eml files."""
        file_path = self.raw_dir / eml_file
        
        # Load the thread
        thread = self.loader.load_thread(file_path)
        
        # Validate thread structure
        assert isinstance(thread, ChatThread)
        assert thread.get_metadata()['subject'] == expected_subject
        
        # Validate participants
        participants = thread.get_participants()
        assert len(participants) == len(expected_participants)
        for expected_participant in expected_participants:
            assert expected_participant in participants
        
        # Validate message count
        messages = thread.get_messages()
        assert len(messages) == expected_message_count
        
        # Validate message structure
        for message in messages:
            assert isinstance(message, Message)
            assert message.participant.strip()
            assert message.content.strip()
            assert message.timestamp
        
        # Validate thread summary
        summary = thread.get_thread_summary()
        assert summary['subject'] == expected_subject
        assert summary['participant_count'] == len(expected_participants)
        assert summary['message_count'] == expected_message_count
        assert summary['participants'] == participants
    
    # ============================================================================
    # COVERAGE TESTS - Email Parsing & Content Extraction
    # ============================================================================
    
    def test_parse_email_headers(self):
        """Coverage test: Email header extraction."""
        file_path = self.raw_dir / "Community Views for City of Armadale in Perth.eml"
        
        # Test private method through public interface
        thread = self.loader.load_thread(file_path)
        metadata = thread.get_metadata()
        
        assert 'subject' in metadata
        assert 'date' in metadata
        assert 'thread_topic' in metadata
        assert 'message_id' in metadata
        assert metadata['subject'] == "Community Views for City of Armadale in Perth"
        assert "Wed, 9 Jul 2025" in metadata['date']
    
    def test_extract_teams_content_detection(self):
        """Coverage test: Teams content detection."""
        file_path = self.raw_dir / "Whitsunday Win.eml"
        
        # This should work (contains Teams content)
        thread = self.loader.load_thread(file_path)
        assert len(thread.get_messages()) > 0
    
    def test_extract_messages_with_attachments(self):
        """Coverage test: Message extraction with attachment references."""
        file_path = self.raw_dir / "Whitsunday Win.eml"
        
        thread = self.loader.load_thread(file_path)
        messages = thread.get_messages()
        
        # Check that attachments are extracted
        attachment_count = 0
        for message in messages:
            if message.attachments:
                attachment_count += 1
                assert isinstance(message.attachments, list)
                for attachment_id in message.attachments:
                    assert attachment_id in thread.get_attachments()
        
        assert attachment_count > 0  # Should have some messages with attachments
    
    def test_message_content_cleaning(self):
        """Coverage test: Message content cleaning and normalization."""
        file_path = self.raw_dir / "Community Views for City of Armadale in Perth.eml"
        
        thread = self.loader.load_thread(file_path)
        messages = thread.get_messages()
        
        for message in messages:
            # Content should be cleaned (no [cid:] references)
            assert '[cid:' not in message.content
            # Content should not be empty
            assert message.content.strip()
            # Content should not have excessive whitespace
            assert '\n\n\n' not in message.content
    
    def test_attachment_metadata_extraction(self):
        """Coverage test: Attachment metadata extraction."""
        file_path = self.raw_dir / "Whitsunday Win.eml"
        
        thread = self.loader.load_thread(file_path)
        attachments = thread.get_attachments()
        
        assert len(attachments) > 0
        
        for attachment_id, attachment_data in attachments.items():
            assert 'filename' in attachment_data
            assert 'content_type' in attachment_data
            assert 'size' in attachment_data
            assert attachment_data['size'] > 0
    
    def test_participant_name_extraction(self):
        """Coverage test: Participant name extraction and cleaning."""
        file_path = self.raw_dir / "Competitive RfQ win with South Australian Dept. of State Development.eml"
        
        thread = self.loader.load_thread(file_path)
        participants = thread.get_participants()
        
        # Should extract multiple participants
        assert len(participants) > 1
        
        # Participant names should be clean
        for participant in participants:
            assert participant.strip()
            assert not participant.startswith('\n')
            assert not participant.endswith('\n')
    
    def test_timestamp_extraction(self):
        """Coverage test: Timestamp extraction from messages."""
        file_path = self.raw_dir / "Westpac.eml"
        
        thread = self.loader.load_thread(file_path)
        messages = thread.get_messages()
        
        for message in messages:
            assert message.timestamp
            assert 'days ago' in message.timestamp or message.timestamp == "unknown"
    
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    def test_file_not_found_error(self):
        """Coverage test: File not found error handling."""
        with pytest.raises(FileNotFoundError) as exc_info:
            self.loader.load_thread(Path("nonexistent_file.eml"))
        assert "Email file not found" in str(exc_info.value)
    
    def test_non_teams_email_error(self):
        """Coverage test: Non-Teams email error handling."""
        # Create a temporary non-Teams email file
        temp_file = Path("temp_non_teams.eml")
        try:
            temp_file.write_text("Subject: Test\n\nThis is not a Teams email.")
            
            with pytest.raises(ValueError) as exc_info:
                self.loader.load_thread(temp_file)
            assert "No Teams content found" in str(exc_info.value)
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    def test_malformed_email_handling(self):
        """Coverage test: Malformed email handling."""
        # Create a malformed email file
        temp_file = Path("temp_malformed.eml")
        try:
            temp_file.write_text("This is not a valid email format at all.")
            
            # Should handle gracefully (might raise ValueError or handle differently)
            try:
                thread = self.loader.load_thread(temp_file)
                # If it doesn't raise an error, it should return a thread with no messages
                assert len(thread.get_messages()) == 0
            except ValueError:
                # This is also acceptable behavior
                pass
        finally:
            if temp_file.exists():
                temp_file.unlink()
    
    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================
    
    def test_empty_message_content(self):
        """Coverage test: Handling of empty message content."""
        # This test ensures the loader handles edge cases gracefully
        # We'll test with a real file that might have minimal content
        file_path = self.raw_dir / "Community Views for City of Armadale in Perth.eml"
        
        thread = self.loader.load_thread(file_path)
        messages = thread.get_messages()
        
        # All messages should have content
        for message in messages:
            assert message.content.strip()
    
    def test_unicode_character_handling(self):
        """Coverage test: Unicode character handling in messages."""
        file_path = self.raw_dir / "Whitsunday Win.eml"
        
        thread = self.loader.load_thread(file_path)
        messages = thread.get_messages()
        
        # Should handle emojis and special characters gracefully
        for message in messages:
            # Content should be properly decoded
            assert isinstance(message.content, str)
            # Should not raise encoding errors when processed
    
    def test_large_email_file_handling(self):
        """Coverage test: Large email file handling."""
        # Test with the largest .eml file
        file_path = self.raw_dir / "Whitsunday Win.eml"  # 146KB file
        
        thread = self.loader.load_thread(file_path)
        
        # Should process successfully
        assert isinstance(thread, ChatThread)
        assert len(thread.get_messages()) > 0
    
    def test_multiple_attachment_references(self):
        """Coverage test: Multiple attachment references in single message."""
        file_path = self.raw_dir / "Whitsunday Win.eml"
        
        thread = self.loader.load_thread(file_path)
        messages = thread.get_messages()
        
        # Find messages with multiple attachments
        multi_attachment_messages = [msg for msg in messages if len(msg.attachments) > 1]
        
        if multi_attachment_messages:
            for message in multi_attachment_messages:
                assert len(message.attachments) > 1
                # All attachment IDs should be valid
                for attachment_id in message.attachments:
                    assert attachment_id in thread.get_attachments() 