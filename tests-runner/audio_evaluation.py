from scipy.io import wavfile
from pesq import pesq
import subprocess
import os
import re

P563_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "p563")

def calc_pesq(in_file: str, out_file: str) -> float:
    rate, ref = wavfile.read(in_file)
    rate, deg = wavfile.read(out_file)
    
    try:
        return pesq(rate, ref, deg, 'nb')
    except:
        return pesq(rate, ref, deg, 'wb')
    
def calc_p563(in_file: str) -> float:
    out = subprocess.run([P563_PATH, in_file], stdout=subprocess.PIPE).stdout.decode().strip()
    print(out)
    out = out.split()[3]
    return float(out)
            
