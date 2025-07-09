#!/usr/bin/env python3
"""Debug script to test ChatThreadLoader with a single file."""

from pathlib import Path
from src.tool_experiments.chat_thread_loader import EmailChatThreadLoader

def test_single_file():
    """Test loading a single .eml file."""
    print("Starting debug test...")
    
    # Initialize loader
    loader = EmailChatThreadLoader()
    
    # Test with a simple file
    file_path = Path("data/raw/Community Views for City of Armadale in Perth.eml")
    
    print(f"Testing file: {file_path}")
    print(f"File exists: {file_path.exists()}")
    
    if file_path.exists():
        try:
            # Load the thread
            thread = loader.load_thread(file_path)
            
            print("✓ Thread loaded successfully")
            print(f"Subject: {thread.get_metadata()['subject']}")
            print(f"Participants: {thread.get_participants()}")
            print(f"Message count: {len(thread.get_messages())}")
            
            # Test markdown generation
            markdown = thread.to_markdown()
            print(f"Markdown length: {len(markdown)} characters")
            print("✓ All basic functionality working")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("✗ File not found")

if __name__ == "__main__":
    test_single_file() 