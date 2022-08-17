import os
import os.path
import time

from converter.parser import get_config, last_file

if __name__ == '__main__':
    config = get_config()
    print(config['path'])
    oldFile = os.path.join(config['path'], 'RTP_Values.txt')
    print(oldFile)

    while True:
        if oldFile == os.path.join(config['path'], 'RTP_Values.txt'):
            oldFile = os.path.join(config['path'], 'RTP_Values.txt')
            newFile = os.path.join(config['path'], 'RTP_Values.txt_')
            os.rename(oldFile, newFile)
            oldFile = os.path.join(config['path'], 'RTP_Values.txt_')
            print('RTP_VALUES.txt_')
            time.sleep(15)
        else:
            oldFile = os.path.join(config['path'], 'RTP_Values.txt_')
            newFile = os.path.join(config['path'], 'RTP_Values.txt')
            os.rename(oldFile, newFile)
            oldFile = os.path.join(config['path'], 'RTP_Values.txt')
            print('RTP_VALUES.txt')
            time.sleep(15)
