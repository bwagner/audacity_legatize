#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
# ]
# ///
"""
audacity_legatize.py: makes audacity labels legato, i.e. turns:
t1  t1  l1
t2  t2  l2
t3  t3
t4
t5
into:
t1  t2  l1
t2  t3  l2
t3  t4
t4  t5
t5
"""

import sys
from typing import List, Tuple, Optional

def parse_label_line(line: str) -> Tuple[float, float, Optional[str]]:
    """Parse a single Audacity label line."""
    parts = line.strip().split('\t')
    if not parts or not parts[0]:
        return None
    
    try:
        if len(parts) == 1:
            # Just a time point
            return (float(parts[0]), float(parts[0]), None)
        elif len(parts) == 2:
            # Start and end time, no label
            return (float(parts[0]), float(parts[1]), None)
        else:
            # Start, end, and label
            return (float(parts[0]), float(parts[1]), '\t'.join(parts[2:]))
    except ValueError:
        return None

def legatize_labels(labels: List[Tuple[float, float, Optional[str]]]) -> List[Tuple[float, float, Optional[str]]]:
    """Convert point labels to legato (continuous) labels."""
    if not labels:
        return []
    
    result = []
    for i in range(len(labels)):
        start_time = labels[i][0]
        label_text = labels[i][2]
        
        # Extend to the start of the next label, or keep the same time for the last one
        if i < len(labels) - 1:
            end_time = labels[i + 1][0]
        else:
            # For the last label, check if it already has a different end time
            # If it's a point label (start == end), keep it as is
            end_time = labels[i][1] if labels[i][0] != labels[i][1] else labels[i][0]
        
        result.append((start_time, end_time, label_text))
    
    return result

def format_label(start: float, end: float, text: Optional[str]) -> str:
    """Format a label for output."""
    if text is not None:
        return f"{start}\t{end}\t{text}"
    elif start != end:
        return f"{start}\t{end}"
    else:
        return f"{start}"

def main():
    labels = []
    
    # Read from stdin
    for line in sys.stdin:
        parsed = parse_label_line(line)
        if parsed:
            labels.append(parsed)
    
    # Convert to legato
    legato_labels = legatize_labels(labels)
    
    # Output
    for label in legato_labels:
        print(format_label(*label))

if __name__ == "__main__":
    main()
