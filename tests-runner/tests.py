#!/usr/bin/env python3
import pickle
import time
from audio_evaluation import calc_pesq, calc_p563
import os
import threading
import itertools
import ast
import random
import cv2
from skimage.metrics import structural_similarity as scikit_ssim
from skimage.metrics import peak_signal_noise_ratio as scikit_psnr
import network_utils

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
TEST_RESULTS_DIR=os.path.join(SCRIPT_DIR, "test_results")

SENDER_APP_PATH = os.path.join(SCRIPT_DIR, "sender_app") #TODO

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Reads the in file, saves data to compare in original_data_dir and out_data_dir
def audio_test_mock(in_file, original_data_dir, out_data_dir, parameters):

    with open(in_file, "rb") as tmp:
        os.set_blocking(tmp.fileno(), False)
        orig_file = os.path.join(original_data_dir, "in.wav")
        with open(orig_file, "wb") as out:
            out.write(tmp.read())
            
    with open(in_file, "rb") as tmp:
        os.set_blocking(tmp.fileno(), False)
        out_file = os.path.join(out_data_dir, "out.wav")
        with open(out_file, "wb") as out:
            out.write(tmp.read())

def measure_audio(original_data_dir, out_data_dir, results_dir) -> dict:
    in_file = os.path.join(original_data_dir, "in.wav")
    out_file = os.path.join(out_data_dir, "out.wav")
    pesq = random.randint(0,1)*5 # calc_pesq(in_file, out_file)
    p563 = random.randint(0,1)*5 # calc_p563(in_file)
    
    result = {"pesq": pesq, "p.563": p563}
    with open(os.path.join(results_dir, "result.pkl"), "wb") as f:
        pickle.dump(result, f)
    with open(os.path.join(results_dir, "result.txt"), "w") as f:
        f.write(str(result))
        
    return result

def video_test_mock(in_file, original_data_dir, out_data_dir, parameters):
    
    with open(in_file, "rb") as tmp:
        os.set_blocking(tmp.fileno(), False)
        orig_file = os.path.join(original_data_dir, "in.mp4")       
        with open(orig_file, "wb") as out:
            out.write(tmp.read())
            
    with open(in_file, "rb") as tmp:
        os.set_blocking(tmp.fileno(), False)
        out_file = os.path.join(out_data_dir, "out.mp4")
        with open(out_file, "wb") as out:
            out.write(tmp.read())

def measure_video(original_data_dir, out_data_dir, results_dir) -> dict:
    in_file = os.path.join(original_data_dir, "in.mp4")
    out_file = os.path.join(out_data_dir, "out.mp4")
    # in_video = cv2.VideoCapture(in_file)
    # out_video = cv2.VideoCapture(out_file)
    # frames_count = 0
    # psnr = 0
    # ssim = 0
    # while 1:
    #     _, image_in = in_video.read()
    #     _, image_out = out_video.read()
    #     if image_in is None or image_out is None:
    #         break
    #     # print(image_in.shape)

    #     print(frames_count)
    #     # cv2.imshow("Input", image_in)
    #     # cv2.waitKey(0)

    #     frames_count = frames_count + 1
    #     image_in = cv2.cvtColor(image_in, cv2.COLOR_BGR2RGB)
    #     image_out = cv2.cvtColor(image_out, cv2.COLOR_BGR2RGB)
    #     psnr_score = scikit_psnr(image_in, image_out)
    #     ssim_score = scikit_ssim(image_in, image_out, multichannel=True, full=True, win_size=7, channel_axis=2)
    #     psnr = psnr + min(psnr_score, 100)
    #     ssim = ssim + ssim_score[0]
    # #cv2.destroyAllWindows()
    # in_video.release()
    # out_video.release()
    
    psnr = random.randint(0, 100) # psnr / frames_count
    ssim = random.random() # ssim / frames_count
    result = {"psnr [dB]": psnr, "ssim [%]": ssim * 100.0}
    with open(os.path.join(results_dir, "result.pkl"), "wb") as f:
        pickle.dump(result, f)
    with open(os.path.join(results_dir, "result.txt"), "w") as f:
        f.write(str(result))
    return result

def perform_test(test_id, file_in, tested_parameters, test_fun, measure_fun) -> {float, float}:
    out_dir = os.path.join(TEST_RESULTS_DIR, test_id)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    results = {}
    
    def loop_iteration(measurement_id, parameters):
        dir_out = os.path.join(out_dir, str(measurement_id))
        ensure_dir(dir_out)
        original_data_dir = os.path.join(dir_out, "original")
        ensure_dir(original_data_dir)
        out_data_dir = os.path.join(dir_out, "out")
        ensure_dir(out_data_dir)
        results_dir = dir_out
        ensure_dir(results_dir)
        
        test_fun(file_in, original_data_dir, out_data_dir, parameters)
        result = measure_fun(original_data_dir, out_data_dir, results_dir)
        # A dictionary is not hashable and cannot be used as a key in a dictionary
        # a frozenset can
        results[frozenset(parameters.items())] = result
    
    keys, values = zip(*tested_parameters.items())
    parameter_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    time_start = time.time()
    threads = []
    for i in range(len(parameter_combinations)):
        measurement_id = i
        threads.append(threading.Thread(target=loop_iteration, args=(measurement_id, parameter_combinations[i],)))
    # threads = [threading.Thread(target=loop_iteration, args=(parameters,)) for parameters in parameter_combinations]
    
    print("Starting tests")
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Tests finished:")
    
    # for parameters in parameter_combinations:
    #     loop_iteration(parameters)
    with open(os.path.join(out_dir, "results.pkl"), "wb") as f:
        pickle.dump(results, f)
    with open(os.path.join(out_dir, "results.txt"), "w") as f:
        f.write(str(results))
        
    time_end = time.time()
    print("Time elapsed: ", time_end - time_start)
    return results


def perform_tests_audio(test_id, file, on_finish, parameters):
    results = perform_test(test_id, file, parameters, audio_test_mock, measure_audio) # Replace test_id with a unique identifier
    on_finish(results)

def perform_tests_video(test_id, file, on_finish, parameters):
    results = perform_test(test_id, file, parameters, video_test_mock, measure_video) # Replace test_id with a unique identifier
    on_finish(results)