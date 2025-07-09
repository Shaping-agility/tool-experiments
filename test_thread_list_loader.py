#!/usr/bin/env python3
"""Test the load_threadList method of EmailChatThreadLoader."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tool_experiments.chat_thread_loader import EmailChatThreadLoader

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

def test_load_threadList():
    """Test that load_threadList returns expected ChatThread objects with correct subjects."""
    loader = EmailChatThreadLoader()
    
    # Load all threads from the pattern
    threads = loader.load_threadList("data/raw/*.eml")
    
    # Verify we got the expected number of threads
    print(f"Loaded {len(threads)} threads")
    print(f"Expected {len(EXPECTED_SUBJECTS)} threads")
    
    assert len(threads) == len(EXPECTED_SUBJECTS), f"Expected {len(EXPECTED_SUBJECTS)} threads, got {len(threads)}"
    
    # Extract subjects from loaded threads
    actual_subjects = [thread.get_metadata()['subject'] for thread in threads]
    actual_subjects_sorted = sorted(actual_subjects)
    
    print("\nActual subjects (sorted):")
    for subject in actual_subjects_sorted:
        print(f"  '{subject}'")
    
    print("\nExpected subjects (sorted):")
    for subject in EXPECTED_SUBJECTS:
        print(f"  '{subject}'")
    
    # Verify subjects match (allowing for minor differences in line breaks)
    assert len(actual_subjects_sorted) == len(EXPECTED_SUBJECTS), "Subject count mismatch"
    
    # Compare subjects, normalizing line breaks
    for actual, expected in zip(actual_subjects_sorted, EXPECTED_SUBJECTS):
        actual_normalized = actual.replace('\n', ' ').strip()
        expected_normalized = expected.replace('\n', ' ').strip()
        assert actual_normalized == expected_normalized, f"Subject mismatch: '{actual}' vs '{expected}'"
    
    # Verify all objects are ChatThread instances with expected methods
    for thread in threads:
        assert hasattr(thread, 'get_metadata'), "Thread missing get_metadata method"
        assert hasattr(thread, 'get_messages'), "Thread missing get_messages method"
        assert hasattr(thread, 'get_participants'), "Thread missing get_participants method"
    
    print("\n✅ All tests passed!")
    print(f"Successfully loaded {len(threads)} ChatThread objects with matching subjects")

if __name__ == "__main__":
    test_load_threadList() 