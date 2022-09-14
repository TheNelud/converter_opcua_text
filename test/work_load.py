import os
import os.path
import time

from converter.parser import get_config, last_file

if __name__ == '__main__':
    config = get_config()
    print(config['path'])
    oldFile = os.path.join(config['path'], 'RTP_Values._')
    print(oldFile)

    while True:
        if oldFile == os.path.join(config['path'], 'RTP_Values._'):
            oldFile = os.path.join(config['path'], 'RTP_Values._')
            newFile = os.path.join(config['path'], 'RTP_Values._')
            os.rename(oldFile, newFile)
            oldFile = os.path.join(config['path'], 'RTP_Values._')
            print('RTP_VALUES.txt_')
            time.sleep(50)
        else:
            oldFile = os.path.join(config['path'], 'RTP_Values._')
            newFile = os.path.join(config['path'], 'RTP_Values._')
            os.rename(oldFile, newFile)
            oldFile = os.path.join(config['path'], 'RTP_Values._')
            print('RTP_VALUES.txt')
            time.sleep(50)
