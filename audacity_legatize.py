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

The trailing t5 is a sentinel: its only purpose in the input was to supply an
end time for the label before it, so by default it is dropped from the output.
Pass --keep-sentinel to emit it as a bare point label instead.

A sentinel is the last label when its start equals its end. A trailing range
label is a real label and is never dropped, and a lone label is never dropped.
If the sentinel carries text, that text is appended to the preceding label:

t1  t1  l1
t2  t2  end
becomes:
t1  t2  l1 end
"""

import argparse
import fileinput
from typing import List, Tuple, Optional

# Joins a sentinel's text onto the preceding label's text when the sentinel is
# dropped. A space keeps the result a single Audacity label field.
SENTINEL_TEXT_SEPARATOR = ' '

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

def drop_trailing_sentinel(labels: List[Tuple[float, float, Optional[str]]]) -> List[Tuple[float, float, Optional[str]]]:
    """Drop a trailing point label, folding its text into the preceding label.

    The last label is a sentinel only if it is a point (start == end) and
    something precedes it. A trailing range label is a real label, and a lone
    label has nothing to fold into, so both are returned untouched.
    """
    if len(labels) < 2:
        return labels

    start, end, text = labels[-1]
    if start != end:
        return labels

    result = labels[:-1]
    if text is not None:
        prev_start, prev_end, prev_text = result[-1]
        merged = text if prev_text is None else prev_text + SENTINEL_TEXT_SEPARATOR + text
        result[-1] = (prev_start, prev_end, merged)

    return result

def legatize_labels(labels: List[Tuple[float, float, Optional[str]]],
                    drop_sentinel: bool = True) -> List[Tuple[float, float, Optional[str]]]:
    """Convert point labels to legato (continuous) labels."""
    if not labels:
        return []

    result = []
    for i in range(len(labels)):
        start_time = labels[i][0]
        label_text = labels[i][2]

        # Extend to the start of the next label; the last one keeps its own end
        if i < len(labels) - 1:
            end_time = labels[i + 1][0]
        else:
            end_time = labels[i][1]

        result.append((start_time, end_time, label_text))

    if drop_sentinel:
        result = drop_trailing_sentinel(result)

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
  %(prog)s -i input.txt              # Modify input.txt in place
  %(prog)s -k input.txt              # Keep the trailing sentinel label"""
    )

    parser.add_argument('-i', '--in-place', action='store_true',
                        help='Edit input file in place')
    parser.add_argument('-k', '--keep-sentinel', action='store_true',
                        help='Keep the trailing point label instead of dropping it')
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
    legato_labels = legatize_labels(labels, drop_sentinel=not args.keep_sentinel)

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
