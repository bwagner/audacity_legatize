# audacity-legatize

Convert Audacity point labels to legato (continuous) labels, where each label extends to the start of the next label.

## What it does

Transforms Audacity label tracks from point labels (instantaneous markers) to range labels (continuous segments):

**Before:**
```
1.0    1.0    Verse
2.5    2.5    Chorus  
4.0    4.0    Bridge
5.5
```

**After:**
```
1.0    2.5    Verse
2.5    4.0    Chorus
4.0    5.5    Bridge
5.5
```

Each label now extends until the start of the next label, creating a continuous (legato) sequence with no gaps.

## Installation

The script uses Python 3 and requires no external dependencies for basic operation.

### Using uv (recommended)

The script includes inline dependency metadata for [uv](https://github.com/astral-sh/uv):
```bash
# Make executable and run directly
chmod +x audacity_legatize.py
./audacity_legatize.py input.txt
```

### Using standard Python
```bash
python audacity_legatize.py input.txt
```

## Usage
```bash
# Read from stdin, write to stdout
./audacity_legatize.py < input.txt > output.txt

# Read from file, write to stdout  
./audacity_legatize.py input.txt

# Read from file, write to file
./audacity_legatize.py input.txt output.txt

# Modify file in place
./audacity_legatize.py -i input.txt

# Show help
./audacity_legatize.py -h
```

## Options

- `-i, --in-place`: Edit the input file in place (cannot be used with stdin or when output file is specified)

## Input Format

The script accepts Audacity label track format (tab-separated values):

1. **Point label with text:** `time⇥time⇥label`
2. **Range label with text:** `start⇥end⇥label`  
3. **Point without text:** `time⇥time` or just `time`
4. **Range without text:** `start⇥end`

Where `⇥` represents a tab character.

## Examples

### Basic usage

Input file `labels.txt`:
```
0.0    0.0    Intro
10.5   10.5   Verse 1
25.3   25.3   Chorus
40.0   40.0   Verse 2
55.5   55.5   Chorus
70.2   70.2   Outro
85.0
```

Command:
```bash
./audacity_legatize.py labels.txt output.txt
```

Output file `output.txt`:
```
0.0    10.5   Intro
10.5   25.3   Verse 1
25.3   40.0   Chorus
40.0   55.5   Verse 2
55.5   70.2   Chorus
70.2   85.0   Outro
85.0
```

### Pipeline usage

Combine with other tools:
```bash
# Sort labels by time and convert to legato
sort -n labels.txt | ./audacity_legatize.py > sorted_legato.txt

# Extract specific sections and make legato
grep "Chorus" labels.txt | ./audacity_legatize.py > choruses.txt
```

## Testing

Run the test suite using pytest:
```bash
# Install test dependencies
pip install pytest

# Run all tests
python -m pytest test_audacity_legatize.py -v

# Run with coverage report
pip install pytest-cov
python -m pytest test_audacity_legatize.py --cov=audacity_legatize --cov-report=term-missing
```

## Use Cases

- **Music production:** Convert beat markers or chord changes into continuous regions
- **Podcast editing:** Transform chapter markers into non-overlapping segments
- **Audio transcription:** Convert word timestamps into continuous speech segments
- **Video subtitling:** Create non-overlapping subtitle regions from point markers

## Notes

- The script preserves the last label's duration if it already has a range
- Labels without text are supported and remain without text after conversion
- Empty lines and invalid entries are skipped
- For in-place editing, a temporary file is used to ensure atomicity

## Limitations

- Input labels should be sorted by time for correct results
- The script does not validate overlapping ranges in the input
- Very large files are loaded entirely into memory

## Contributing

Issues and pull requests are welcome! Please ensure:
- All tests pass
- New features include tests
- Code follows Python conventions

## License

MIT License - see LICENSE file for details

## See Also
[shift_labels](https://github.com/bwagner/shift_labels), [quantize_labels](https://github.com/bwagner/quantize_labels), [beats2bars](https://github.com/bwagner/beats2bars), [pyaudacity](https://github.com/bwagner/pyaudacity)
