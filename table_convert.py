import re
from typing import Optional, Tuple
import copy


def extract_number(input_str: str) -> Optional[Tuple[float, str]]:
    """
    Extracts a numeric value from a string and returns a tuple (number, other_characters).
    If no number is found, returns None.
    
    Handles integers, floats, percentages, currency, thousand separators, and scale units like 'm' (million) or 'k' (thousand).
    
    Args:
        input_str (str): The input string.
    
    Returns:
        Optional[Tuple[float, str]]: A tuple with the number and the other characters,
        or None if no number is found.
    """
    # Define a regex pattern for matching numbers
    pattern = r"""
        (?P<number>
            [-+]?                        # Optional sign
            (?:
                \d{1,3}(?:,\d{3})*       # Integer with thousand separators
                (?:\.\d+)?               # Optional decimal part
                |
                \d+\.\d+                 # Decimal number without thousand separators
            )
        )
        (?P<scale>[kKmM]?)               # Optional scale: k (thousand), m (million)
        (?P<percent>\s*%?)               # Optional percentage symbol
    """
    
    # Compile the regex with the verbose flag
    regex = re.compile(pattern, re.VERBOSE)
    
    match = regex.search(input_str)
    if not match:
        return None
    
    number_str = match.group("number").replace(',', '')  # Remove commas from the number
    scale = match.group("scale") or ''
    percent = match.group("percent") or ''
    
    try:
        number = float(number_str)
    except ValueError:
        return None
    
    # Adjust number based on scale
    scale = scale.lower()
    if scale == 'k':
        number *= 1_000
    elif scale == 'm':
        number *= 1_000_000

    # Construct the other_characters string
    other_characters = f"{percent}{scale}".strip()
    
    return number, other_characters


def fill_column_headers(row):    
    if row[0] != '':
        return row
    new_row = ['']
    
    col_num = len([c for c in row if c!=''])    
    step_size = int((len(row) - 1) / col_num)    
    for i in range(col_num):
        col_name = None
        for j in range(step_size):
            if row[1+i*step_size+j] != '':
                col_name = row[1+i*step_size+j]
                break
        for j in range(step_size):
            new_row.append(col_name)
    return new_row

def fill_table_headers(table):
    new_table = copy.deepcopy(table)
    
    first_value_col_idx = 1
    
    for idx, r in enumerate(reversed(new_table)):
        if r[0] == '': ## header end
            first_value_row_idx = len(new_table) - idx
            break        
    for idx, r in enumerate(reversed(new_table[0:first_value_row_idx])):
       new_table[idx] = fill_column_headers(new_table[idx])    
        
    return (new_table, first_value_col_idx, first_value_row_idx)

def convert_table(table):
    (table, first_value_col_idx, first_value_row_idx) = fill_table_headers(table)
    res = []
    for i in range(first_value_row_idx, len(table)):           
        for j in range(first_value_col_idx, len(table[0])):            
            r = extract_number(table[i][j])
            if r is None:
                continue
            (number, other_chars) = r
            
            upper_heads = []
            for ih in reversed(range( 0, first_value_row_idx)):
                header_table[ih][j])
                if other_chars = '':
                    if 
                upper_heads.append()

            left_heads = []
            for jh in reversed(range( 0, first_value_col_idx)):
                left_heads.append(table[i][jh])
                        
            #res.append({'number_value': number, 'scale': other_chars, 'categories': left_heads , 'metadata': upper_heads })
            res.append({'number_value': number, 'scale': other_chars, 'categories': left_heads + upper_heads })
    return res

