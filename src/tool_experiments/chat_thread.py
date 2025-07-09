from dataclasses import dataclass, field
from typing import List, Dict, Any
from pathlib import Path


@dataclass
class Message:
    """Represents a single message within a Teams thread."""
    
    participant: str
    timestamp: str  # "X days ago" format from Teams
    content: str
    attachments: List[str] = field(default_factory=list)  # List of attachment IDs
    
    def __post_init__(self):
        """Validate message data after initialization."""
        if not self.participant or not self.participant.strip():
            raise ValueError("Message participant cannot be empty")
        if not self.content or not self.content.strip():
            raise ValueError("Message content cannot be empty")


class ChatThread:
    """Represents a single Teams conversation thread."""
    
    def __init__(self, subject: str, date: str, thread_topic: str = "", message_id: str = ""):
        """Initialize a ChatThread with basic metadata.
        
        Args:
            subject: Thread subject/title
            date: Thread date
            thread_topic: Teams thread topic (optional)
            message_id: Email message ID (optional)
        """
        self._subject = subject
        self._date = date
        self._thread_topic = thread_topic
        self._message_id = message_id
        self._messages: List[Message] = []
        self._attachments: Dict[str, Dict[str, Any]] = {}
    
    def add_message(self, message: Message) -> None:
        """Add a message to the thread.
        
        Args:
            message: Message object to add
        """
        self._messages.append(message)
    
    def add_attachment(self, attachment_id: str, attachment_data: Dict[str, Any]) -> None:
        """Add attachment metadata to the thread.
        
        Args:
            attachment_id: Unique identifier for the attachment
            attachment_data: Dictionary containing attachment metadata
        """
        self._attachments[attachment_id] = attachment_data
    
    def get_messages(self) -> List[Message]:
        """Get all messages in the thread.
        
        Returns:
            List of Message objects in chronological order
        """
        return self._messages.copy()
    
    def get_participants(self) -> List[str]:
        """Get all unique participants in the thread.
        
        Returns:
            List of unique participant names
        """
        return list(set(msg.participant for msg in self._messages))
    
    def get_thread_summary(self) -> Dict[str, Any]:
        """Get structured summary of the thread.
        
        Returns:
            Dictionary containing thread metadata and statistics
        """
        return {
            'subject': self._subject,
            'date': self._date,
            'thread_topic': self._thread_topic,
            'message_id': self._message_id,
            'participant_count': len(self.get_participants()),
            'message_count': len(self._messages),
            'attachment_count': len(self._attachments),
            'participants': self.get_participants(),
            'first_message': self._messages[0].content[:200] + "..." if self._messages else "",
            'last_message': self._messages[-1].content[:200] + "..." if self._messages else ""
        }
    
    def to_markdown(self) -> str:
        """Render thread as LLM-friendly markdown.
        
        Returns:
            Formatted markdown string representing the thread
        """
        markdown = f"# {self._subject}\n\n"
        markdown += f"**Date:** {self._date}\n"
        markdown += f"**Participants:** {', '.join(self.get_participants())}\n"
        markdown += f"**Messages:** {len(self._messages)}\n\n"
        markdown += "---\n\n"
        
        for i, message in enumerate(self._messages, 1):
            markdown += f"### Message {i}: {message.participant}\n"
            markdown += f"**Time:** {message.timestamp}\n\n"
            markdown += f"{message.content}\n\n"
            if message.attachments:
                markdown += f"*Attachments: {', '.join(message.attachments)}*\n\n"
            markdown += "---\n\n"
        
        return markdown
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get thread metadata.
        
        Returns:
            Dictionary containing thread metadata
        """
        return {
            'subject': self._subject,
            'date': self._date,
            'thread_topic': self._thread_topic,
            'message_id': self._message_id
        }
    
    def get_attachments(self) -> Dict[str, Dict[str, Any]]:
        """Get attachment metadata.
        
        Returns:
            Dictionary mapping attachment IDs to metadata
        """
        return self._attachments.copy() 