from tika import parser
from itertools import *
import os
import sys
import pandas as pd
import numpy as np

import sys
sys.path.append('..')
from common import *

def _extract_numbers(s):
    """ List[str table numbers] -> List[int numbers (-1 for an information missing)] """
    s+=' '
    result = []
    acum_number = 0
    last_digit = -1
    for i in range(len(s)):
        if s[i].isdigit():
            if last_digit<i-2:
                result.append(-1)
            acum_number = acum_number*10 + int(s[i])
            last_digit = i
        else:
            if acum_number:
                result.append(acum_number)
            acum_number = 0
    return result
def _get_number_tuple(numbers):
    """ List[int numbers (-1 for an information missing)] -> [CONFIRMADOS, DESCARTADOS, SOSPECHOSOS, TOTAL] """
    assert numbers[-1]>0
    res_tuple = [0,0,0,0]
    res_tuple[3] = numbers[-1]
    numbers = numbers[:-1]
    if numbers[0]!=-1:
        res_tuple[0] = numbers[0]
    numbers = numbers[1:]
    if len(numbers)==1:
        res_tuple[2] = numbers[0]
    else:
        assert len(numbers)==2
        res_tuple[1] = numbers[0]
        if numbers[1]!=-1:
            res_tuple[2] = numbers[1]
    return res_tuple

def _extract_values(s):
    """ List[str table entry] -> [PLACE, CONFIRMADOS, DESCARTADOS, SOSPECHOSOS, TOTAL] """
    if not s:
        return None
    suffix_len = len(''.join(takewhile(lambda x: not x.isalpha(), s[len(s)::-1])))
    place_name = s[:len(s)-suffix_len]
    place_name_norm = normalize_str(place_name)
    if len([x for x in place_name if x.isalpha()])==0:
        return None
    bad_tokens = ['2020 Año del General Manuel Belgrano', 'Ministerio de Salud', 'Juan de Garay 2880']
    bad_tokens = [ normalize_str(v) for v in bad_tokens ]
    if any(place_name_norm.find(v)!=-1 for v in bad_tokens):
        return None
    numbers = s[len(s)-suffix_len:]
    numbers = _extract_numbers(numbers)
    departamento = any([x.islower() for x in place_name])
    return [place_name]+_get_number_tuple(numbers)

def _extract_table_text(text):
    """ Given the text look up to the main table and extract it (using adhoc markers). """
    init_marker = 'Departamento/ Localidad'
    assert sum(1 for i in range(len(text)) if text.startswith(init_marker, i)) == 1
    text = text[text.find(init_marker):]
    text = ''.join(dropwhile(lambda x: x!='\n',text))
    text = ''.join(dropwhile(lambda x: x=='\n',text))
    end_marker = 'Total'
    end_marker_pos = text.find(end_marker)
    return text[:end_marker_pos].split('\n') + [ text[end_marker_pos:].split('\n')[0] ]

def _fill_department(place_name):
    """ Given the place name deduce if it's a department by seeing lowercase/uppercase and add '#D_' prefix """
    is_dep = any([x.islower() for x in place_name])
    place_name = normalize_str(place_name)
    if place_name=='TOTAL':
        return '##TOTAL'
    return ('#D_' if is_dep else '') + place_name

def parse_pdf(in_pdf_filepath, out_csv_filepath):
    """ Read, parse and process PDF report and produce a CSV """
    print('Parsing pdf with adhoc parser...')
    parse_result = parser.from_file(in_pdf_filepath)
    text = parse_result['content']
    text_list = _extract_table_text(text)
    data = [ _extract_values(s) for s in text_list ]    
    data = [ v for v in data if v is not None ]
    df = pd.DataFrame(data,columns=['Departamento/ Localidad','Confirmados','Descartados','Sospechosos','Total'])
    df['Departamento/ Localidad']=df['Departamento/ Localidad'].apply(_fill_department)
    df.to_csv(out_csv_filepath, index = False)
    print('Finished!')

if __name__ == '__main__':
    usage = ''' Usage:
    python adhoc_pdf_santa_fe_parser.py reporte.pdf output.csv '''
    if len(sys.argv)!=3:
        print(usage)
        exit(0)
    parse_pdf(sys.argv[1], sys.argv[2])
