#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#     "pytest",
# ]
# ///
"""
test_audacity_legatize.py - Test suite for audacity_legatize.py
"""

import pytest
import subprocess
import sys
from pathlib import Path

# Import the functions from the main script
# (assumes audacity_legatize.py is in the same directory)
from audacity_legatize import parse_label_line, legatize_labels, format_label

class TestParseLabelLine:
    """Test the label line parsing function."""
    
    def test_parse_single_time(self):
        """Test parsing a line with just a time point."""
        result = parse_label_line("1.5")
        assert result == (1.5, 1.5, None)
    
    def test_parse_time_range(self):
        """Test parsing a line with start and end time."""
        result = parse_label_line("1.5\t2.5")
        assert result == (1.5, 2.5, None)
    
    def test_parse_with_label(self):
        """Test parsing a line with times and label."""
        result = parse_label_line("1.5\t2.5\tHello")
        assert result == (1.5, 2.5, "Hello")
    
    def test_parse_with_multipart_label(self):
        """Test parsing when label contains tabs."""
        result = parse_label_line("1.5\t2.5\tPart1\tPart2")
        assert result == (1.5, 2.5, "Part1\tPart2")
    
    def test_parse_empty_line(self):
        """Test parsing empty or whitespace lines."""
        assert parse_label_line("") is None
        assert parse_label_line("  \t  ") is None
    
    def test_parse_invalid_numbers(self):
        """Test parsing lines with invalid numbers."""
        assert parse_label_line("not_a_number") is None
        assert parse_label_line("1.5\tnot_a_number") is None
    
    def test_parse_with_spaces(self):
        """Test that lines with spaces are trimmed."""
        result = parse_label_line("  1.5\t2.5\tHello  ")
        assert result == (1.5, 2.5, "Hello")


class TestLegatizeLabels:
    """Test the legato conversion logic."""
    
    def test_empty_input(self):
        """Test with empty label list."""
        result = legatize_labels([])
        assert result == []
    
    def test_single_point_label(self):
        """Test with a single point label."""
        input_labels = [(1.0, 1.0, "Label1")]
        result = legatize_labels(input_labels)
        assert result == [(1.0, 1.0, "Label1")]
    
    def test_single_range_label(self):
        """Test with a single range label."""
        input_labels = [(1.0, 2.0, "Label1")]
        result = legatize_labels(input_labels)
        assert result == [(1.0, 2.0, "Label1")]
    
    def test_multiple_point_labels(self):
        """Test converting multiple point labels to legato."""
        input_labels = [
            (1.0, 1.0, "Label1"),
            (2.0, 2.0, "Label2"),
            (3.0, 3.0, "Label3")
        ]
        expected = [
            (1.0, 2.0, "Label1"),
            (2.0, 3.0, "Label2"),
            (3.0, 3.0, "Label3")
        ]
        result = legatize_labels(input_labels)
        assert result == expected
    
    def test_mixed_labels(self):
        """Test with mix of point and range labels."""
        input_labels = [
            (1.0, 1.0, "Label1"),
            (2.0, 2.5, "Label2"),
            (3.0, 3.0, None)
        ]
        expected = [
            (1.0, 2.0, "Label1"),
            (2.0, 3.0, "Label2"),
            (3.0, 3.0, None)
        ]
        result = legatize_labels(input_labels)
        assert result == expected
    
    def test_labels_without_text(self):
        """Test labels that have no text."""
        input_labels = [
            (1.0, 1.0, None),
            (2.0, 2.0, None),
            (3.0, 3.0, None)
        ]
        expected = [
            (1.0, 2.0, None),
            (2.0, 3.0, None),
            (3.0, 3.0, None)
        ]
        result = legatize_labels(input_labels)
        assert result == expected
    
    def test_preserves_last_range(self):
        """Test that the last label preserves its range if it has one."""
        input_labels = [
            (1.0, 1.0, "Label1"),
            (2.0, 4.0, "Label2")
        ]
        expected = [
            (1.0, 2.0, "Label1"),
            (2.0, 4.0, "Label2")
        ]
        result = legatize_labels(input_labels)
        assert result == expected


class TestFormatLabel:
    """Test the label formatting function."""
    
    def test_format_with_text(self):
        """Test formatting a label with text."""
        result = format_label(1.0, 2.0, "Hello")
        assert result == "1.0\t2.0\tHello"
    
    def test_format_range_without_text(self):
        """Test formatting a range without text."""
        result = format_label(1.0, 2.0, None)
        assert result == "1.0\t2.0"
    
    def test_format_point_without_text(self):
        """Test formatting a point without text."""
        result = format_label(1.0, 1.0, None)
        assert result == "1.0"
    
    def test_format_preserves_multipart_text(self):
        """Test that multipart text with tabs is preserved."""
        result = format_label(1.0, 2.0, "Part1\tPart2")
        assert result == "1.0\t2.0\tPart1\tPart2"


class TestIntegration:
    """Integration tests using the command-line interface."""
    
    @pytest.fixture
    def script_path(self):
        """Get the path to the main script."""
        return Path(__file__).parent / "audacity_legatize.py"
    
    def test_stdin_stdout(self, script_path):
        """Test reading from stdin and writing to stdout."""
        input_data = "1.0\t1.0\tLabel1\n2.0\t2.0\tLabel2\n3.0\t3.0\tLabel3\n"
        expected = "1.0\t2.0\tLabel1\n2.0\t3.0\tLabel2\n3.0\t3.0\tLabel3\n"
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=input_data,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert result.stdout == expected
    
    def test_file_input(self, script_path, tmp_path):
        """Test reading from a file."""
        input_file = tmp_path / "input.txt"
        input_file.write_text("1.0\t1.0\tLabel1\n2.0\t2.0\tLabel2\n")
        
        result = subprocess.run(
            [sys.executable, str(script_path), str(input_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert result.stdout == "1.0\t2.0\tLabel1\n2.0\t2.0\tLabel2\n"
    
    def test_file_output(self, script_path, tmp_path):
        """Test writing to an output file."""
        input_file = tmp_path / "input.txt"
        output_file = tmp_path / "output.txt"
        input_file.write_text("1.0\t1.0\tLabel1\n2.0\t2.0\tLabel2\n")
        
        result = subprocess.run(
            [sys.executable, str(script_path), str(input_file), str(output_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert output_file.read_text() == "1.0\t2.0\tLabel1\n2.0\t2.0\tLabel2\n"
    
    def test_in_place_editing(self, script_path, tmp_path):
        """Test in-place file editing."""
        input_file = tmp_path / "input.txt"
        original_content = "1.0\t1.0\tLabel1\n2.0\t2.0\tLabel2\n3.0\t3.0\tLabel3\n"
        input_file.write_text(original_content)
        
        result = subprocess.run(
            [sys.executable, str(script_path), "-i", str(input_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert input_file.read_text() == "1.0\t2.0\tLabel1\n2.0\t3.0\tLabel2\n3.0\t3.0\tLabel3\n"
    
    def test_error_in_place_without_file(self, script_path):
        """Test that in-place without input file fails."""
        result = subprocess.run(
            [sys.executable, str(script_path), "-i"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "requires an input file" in result.stderr
    
    def test_error_in_place_with_output(self, script_path, tmp_path):
        """Test that in-place with output file fails."""
        input_file = tmp_path / "input.txt"
        output_file = tmp_path / "output.txt"
        input_file.write_text("1.0\t1.0\tLabel1\n")
        
        result = subprocess.run(
            [sys.executable, str(script_path), "-i", str(input_file), str(output_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "cannot be used with an output file" in result.stderr
    
    def test_empty_file(self, script_path, tmp_path):
        """Test handling of empty input file."""
        input_file = tmp_path / "empty.txt"
        input_file.write_text("")
        
        result = subprocess.run(
            [sys.executable, str(script_path), str(input_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert result.stdout == ""
    
    def test_complex_example(self, script_path):
        """Test the example from the docstring."""
        input_data = "1.0\t1.0\tl1\n2.0\t2.0\tl2\n3.0\t3.0\n4.0\n5.0\n"
        expected = "1.0\t2.0\tl1\n2.0\t3.0\tl2\n3.0\t4.0\n4.0\t5.0\n5.0\n"
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=input_data,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert result.stdout == expected


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_unsorted_input(self):
        """Test that unsorted times are handled (or not)."""
        # This tests the current behavior - you might want to sort first
        input_labels = [
            (2.0, 2.0, "Label2"),
            (1.0, 1.0, "Label1"),
            (3.0, 3.0, "Label3")
        ]
        result = legatize_labels(input_labels)
        # Current implementation doesn't sort
        expected = [
            (2.0, 1.0, "Label2"),  # This might be unexpected!
            (1.0, 3.0, "Label1"),
            (3.0, 3.0, "Label3")
        ]
        assert result == expected
    
    def test_duplicate_times(self):
        """Test handling of duplicate time points."""
        input_labels = [
            (1.0, 1.0, "Label1"),
            (1.0, 1.0, "Label2"),
            (2.0, 2.0, "Label3")
        ]
        result = legatize_labels(input_labels)
        expected = [
            (1.0, 1.0, "Label1"),
            (1.0, 2.0, "Label2"),
            (2.0, 2.0, "Label3")
        ]
        assert result == expected
    
    def test_very_long_label(self):
        """Test handling of very long label text."""
        long_text = "A" * 1000
        result = format_label(1.0, 2.0, long_text)
        assert result == f"1.0\t2.0\t{long_text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])