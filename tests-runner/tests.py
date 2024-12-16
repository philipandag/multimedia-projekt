#!/usr/bin/env python3
import pickle
from audio_evaluation import calc_pesq, calc_p563
import os
import threading
import itertools
import ast
import random
import cv2
from skimage.metrics import structural_similarity as scikit_ssim
from skimage.metrics import peak_signal_noise_ratio as scikit_psnr

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
TEST_RESULTS_DIR=os.path.join(SCRIPT_DIR, "test_results")

def audio_test_mock(in_file, out_file, parameters):
    with open(in_file, "rb") as tmp:
        os.set_blocking(tmp.fileno(), False)
        with open(out_file, "wb+") as out:
            out.write(tmp.read())
def measure_audio(in_file, out_file) -> dict:
    pesq = random.randint(0,1)*5 # calc_pesq(in_file, out_file)
    p563 = random.randint(0,1)*5 # calc_p563(in_file)
    return {"pesq": pesq, "p.563": p563}

def video_test_mock(in_file, out_file, parameters):
    with open(in_file, "rb") as tmp:
        os.set_blocking(tmp.fileno(), False)
        with open(out_file, "wb+") as out:
            out.write(tmp.read())

def measure_video(in_file, out_file) -> dict:
    in_video = cv2.VideoCapture(in_file)
    out_video = cv2.VideoCapture(out_file)
    frames_count = 0
    psnr = 0
    ssim = 0
    while 1:
        _, image_in = in_video.read()
        _, image_out = out_video.read()
        if image_in is None or image_out is None:
            break
        # print(image_in.shape)
        # cv2.namedWindow("Input")
        # cv2.imshow("Input", image_in)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        frames_count = frames_count + 1
        image_in = cv2.cvtColor(image_in, cv2.COLOR_BGR2RGB)
        image_out = cv2.cvtColor(image_out, cv2.COLOR_BGR2RGB)
        psnr_score = scikit_psnr(image_in, image_out)
        ssim_score = scikit_ssim(image_in, image_out, multichannel=True, full=True, win_size=7, channel_axis=2)
        psnr = psnr + min(psnr_score, 100)
        ssim = ssim + ssim_score[0]
    in_video.release()
    out_video.release()
    psnr = psnr / frames_count
    ssim = ssim / frames_count
    return {"psnr [dB]": psnr, "ssim [%]": ssim * 100.0}

def perform_test(test_id, file_in, tested_parameters, test_fun, measure_fun) -> {float, float}:
    out_dir = os.path.join(TEST_RESULTS_DIR, test_id)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    results = {}
    
    def loop_iteration(parameters):
        file_out = os.path.join(out_dir, test_id+"_"+str(parameters))
        test_fun(file_in, file_out, parameters)
        result = measure_fun(file_in, file_out)
        # A dictionary is not hashable and cannot be used as a key in a dictionary
        # a frozenset can
        results[frozenset(parameters.items())] = result
    
    keys, values = zip(*tested_parameters.items())
    parameter_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
    threads = [threading.Thread(target=loop_iteration, args=(parameters,)) for parameters in parameter_combinations]
    
    print("Starting tests")
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Tests finished:")
    return results


def perform_tests_audio(file, on_finish, packet_loss_iter, rtt_iter, reorder_iter):
    tested_values = {
        packet_loss_iter.name: list(packet_loss_iter),
        rtt_iter.name: list(rtt_iter),
        reorder_iter.name: list(reorder_iter)
    }
    results = perform_test("audio_wav_", file, tested_values, audio_test_mock, measure_audio) # Replace test_id with a unique identifier
    on_finish(results)

def perform_tests_video(file, on_finish, packet_loss_iter, rtt_iter, reorder_iter):
    tested_values = {
        packet_loss_iter.name: list(packet_loss_iter),
        rtt_iter.name: list(rtt_iter),
        reorder_iter.name: list(reorder_iter)
    }
    results = perform_test("audio_wav_", file, tested_values, video_test_mock, measure_video) # Replace test_id with a unique identifier
    on_finish(results)