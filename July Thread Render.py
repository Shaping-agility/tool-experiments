#!/usr/bin/env python3
"""Render all July message threads to markdown for inspection."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tool_experiments.chat_thread_loader import EmailChatThreadLoader

def main():
    """Load all July message threads and render to markdown."""
    loader = EmailChatThreadLoader()
    
    # Define input and output paths
    july_messages_dir = Path("data/raw/july work done messages")
    output_file = Path("data/output/July Work Done.md")
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if july messages directory exists
    if not july_messages_dir.exists():
        print(f"✗ Directory not found: {july_messages_dir}")
        return
    
    # Get all .eml files in the july messages directory
    eml_files = list(july_messages_dir.glob("*.eml"))
    
    if not eml_files:
        print(f"✗ No .eml files found in {july_messages_dir}")
        return
    
    print(f"Found {len(eml_files)} .eml files in {july_messages_dir}")
    
    # Sort files for consistent output
    eml_files.sort()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# July Messages - All Threads\n\n")
        f.write(f"**Source Directory:** {july_messages_dir}\n")
        f.write(f"**Total Threads:** {len(eml_files)}\n\n")
        f.write("---\n\n")
        
        for i, eml_file in enumerate(eml_files, 1):
            try:
                print(f"Loading {eml_file.name}... ({i}/{len(eml_files)})")
                
                thread = loader.load_thread(eml_file)
                markdown = thread.to_markdown()
                
                f.write(f"## Thread {i}: {eml_file.name}\n\n")
                f.write(markdown)
                f.write("\n\n---\n\n")
                
                print(f"✓ Rendered {eml_file.name}")
                
            except Exception as e:
                print(f"✗ Error loading {eml_file.name}: {e}")
                f.write(f"## Thread {i}: {eml_file.name}\n\n")
                f.write(f"**Error loading file:** {e}\n\n")
                f.write("---\n\n")
    
    print(f"\n✅ Successfully processed {len(eml_files)} threads")
    print(f"Output written to: {output_file}")

if __name__ == "__main__":
    main()
