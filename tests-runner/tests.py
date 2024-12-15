#!/usr/bin/env python3
from audio_evaluation import calc_pesq, calc_p563
import os
import threading
import itertools
import ast
import random


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

def perform_wav_test(file_in, test_function, tested_values) -> {float, float}:
    test_name = "audio_wav_"
    out_dir = os.path.join(TEST_RESULTS_DIR, test_name)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    results = {}
    
    def loop_iteration(values):

        file_out = os.path.join(out_dir, test_name+"_"+str(values) + ".wav")
        with open(AUDIO_FILE, "rb") as tmp:
            os.set_blocking(tmp.fileno(), False)
            with open(file_out, "wb+") as out:
                out.write(tmp.read())
                
                
        test_function(file_in, file_out, values)
        pesq = calc_pesq(file_in, file_out) + random.random()
        p563 = calc_p563(file_in) + random.random()
        # print(values, pesq, p563)
        results[frozenset(values.items())] = {"pesq": pesq, "p.563": p563}
    
    keys, values = zip(*tested_values.items())
    values_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    threads = [threading.Thread(target=loop_iteration, args=(values,)) for values in values_combinations]
    
    print("Starting tests")
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Tests finished:")
    return results

def perform_tests(on_finish, packet_loss_iter, rtt_iter, reorder_iter):
    tested_values = {
        packet_loss_iter.name: list(packet_loss_iter),
        rtt_iter.name: list(rtt_iter),
        reorder_iter.name: list(reorder_iter)
    }
    results = perform_wav_test(AUDIO_FILE, audio_test_mock, tested_values)
    on_finish(results)