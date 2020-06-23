import pandas as pd
import numpy as np
import os
from PIL import Image


THRESHOLDS = [28,14,7,0,0]
COLORS_HEXA = [ "F4E5D0", "FED79D", "FBA525", "FF6500", "E6E6E6" ]
COLORS_RGB = [ list(int(c[i:i+2], 16) for i in (0, 2, 4)) for c in COLORS_HEXA ]
IMG_PATH = './imgs/'
IMG_DAYS = 56

def value_to_color(value):
    confirmados = value[1]
    dup_time =  value[0]
    if confirmados<10:
        return COLORS_RGB[-1]
    for threshold,color in zip(THRESHOLDS,COLORS_RGB):
        if dup_time>=threshold:
            return color
    print(dup_time)
    assert False
def values_to_img(values, len_day=5, height=15, rule_height=7, rule_width=1):
    color_line = []
    n_days = 0
    rule_line = []
    for v in values:
        for _ in range(rule_width):
            color_line.append((0,0,0) if n_days%7==0 else (255,255,255))
            rule_line.append((0,0,0) if n_days%7==0 else (255,255,255))
        color = value_to_color(v)
        for _ in range(len_day):
            color_line.append(color)
            rule_line.append((255,255,255))
        n_days += 1
    for _ in range(rule_width):
        color_line.append((0,0,0))
        rule_line.append((0,0,0))
    img_np = np.array([ color_line for _ in range(height) ] + [ rule_line for _ in range(rule_height) ] ,dtype=np.uint8)
    img = Image.fromarray(img_np)
    return img

def calculate_colors(df):
    df=df.reset_index().set_index(['LOCATION','TYPE'])
    for location in df.index.get_level_values(0):
        print(location)
        values = list(zip(list(df.loc[location].loc['DUPLICATION_TIME']) ,list(df.loc[location].loc['CONFIRMADOS'])))
        img = values_to_img(values[-IMG_DAYS:])
        img.save(os.path.join(IMG_PATH,location.replace('/','-')+'.png'))
