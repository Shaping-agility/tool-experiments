from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
import email
import re
from .chat_thread import ChatThread, Message


class ChatThreadLoader(ABC):
    """Abstract base class for loading ChatThread objects from various sources."""
    
    @abstractmethod
    def load_thread(self, source_path: Path) -> ChatThread:
        """Load a ChatThread from the specified source.
        
        Args:
            source_path: Path to the source file
            
        Returns:
            Populated ChatThread object
            
        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If source file cannot be parsed
        """
        pass


class EmailChatThreadLoader(ChatThreadLoader):
    """Concrete implementation for loading ChatThread objects from .eml files.
    
    Note: This loader is responsible only for parsing and populating ChatThread and Message objects.
    It does NOT handle any markdown generation or formatting. That is the responsibility of ChatThread.
    """
    
    def load_thread(self, source_path: Path) -> ChatThread:
        """Load a ChatThread from an .eml file.
        
        Args:
            source_path: Path to the .eml file
            
        Returns:
            Populated ChatThread object
            
        Raises:
            FileNotFoundError: If .eml file doesn't exist
            ValueError: If .eml file cannot be parsed or doesn't contain Teams content
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Email file not found: {source_path}")
        
        # Parse the email
        email_data = self._parse_email_file(source_path)
        
        # Extract Teams content
        teams_content = self._extract_teams_content(email_data)
        if not teams_content:
            raise ValueError(f"No Teams content found in email: {source_path}")
        
        # Create ChatThread with metadata
        thread = ChatThread(
            subject=email_data['headers']['subject'],
            date=email_data['headers']['date'],
            thread_topic=email_data['headers']['thread_topic'],
            message_id=email_data['headers']['message_id']
        )
        
        # Add messages to thread (skip empty-content messages)
        for message_data in teams_content['messages']:
            content_clean = message_data['content']
            if not content_clean.strip():
                continue  # Skip messages with empty content
            message = Message(
                participant=message_data['participant'],
                timestamp=message_data['timestamp'],
                content=content_clean,
                attachments=message_data['attachments']
            )
            thread.add_message(message)
        
        # Add attachments to thread
        for attachment_id, attachment_data in teams_content['attachments'].items():
            thread.add_attachment(attachment_id, attachment_data)
        
        return thread
    
    def load_threadList(self, file_pattern: str) -> List[ChatThread]:
        """Load multiple ChatThread objects from files matching the pattern.
        
        Args:
            file_pattern: Glob pattern for .eml files (e.g., 'data/raw/*.eml')
            
        Returns:
            List of ChatThread objects, one for each matching .eml file
            
        Raises:
            ValueError: If no files match the pattern or if files cannot be parsed
        """
        pattern_path = Path(file_pattern)
        eml_files = list(pattern_path.parent.glob(pattern_path.name))
        
        if not eml_files:
            raise ValueError(f"No .eml files found matching pattern: {file_pattern}")
        
        threads = []
        for eml_file in sorted(eml_files):
            try:
                thread = self.load_thread(eml_file)
                threads.append(thread)
            except Exception as e:
                print(f"Warning: Could not load {eml_file}: {e}")
                continue
        
        return threads
    
    def _parse_email_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse .eml file and extract basic structure.
        
        Args:
            file_path: Path to the .eml file
            
        Returns:
            Dictionary containing email headers and content
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Parse with email module
        msg = email.message_from_string(content)
        
        # Extract headers
        headers = {
            'subject': msg.get('Subject', ''),
            'date': msg.get('Date', ''),
            'thread_topic': msg.get('Thread-Topic', ''),
            'message_id': msg.get('Message-ID', ''),
        }
        
        # Extract text content
        plain_content = self._extract_text_content(msg)
        
        # Extract attachments
        attachments = self._extract_attachments(msg)
        
        return {
            'headers': headers,
            'plain_content': plain_content,
            'attachments': attachments
        }
    
    def _extract_text_content(self, msg) -> str:
        """Extract plain text content from email message.
        
        Args:
            msg: Parsed email message
            
        Returns:
            Plain text content
        """
        content_parts = []
        
        def extract_parts(part):
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    try:
                        decoded = payload.decode('utf-8', errors='ignore')
                        content_parts.append(decoded)
                    except UnicodeDecodeError:
                        try:
                            decoded = payload.decode('iso-8859-1', errors='ignore')
                            content_parts.append(decoded)
                        except:
                            content_parts.append(str(payload))
            elif part.is_multipart():
                for subpart in part.get_payload():
                    extract_parts(subpart)
        
        extract_parts(msg)
        return '\n'.join(content_parts) if content_parts else ""
    
    def _extract_attachments(self, msg) -> Dict[str, Dict[str, Any]]:
        """Extract attachment metadata from email message.
        
        Args:
            msg: Parsed email message
            
        Returns:
            Dictionary mapping attachment IDs to metadata
        """
        attachments = {}
        
        for part in msg.walk():
            if part.get_filename():
                attachment_id = part.get('Content-ID', '').strip('<>')
                if attachment_id:
                    payload = part.get_payload(decode=True)
                    attachments[attachment_id] = {
                        'filename': part.get_filename(),
                        'content_type': part.get_content_type(),
                        'size': len(payload) if payload else 0
                    }
        
        return attachments
    
    def _extract_teams_content(self, email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract Teams-specific content from email data.
        
        Args:
            email_data: Parsed email data
            
        Returns:
            Dictionary containing Teams messages and attachments, or None if no Teams content
        """
        content = email_data['plain_content']
        
        # Check if this is a Teams email
        if 'Microsoft Teams' not in content:
            return None
        
        # Extract messages using regex patterns
        messages = self._extract_messages(content)
        
        # Extract attachment references
        attachment_refs = self._extract_attachment_references(content)
        
        # Filter attachments to only those referenced in content
        referenced_attachments = {
            ref: email_data['attachments'].get(ref, {})
            for ref in attachment_refs
            if ref in email_data['attachments']
        }
        
        return {
            'messages': messages,
            'attachments': referenced_attachments
        }
    
    def _extract_messages(self, content: str) -> List[Dict[str, Any]]:
        """Extract individual messages from Teams content.
        
        Args:
            content: Plain text content from email
            
        Returns:
            List of message dictionaries
        """
        messages = []
        
        # Pattern to match Teams message format
        # Matches: "Name    X days ago\nMessage content"
        # Updated to handle names with hyphens and other characters
        message_pattern = r'([A-Za-z\s\-]+)\s+\d+\s+days?\s+ago\s*\n(.*?)(?=\n[A-Za-z\s\-]+\s+\d+\s+days?\s+ago|\nGo to Teams|$)'
        
        matches = re.findall(message_pattern, content, re.DOTALL)
        
        for participant, message_content in matches:
            # Clean participant name
            participant = participant.strip()
            
            # Clean message content
            content_clean = self._clean_message_content(message_content)
            
            # Extract attachment references
            attachments = self._extract_attachment_references(message_content)
            
            # Extract timestamp
            timestamp_match = re.search(r'(\d+\s+days?\s+ago)', message_content)
            timestamp = timestamp_match.group(1) if timestamp_match else "unknown"
            
            messages.append({
                'participant': participant,
                'timestamp': timestamp,
                'content': content_clean,
                'attachments': attachments
            })
        
        return messages
    
    def _clean_message_content(self, content: str) -> str:
        """Clean and normalize message content.
        
        Args:
            content: Raw message content
            
        Returns:
            Cleaned message content
        """
        # Remove attachment references
        content = re.sub(r'\[cid:[^\]]+\]', '', content)
        
        # Remove extra whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Strip leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def _extract_attachment_references(self, content: str) -> List[str]:
        """Extract attachment references from content.
        
        Args:
            content: Text content to search
            
        Returns:
            List of attachment IDs
        """
        # Pattern to match [cid:attachment_id] references
        pattern = r'\[cid:([^\]]+)\]'
        matches = re.findall(pattern, content)
        return matches 