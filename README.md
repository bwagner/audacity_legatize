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
```

Each label now extends until the start of the next label, creating a continuous (legato) sequence with no gaps.

The trailing `5.5` is gone. Its only job in the input was to supply an end time for `Bridge`, so once that end time is assigned it carries no information - keeping it would leave a stray zero-length label at the end of your track. Pass `-k` if you want it back.

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

# Keep the trailing sentinel label
./audacity_legatize.py -k input.txt

# Show help
./audacity_legatize.py -h
```

## Options

- `-i, --in-place`: Edit the input file in place (cannot be used with stdin or when output file is specified)
- `-k, --keep-sentinel`: Keep the trailing point label instead of dropping it

## The trailing sentinel

Point-label input usually ends with one marker more than there are labels - the final marker exists only to close off the last real label. After legatizing it has served its purpose, so by default it is dropped.

A label counts as a sentinel only if it is the **last** label and its start equals its end. Two things are therefore never dropped:

- a trailing **range** label, which is a real label with a duration of its own
- a **lone** label, since there is nothing to legatize and nothing to fold it into

If the sentinel carries text, that text is appended to the preceding label rather than discarded, separated by a space:

```
1.0    1.0    Bridge
5.5    5.5    fine
```
becomes
```
1.0    5.5    Bridge fine
```

Note that this means a trailing point label that you meant to keep - `70.2 70.2 Outro` with no terminator after it - will be absorbed into the label before it. Use `-k` for such files.

Dropping the sentinel is idempotent: re-running the tool on its own output changes nothing, because the last label is then a range and is no longer treated as a sentinel.

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
```

With `-k`, the closing `85.0` marker is retained as a final point label.

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

- The trailing sentinel label is dropped by default; see [The trailing sentinel](#the-trailing-sentinel)
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
- [rebuildap](https://github.com/bwagner/rebuildap)
- [audacity_shift_labels](https://github.com/bwagner/audacity_shift_labels)
- [audacity_click_label](https://github.com/bwagner/audacity_click_label)
- [quantize_labels](https://github.com/bwagner/quantize_labels)
- [beats2bars](https://github.com/bwagner/beats2bars)
- [pyaudacity](https://github.com/bwagner/pyaudacity)
