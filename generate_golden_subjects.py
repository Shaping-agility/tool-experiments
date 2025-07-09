#!/usr/bin/env python3
"""Generate golden example of expected subjects from all .eml files."""

from pathlib import Path
import email

def extract_subject_from_eml(file_path: Path) -> str:
    """Extract subject from .eml file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        msg = email.message_from_string(content)
        return msg.get('Subject', '')
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def main():
    """Generate golden example of subjects."""
    raw_dir = Path("data/raw")
    eml_files = list(raw_dir.glob("*.eml"))
    
    print("Found .eml files:")
    subjects = []
    
    for eml_file in sorted(eml_files):
        subject = extract_subject_from_eml(eml_file)
        subjects.append(subject)
        print(f"  {eml_file.name}: {subject}")
    
    print(f"\nTotal files: {len(subjects)}")
    print("\nGolden example (sorted):")
    print("EXPECTED_SUBJECTS = [")
    for subject in sorted(subjects):
        print(f"    '{subject}',")
    print("]")

if __name__ == "__main__":
    main() 