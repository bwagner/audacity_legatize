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

import argparse
import fileinput
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
    parser = argparse.ArgumentParser(
        description='Convert Audacity labels to legato (continuous) format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s                           # Read from stdin, write to stdout
  %(prog)s input.txt                 # Read from file, write to stdout
  %(prog)s input.txt output.txt      # Read from file, write to file
  %(prog)s -i input.txt              # Modify input.txt in place"""
    )

    parser.add_argument('-i', '--in-place', action='store_true',
                        help='Edit input file in place')
    parser.add_argument('input_file', nargs='?',
                        help='Input file (default: stdin)')
    parser.add_argument('output_file', nargs='?',
                        help='Output file (default: stdout)')

    args = parser.parse_args()

    # Validate arguments
    if args.in_place:
        if not args.input_file:
            parser.error("-i/--in-place requires an input file (cannot use stdin)")
        if args.output_file:
            parser.error("-i/--in-place cannot be used with an output file")

    # First pass: read all labels (we need lookahead for legato conversion)
    labels = []
    input_files = (args.input_file,) if args.input_file else ('-',)

    with fileinput.input(files=input_files) as f:
        for line in f:
            parsed = parse_label_line(line)
            if parsed:
                labels.append(parsed)

    # Convert to legato
    legato_labels = legatize_labels(labels)

    # Output
    if args.output_file:
        # Write to specified output file
        with open(args.output_file, 'w') as f:
            for label in legato_labels:
                f.write(format_label(*label) + '\n')
    elif args.in_place:
        # Write back to input file using fileinput's in-place mode
        with fileinput.input(files=(args.input_file,), inplace=True) as f:
            output_written = False
            for line in f:
                if not output_written:
                    # Write all our output on encountering the first line
                    for label in legato_labels:
                        print(format_label(*label))
                    output_written = True
                # Skip all original lines
    else:
        # Write to stdout
        for label in legato_labels:
            print(format_label(*label))

if __name__ == "__main__":
    main()
