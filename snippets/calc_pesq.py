from scipy.io import wavfile
from pesq import pesq
import sys

ORIGINAL_ = "ENG_M.wav" # ITU 4.5
MELPE_PLUS_4kb = "eng_m6.wav" # ITU 3.266

args = sys.argv[1:]
if len(args) == 2:
    rate, ref = wavfile.read(args[0])
    rate, deg = wavfile.read(args[1])
    
print(pesq(rate, ref, deg, 'nb'))

