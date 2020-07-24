"""
Dada una serie temporal con LOCATION, hace la imagen de duplicacion de tiempo
y la guarda en IMG_PATH
Output functions: calculate_images
"""
import pandas as pd
import numpy as np
import os
from PIL import Image

import saliomapita_dependency

# La correspondencia entre THRESHOLDS y COLORS_RGB esta dada en la funcion value_to_color
# La idea es que si los confirmados es < MIN_THRESHOLD se usa el ultimo color en COLORS_HEXA
# Si no si los confirmados son mayores o iguales que THRESHOLDS[0] se usa COLORS_HEXA[0]
# Si no si los confirmados son mayores o iguales que THRESHOLDS[1] se usa COLORS_HEXA[1]
# ... asi sucesivamente
# THRESHOLDS[-2] DEBE ser siempre 0, estableciendo el color de menor valor.
MIN_THRESHOLD = {
    0: 100,
    1: 10,
    2: 3,
    3: 3
}
THRESHOLDS = [40,30,20,10,0,0]
COLORS_HEXA = [ "F4E5D0", "FED79D", "FBA525", "FF6500", "C71E18", "E6E6E6" ]
assert THRESHOLDS[-2]==0
# Convierte COLORS_HEXA a 3-uplas hexa (como (0,0,0) o (255,255,255))
COLORS_RGB = [ list(int(c[i:i+2], 16) for i in (0, 2, 4)) for c in COLORS_HEXA ]
# Cantidad de dias que aparecen en las imagenes
IMG_DAYS = 56

def value_to_color(value, location_level):
    """
    Calcula a partir de (DUPLICATION_TIME,CONFIRMADOS) el color
    """
    confirmados = value[1]
    dup_time =  value[0]
    if confirmados<MIN_THRESHOLD[location_level]:
        return COLORS_RGB[-1]
    for threshold,color in zip(THRESHOLDS,COLORS_RGB):
        if dup_time>=threshold:
            return color
    # Esto no deberia suceder nunca
    print(dup_time)
    assert False
def values_to_img(values, location_level, len_day=5, height=15, rule_height=7, rule_width=1):
    """
    Produce imagen de regla a partir de lista values=[(DUPLICATION_TIME,CONFIRMADOS)]
        - len_day: longitud del dia en pixeles.
        - height:  altura del dia en pixeles.
        - rule_height: altura de la parte de la regla que sobresale en pixeles.
        - rule_width: separacion entre cada dia en pixeles.
    """
    # Contador de diassaliomapita_dependency para poner lineas negras que separen por semana.
    n_days = 0
    # Primero producimos dos lineas de 1px de alto color_line, la superior y rule_line, la inferior.
    color_line = []
    rule_line = []
    for v in values:
        for _ in range(rule_width):
            color_line.append((0,0,0) if n_days%7==0 else (255,255,255))
            rule_line.append((0,0,0) if n_days%7==0 else (255,255,255))
        color = value_to_color(v, location_level)
        for _ in range(len_day):
            color_line.append(color)
            rule_line.append((255,255,255))
        n_days += 1
    for _ in range(rule_width):
        color_line.append((0,0,0))
        rule_line.append((0,0,0))
    # Luego concatenamos verticalmente color_line*height + rule_line*rule_height
    img_np = np.array([ color_line for _ in range(height) ] + [ rule_line for _ in range(rule_height) ] ,dtype=np.uint8)
    img = Image.fromarray(img_np)
    return img

def calculate_images(df):
    """ df must be a DataFrame with [LOCATION, TYPE].
        For each LOCATION in df calculate an image for the table (the one with the rule below).
        Store it in saliomapita_dependency.IMG_PATH folder. """
    df=df.reset_index().set_index(['LOCATION','TYPE'])
    for location in df.index.get_level_values(0):
        # print(location)
        values = list(zip(list(df.loc[location].loc['DUPLICATION_TIME']) ,list(df.loc[location].loc['CONFIRMADOS'])))
        img = values_to_img(values[-IMG_DAYS:], location.count('/'))
        img.save(os.path.join(saliomapita_dependency.IMG_PATH,location.replace('/','-')+'.png'))
