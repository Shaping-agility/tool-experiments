#!/usr/bin/env python3
"""Render sample threads to markdown for inspection."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tool_experiments.chat_thread_loader import EmailChatThreadLoader

def main():
    """Load sample threads and render to markdown."""
    loader = EmailChatThreadLoader()
    output_file = Path("data/output/sample_thread.md")
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Sample files to render
    sample_files = [
        "Whitsunday Win.eml",
        "Westpac.eml"
    ]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Sample Thread Renderings\n\n")
        
        for eml_file in sample_files:
            try:
                file_path = Path("data/raw") / eml_file
                print(f"Loading {eml_file}...")
                
                thread = loader.load_thread(file_path)
                markdown = thread.to_markdown()
                
                f.write(f"## {eml_file}\n\n")
                f.write(markdown)
                f.write("\n\n---\n\n")
                
                print(f"✓ Rendered {eml_file}")
                
            except Exception as e:
                print(f"✗ Error loading {eml_file}: {e}")
                f.write(f"## {eml_file}\n\n")
                f.write(f"**Error loading file:** {e}\n\n")
                f.write("---\n\n")
    
    print(f"\nOutput written to: {output_file}")

if __name__ == "__main__":
    main() 