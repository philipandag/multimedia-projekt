#!/usr/bin/env python3
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMainWindow, QVBoxLayout
from PyQt6.QtCore import pyqtSlot
import sys
from audio_evaluation import calc_pesq, calc_p563
import os
import aiofiles
import threading
import itertools


SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIR=os.path.join(SCRIPT_DIR, "resources")
AUDIO_FILE=os.path.join(RESOURCES_DIR, "ENG_M.wav")
AUDIO_FILE_OUT_TMP=os.path.join(RESOURCES_DIR, "eng_m6.wav")
TEST_RESULTS_DIR=os.path.join(SCRIPT_DIR, "test_results")

### PARAMETERS TO TEST
PACKET_LOSS_VALUES_PERCENT = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90] 

def audio_test_mock(in_file, out_file, value):
    with open(in_file) as in_file:
        pass
    with open(out_file) as out_file:
        pass


def perform_wav_test(test_name, file_in, test_function, tested_values) -> {float, float}:
    out_dir = os.path.join(TEST_RESULTS_DIR, test_name)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    results = {}
    
    def loop_iteration(values):
        print(values)
        return
        file_out = os.path.join(out_dir, test_name+"_"+str(value) + ".wav")
        with open(AUDIO_FILE, "rb") as tmp:
            with open(file_out, "wb+") as out:
                out.write(tmp.read())
                
        test_function(file_in, file_out, value)
        pesq = calc_pesq(file_in, file_out)
        p563 = calc_p563(file_in)
        print(value, pesq, p563)
        results[value] = {"pesq": pesq, "p563": p563}
        #return {"pesq": pesq, "p563": p563}
    
    results = {}
    keys, values = zip(*tested_values.items())
    print(keys)
    print(values)
    values_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    
    threads = [threading.Thread(target=loop_iteration, args=(values,)) for values in values_combinations]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results

def perform_tests(packet_loss_iter):
    results = {}
    tested_values = {
        "loss": packet_loss_iter
    }
    perform_wav_test("loss", AUDIO_FILE, audio_test_mock, tested_values)
    return results