#!/usr/bin/env python3
"""
Analyze .eml files to understand Teams message structure for ChatThread interface design.
"""

import base64
import re
import email
from pathlib import Path
from typing import Dict, List, Any
import json

def analyze_eml_file(file_path: Path) -> Dict[str, Any]:
    """Analyze a single .eml file and extract its structure."""
    
    print(f"\n{'='*80}")
    print(f"Analyzing: {file_path.name}")
    print(f"{'='*80}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Parse with email module
    msg = email.message_from_string(content)
    
    # Extract email headers
    headers = {
        'subject': msg.get('Subject', ''),
        'from': msg.get('From', ''),
        'to': msg.get('To', ''),
        'date': msg.get('Date', ''),
        'message_id': msg.get('Message-ID', ''),
        'thread_topic': msg.get('Thread-Topic', ''),
        'thread_index': msg.get('Thread-Index', ''),
    }
    
    print(f"Email Headers:")
    for key, value in headers.items():
        print(f"  {key}: {value}")
    
    # Find all text/plain parts
    plain_parts = []
    html_parts = []
    
    def extract_parts(part, parts_list, content_type):
        if part.get_content_type() == content_type:
            payload = part.get_payload(decode=True)
            if payload:
                try:
                    decoded = payload.decode('utf-8', errors='ignore')
                    parts_list.append(decoded)
                except UnicodeDecodeError:
                    try:
                        decoded = payload.decode('iso-8859-1', errors='ignore')
                        parts_list.append(decoded)
                    except:
                        parts_list.append(str(payload))
        elif part.is_multipart():
            for subpart in part.get_payload():
                extract_parts(subpart, parts_list, content_type)
    
    extract_parts(msg, plain_parts, 'text/plain')
    extract_parts(msg, html_parts, 'text/html')
    
    print(f"\nFound {len(plain_parts)} text/plain parts")
    print(f"Found {len(html_parts)} text/html parts")
    
    # Analyze the first plain text part (main content)
    if plain_parts:
        main_content = plain_parts[0]
        print(f"\nMain Content Preview (first 500 chars):")
        print(f"{'='*50}")
        print(main_content[:500])
        print(f"{'='*50}")
        
        # Look for Teams message patterns
        teams_patterns = {
            'microsoft_teams_header': 'Microsoft Teams' in main_content,
            'participant_patterns': re.findall(r'([A-Za-z\s]+)\s+\d+\s+days?\s+ago', main_content),
            'message_content': re.findall(r'([A-Za-z\s]+)\s+\d+\s+days?\s+ago\s*\n(.*?)(?=\n[A-Za-z\s]+\s+\d+\s+days?\s+ago|\nGo to Teams|$)', main_content, re.DOTALL),
            'teams_link': 'Go to Teams' in main_content,
            'attachments': re.findall(r'\[cid:([^\]]+)\]', main_content),
        }
        
        print(f"\nTeams Message Analysis:")
        print(f"  Microsoft Teams header found: {teams_patterns['microsoft_teams_header']}")
        print(f"  Participants found: {teams_patterns['participant_patterns']}")
        print(f"  Teams link found: {teams_patterns['teams_link']}")
        print(f"  Attachments found: {teams_patterns['attachments']}")
        
        if teams_patterns['message_content']:
            print(f"\nExtracted Messages:")
            for i, (participant, content) in enumerate(teams_patterns['message_content']):
                print(f"  Message {i+1}:")
                print(f"    Participant: {participant.strip()}")
                print(f"    Content: {content.strip()[:200]}...")
                print()
    
    # Look for attachments
    attachments = []
    for part in msg.walk():
        if part.get_filename():
            attachments.append({
                'filename': part.get_filename(),
                'content_type': part.get_content_type(),
                'content_id': part.get('Content-ID', ''),
                'size': len(part.get_payload(decode=True)) if part.get_payload(decode=True) else 0
            })
    
    print(f"\nAttachments:")
    for attachment in attachments:
        print(f"  {attachment['filename']} ({attachment['content_type']}) - {attachment['size']} bytes")
    
    return {
        'headers': headers,
        'plain_parts_count': len(plain_parts),
        'html_parts_count': len(html_parts),
        'attachments': attachments,
        'main_content_preview': plain_parts[0][:500] if plain_parts else '',
        'teams_patterns': teams_patterns if plain_parts else {}
    }

def main():
    """Analyze all .eml files in the data/raw directory."""
    
    raw_dir = Path("data/raw")
    eml_files = list(raw_dir.glob("*.eml"))
    
    print(f"Found {len(eml_files)} .eml files to analyze")
    
    results = {}
    
    for eml_file in eml_files:
        try:
            results[eml_file.name] = analyze_eml_file(eml_file)
        except Exception as e:
            print(f"Error analyzing {eml_file.name}: {e}")
    
    # Summary analysis
    print(f"\n{'='*80}")
    print(f"SUMMARY ANALYSIS")
    print(f"{'='*80}")
    
    teams_files = 0
    total_messages = 0
    total_participants = set()
    total_attachments = 0
    
    for filename, result in results.items():
        if result['teams_patterns'].get('microsoft_teams_header'):
            teams_files += 1
            total_messages += len(result['teams_patterns'].get('message_content', []))
            total_participants.update(result['teams_patterns'].get('participant_patterns', []))
            total_attachments += len(result['attachments'])
    
    print(f"Files containing Teams messages: {teams_files}/{len(results)}")
    print(f"Total messages across all files: {total_messages}")
    print(f"Unique participants: {len(total_participants)}")
    print(f"Total attachments: {total_attachments}")
    
    print(f"\nUnique participants found:")
    for participant in sorted(total_participants):
        print(f"  - {participant}")
    
    # Save detailed results
    with open('eml_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to eml_analysis_results.json")

if __name__ == "__main__":
    main() 