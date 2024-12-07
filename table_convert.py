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

def detect_header_rows(table):
    for idx, r in enumerate(reversed(new_table)):
        if r[0] == '': ## header end
            first_value_row_idx = len(new_table) - idx
            break         
    if first_value_row_idx is None:
        for idx, r in enumerate(reversed(new_table)):
            if all(not item for item in r[1:]):
                first_value_row_idx = len(new_table) - idx                
                break            

    
    
def fill_table_headers(table):
    new_table = copy.deepcopy(table)
    
    first_value_col_idx = 1

    first_value_row_idx = None 
    
    for idx, r in enumerate(reversed(new_table)):
        if r[0] == '': ## header end
            first_value_row_idx = len(new_table) - idx
            break         
    if first_value_row_idx is None:
        for idx, r in enumerate(reversed(new_table)):
            if all(not item for item in r[1:]):
                first_value_row_idx = len(new_table) - idx                
                break            
                        
    for idx, r in enumerate(reversed(new_table[0:first_value_row_idx])):
       new_table[idx] = fill_column_headers(new_table[idx])    
        
    return (new_table, first_value_col_idx, first_value_row_idx)

def convert_table(table):
    (table, first_value_col_idx, first_value_row_idx) = fill_table_headers(table)
    res = []
    if first_value_col_idx is None or first_value_row_idx is None:
        return res
        
    for i in range(first_value_row_idx, len(table)):           
        for j in range(first_value_col_idx, len(table[0])):            
            r = extract_number(table[i][j])
            if r is None:
                continue
            (number, other_chars) = r
            
            upper_heads = []
            for ih in reversed(range( 0, first_value_row_idx)):
                header_text = table[ih][j]
                if header_text is None:
                    continue
                if other_chars == '':
                    if '€m' in  header_text:
                        header_text  = header_text.replace('€m', '').strip()
                        other_chars = 'million'
                upper_heads.append(header_text)

            left_heads = []
            for jh in reversed(range( 0, first_value_col_idx)):
                left_heads.append(table[i][jh])
            item = {'number_value': number, 'scale': other_chars, 'category': left_heads[0]}
            for  idx, h in enumerate(upper_heads):
                item['header' + str(idx+1)] = h
            #res.append({'number_value': number, 'scale': other_chars, 'categories': left_heads , 'metadata': upper_heads })
            #res.append({'number_value': number, 'scale': other_chars, 'categories': left_heads + upper_heads })
            res.append(item)
    return res
    
def detect_header_rows(table):
    res = [1]
    for idx, r in enumerate(table[1:]):
        if r[0] == '' or all(not item for item in r[1:]):
            res.append(1)
        else:
            res.append(0)        
    return res


def split_multitables(table):
    hrs = detect_header_rows(table)

    multi_idxs = []
    for idx in range(1, len(hrs)-1):
        if hrs[idx] == 1 and hrs[idx-1] == 0:
           #print(idx)
           multi_idxs.append(idx)
    
    if len(multi_idxs) == 0:
        return [table]

    top_header_idx = 0
    
    for idx in range(1, len(hrs)-1):
        if hrs[idx] == 1 and hrs[idx-1] == 1 and hrs[idx+1] == 0:
            #print(idx-1)
            top_header_idx = idx -1
            multi_idxs.insert(0, idx)
            break
    
    multi_idxs.append(len(table))
    
    tables = []
    for idx in range(len(multi_idxs[:-1])):
        new_table = table[0:top_header_idx + 1]  + table[multi_idxs[idx]:multi_idxs[idx+1]]        
        tables.append(new_table)
        
    return tables 
    
def convert_multitable(table):
    tables = split_multitables(table)
    values = []
    for subtable in tables:
        
        subvalues = convert_table(subtable)
        values = values + subvalues
    return values
