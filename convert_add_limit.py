#!/usr/bin/env python3
"""
convert_add_limit.py — extract the add_limit parameter from bcBALA_ file paths

PURPOSE
  Given lines of the form "<number> <path>", replaces the first column with the
  trailing numeric component of the path when --convert is passed.  Used to
  translate raw bcBALA_ file paths (e.g. /nas/bcBALA_1_1000000) into the
  add_limit integer (1000000) so downstream plotting scripts can use a clean
  numeric axis.

USAGE
  cat data.txt | python3 convert_add_limit.py --convert
  python3 convert_add_limit.py --convert --file data.txt

ROLE IN PIPELINE
  Post-processing helper called before plot_costs.py or BALAsamp_cost() when
  the X-axis needs to be the map-size integer rather than the full file path.
"""

import sys
import re
import argparse

def extract_add_limit_from_path(path):
    """Extract the last number from a file path."""
    # Split by underscore and take the last part
    parts = path.split('_')
    if parts:
        last_part = parts[-1]
        # Extract any digits from the last part
        match = re.search(r'\d+', last_part)
        if match:
            return int(match.group())
    return None

def process_data(input_text, convert_flag):
    """Process the input data and optionally convert add_limit values."""
    lines = input_text.strip().split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse the line: number and path
        match = re.match(r'^(\s*\d+)\s+(.+)$', line)
        if match:
            value = match.group(1)
            path = match.group(2)
            
            if convert_flag:
                # Extract add_limit from path
                add_limit = extract_add_limit_from_path(path)
                if add_limit is not None:
                    # Replace the first column with the add_limit
                    processed_line = f"{add_limit} {path}"
                else:
                    # If no add_limit found, keep original
                    processed_line = f"{value} {path}"
            else:
                # Keep original format
                processed_line = f"{value} {path}"
            
            processed_lines.append(processed_line)
        else:
            # If line doesn't match expected format, keep as is
            processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def main():
    parser = argparse.ArgumentParser(description='Convert add_limit values from file paths')
    parser.add_argument('--convert', action='store_true', 
                        help='Convert first column to add_limit values from paths')
    parser.add_argument('--file', type=str, 
                        help='Input file (default: read from stdin)')
    
    args = parser.parse_args()
    
    # Read input
    if args.file:
        try:
            with open(args.file, 'r') as f:
                input_text = f.read()
        except FileNotFoundError:
            sys.exit(f"Error: File '{args.file}' not found")
    else:
        input_text = sys.stdin.read()
    
    # Process data
    result = process_data(input_text, args.convert)
    
    # Output result
    print(result)

if __name__ == "__main__":
    main()
