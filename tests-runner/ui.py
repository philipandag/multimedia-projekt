#!/usr/bin/env python3
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMainWindow, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSlot
import sys
import tests
from test_data_selector import TestDataSelector, TestDataSelectorController
import threading
import numpy as np
import os

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIR=os.path.join(SCRIPT_DIR, "resources")
AUDIO_FILE=os.path.join(RESOURCES_DIR, "ENG_M.wav")
AUDIO_FILE_OUT_TMP=os.path.join(RESOURCES_DIR, "eng_m6.wav")
VIDEO_FILE=os.path.join(RESOURCES_DIR, "shrek_short.mp4")
VIDEO_FILE_OUT_TMP=os.path.join(RESOURCES_DIR, "shrek_out.mp4")
        
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        in_file_button = QPushButton()
        in_file_button.setText("Select input file...")
        in_file_button.clicked.connect(self.open_in_file_dialog)
        self.in_file_name_label = QLabel()
        self.in_file_name = VIDEO_FILE
        self.in_file_name_label.setText(self.in_file_name)
        layout.addWidget(self.in_file_name_label)
        layout.addWidget(in_file_button)
        
        packet_loss_selector = TestDataSelector("Packet loss [%]", min=0.0, max=100.0, step=50.0)
        packet_loss_selector.is_variable.get_widget().setChecked(True)
        layout.addWidget(packet_loss_selector)
        rtt_selector = TestDataSelector("RTT [ms]", min=0.0, max=100.0, step=50.0)
        rtt_selector.is_variable.get_widget().setChecked(True)
        layout.addWidget(rtt_selector)
        reorder_selector = TestDataSelector("Reorder [%]", min=0.0, max=100.0, step=10.0)
        layout.addWidget(reorder_selector)
        self.selector_controller = TestDataSelectorController(max_non_const=1, selectors=[packet_loss_selector, rtt_selector, reorder_selector])
        
        self.start_button = QPushButton()
        self.start_button.setText("Start tests")
        layout.addWidget(self.start_button)
        def on_test_started():
            self.status_text.setText("Running tests...")
            self.show_button.setEnabled(False)
        def on_test_finished(results):
            self.results = results
            self.status_text.setText("Tests finished")
            self.show_button.setEnabled(True)
        def start_button_listener():
            if self.file_mode() == "audio": 
                on_test_started()
                threading.Thread(target=tests.perform_tests_audio, args=(AUDIO_FILE, on_test_finished, packet_loss_selector, rtt_selector, reorder_selector)).start()
            elif self.file_mode() == "video":        
                on_test_started()
                threading.Thread(target=tests.perform_tests_video, args=(VIDEO_FILE, on_test_finished, packet_loss_selector, rtt_selector, reorder_selector)).start() 
            else:
                print("Unsupported file type")       
        self.start_button.clicked.connect(start_button_listener)
        
        self.show_button = QPushButton()
        self.show_button.setText("Show graph")
        self.show_button.setEnabled(False)
        layout.addWidget(self.show_button)
        self.show_button.clicked.connect(self.show_graph)
        
        self.status_text = QLabel()
        layout.addWidget(self.status_text)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    @pyqtSlot()
    def open_in_file_dialog(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "${HOME}", "Audio Files (*.wav)")
        if fname[0] is not None:
            self.in_file_name = fname
            self.in_file_name_label.setText(fname[0])
    
    def file_mode(self):
        if self.in_file_name.endswith(".wav"):
            return "audio"
        elif self.in_file_name.endswith(".mp4"):
            return "video"
        else:
            return None
    
    def show_graph(self):
        if self.file_mode() == "audio":
            self.show_graph_audio()
        elif self.file_mode() == "video":
            self.show_graph_video()
        else:
            print("Unsupported file type")
            
    def show_graph_audio(self):
        results = self.results
        # for i in results.items():
        #     print(i)
        
        # Convert from frozensets to dictionaries
        results = [(dict(k), v) for k, v in results.items()]
        
        # Get only the variable parameter names
        x_keys = [x.name for x in self.selector_controller.get_variables()]
        
        #
        # Convert from, for example:
        # {('Packet loss', 0.0), ('RTT', 50.0), ('Reorder', 0.0)}: {'pesq': 0, 'p.563': 0}
        #         ^ variable       ^ variable       ^ const
        # To:
        # [0.0, 50.0, {'pesq': 0, 'p.563': 0}]
        data = []
        for measurement in results:
            entry = []
            for key in x_keys:
                entry.append(measurement[0][key])
            entry.append(measurement[1])
            data.append(entry)             
                    
        # Get constant values to include in the title
        consts = [c.name for c in self.selector_controller.get_constants()]
        const_values = [results[0][0][name] for name in consts]
        consts = list(zip(consts, const_values))
        title = "Test results" + str(consts)
        # Convert from results to series of data:
        # [0.0, 50.0, {'pesq': 1, 'p.563': 2}]
        # To:
        # {'pesq': [0.0, 50.0, 1], 'p.563': [0.0, 50.0, 2]}
        y_series_names = list(data[0][len(x_keys)].keys())
        y_series = {name: [] for name in y_series_names}
        for data_entry in data:
            for series_name in y_series_names:
                value = data_entry[len(x_keys)][series_name]
                series_entry = data_entry[:len(x_keys)]
                series_entry.append(value)
                y_series[series_name].append(series_entry)

        # Plot the data
        if len(x_keys) == 1: # 1D plot
            for key, entry in y_series.items():
                x_values = [x[0] for x in entry]
                y_values = [x[1] for x in entry]
                xy_pairs = list(zip(x_values, y_values))
                xy_pairs.sort(key=lambda x: x[0])
                x_values, y_values = zip(*xy_pairs)
                plt.plot(x_values, y_values, label=str(key))
            plt.title(title)
            plt.x_label = x_keys[0]
            plt.y_label = "MOS"
            plt.ylim(-0.5, 5.5)
            plt.legend()
        elif len(x_keys) == 2: # 2D plot
            fig = plt.figure()
            ax = plt.axes(projection='3d')
            for key, entry in y_series.items():
                x_values = [x[0] for x in entry]
                y_values = [x[1] for x in entry]
                z_values = [x[2] for x in entry]
                ax.plot_trisurf(x_values, y_values, z_values, label=str(key))
            ax.set_title(title)
            ax.set_xlabel(x_keys[0])
            ax.set_ylabel(x_keys[1])
            ax.set_zlabel("MOS")
            ax.set_zlim(-0.5, 5.5)
            ax.legend()
        plt.show()
    
    def show_graph_video(self):
        results = self.results
        # for i in results.items():
        #     print(i)
        
        # Convert from frozensets to dictionaries
        results = [(dict(k), v) for k, v in results.items()]
        
        # Get only the variable parameter names
        x_keys = [x.name for x in self.selector_controller.get_variables()]
        
        #
        # Convert from, for example:
        # {('Packet loss', 0.0), ('RTT', 50.0), ('Reorder', 0.0)}: {'pesq': 0, 'p.563': 0}
        #         ^ variable       ^ variable       ^ const
        # To:
        # [0.0, 50.0, {'pesq': 0, 'p.563': 0}]
        data = []
        for measurement in results:
            entry = []
            for key in x_keys:
                entry.append(measurement[0][key])
            entry.append(measurement[1])
            data.append(entry)             
                    
        # Get constant values to include in the title
        consts = [c.name for c in self.selector_controller.get_constants()]
        const_values = [results[0][0][name] for name in consts]
        consts = list(zip(consts, const_values))
        title = "Test results" + str(consts)
        # Convert from results to series of data:
        # [0.0, 50.0, {'pesq': 1, 'p.563': 2}]
        # To:
        # {'pesq': [0.0, 50.0, 1], 'p.563': [0.0, 50.0, 2]}
        y_series_names = list(data[0][len(x_keys)].keys())
        y_series = {name: [] for name in y_series_names}
        for data_entry in data:
            for series_name in y_series_names:
                value = data_entry[len(x_keys)][series_name]
                series_entry = data_entry[:len(x_keys)]
                series_entry.append(value)
                y_series[series_name].append(series_entry)

        # Plot the data
        if len(x_keys) == 1: # 1D plot
            for key, entry in y_series.items():
                x_values = [x[0] for x in entry]
                y_values = [x[1] for x in entry]
                xy_pairs = list(zip(x_values, y_values))
                xy_pairs.sort(key=lambda x: x[0])
                x_values, y_values = zip(*xy_pairs)
                plt.plot(x_values, y_values, label=str(key))
                plt.title(title)
                plt.x_label = x_keys[0]
                plt.y_label = "Value"
                plt.legend()
                plt.show()
        elif len(x_keys) == 2: # 2D plot
            for key, entry in y_series.items():
                fig = plt.figure()
                ax = plt.axes(projection='3d')
                x_values = [x[0] for x in entry]
                y_values = [x[1] for x in entry]
                z_values = [x[2] for x in entry]
                ax.plot_trisurf(x_values, y_values, z_values, label=str(key))
                ax.set_title(title)
                ax.set_xlabel(x_keys[0])
                ax.set_ylabel(x_keys[1])
                ax.set_zlabel("Value")
                ax.legend()
                plt.show()

def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()