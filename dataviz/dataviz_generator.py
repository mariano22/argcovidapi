import os
import glob

if __name__ == '__main__':
    with open('dataviz.md', 'w') as f:
        for fp in glob.glob('./*.png'):
            fn = os.path.basename(fp)
            f.write('![{}]({})\n'.format(fn[:-4],fp))
