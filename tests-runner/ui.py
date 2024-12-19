#!/usr/bin/env python3
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMainWindow, QVBoxLayout, QLabel, QListView
from PyQt6.QtCore import pyqtSlot, QStringListModel
import sys
import tests
from test_data_selector import TestDataSelector, TestDataSelectorController, ResultItem
import threading
import numpy as np
import os
import uuid


SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIR=os.path.join(SCRIPT_DIR, "resources")
AUDIO_FILE=os.path.join(RESOURCES_DIR, "ENG_M.wav")
VIDEO_FILE=os.path.join(RESOURCES_DIR, "shrek_shortest.mp4")
        
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        in_file_button = QPushButton()
        in_file_button.setText("Select input file...")
        in_file_button.clicked.connect(self.open_in_file_dialog)
        self.in_file_name_label = QLabel()
        self.in_file_name = str(VIDEO_FILE)
        self.in_file_name_label.setText(self.in_file_name)
        layout.addWidget(self.in_file_name_label)
        layout.addWidget(in_file_button)
        
        self.packet_loss_selector = TestDataSelector("Packet loss [%]", min=0.0, max=100.0, step=50.0)
        self.packet_loss_selector.is_variable.get_widget().setChecked(True)
        layout.addWidget(self.packet_loss_selector)
        self.rtt_selector = TestDataSelector("RTT [ms]", min=0.0, max=100.0, step=50.0)
        self.rtt_selector.is_variable.get_widget().setChecked(True)
        layout.addWidget(self.rtt_selector)
        self.reorder_selector = TestDataSelector("Reorder [%]", min=0.0, max=100.0, step=10.0)
        layout.addWidget(self.reorder_selector)
        self.selector_controller = TestDataSelectorController(max_non_const=1, selectors=[self.packet_loss_selector, self.rtt_selector, self.reorder_selector])
        
        self.start_button = QPushButton()
        self.start_button.setText("Start tests")
        layout.addWidget(self.start_button)    
        
        self.start_button.clicked.connect(self.start_button_listener)
        
        # self.show_button = QPushButton()
        # self.show_button.setText("Show graph")
        # self.show_button.setEnabled(False)
        # layout.addWidget(self.show_button)
        # self.show_button.clicked.connect(self.show_graph)
        
        
        self.tests = {}
        self.results = {}
        self.tests_constants = {}
        self.tests_variables = {}
        self.tests_types = {}
        self.results_list = QVBoxLayout()
        layout.addLayout(self.results_list)
        
        self.status_text = QLabel()
        layout.addWidget(self.status_text)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def get_test_parameters(self):
        return {
            self.packet_loss_selector.name: list(self.packet_loss_selector),
            self.rtt_selector.name: list(self.rtt_selector),
            self.reorder_selector.name: list(self.reorder_selector)
        }
        
    def start_button_listener(self):
        test_id = str(uuid.uuid4())
        parameters = self.get_test_parameters()
        file_mode = self.file_mode()
        self.tests[test_id] = parameters
        self.tests_constants[test_id] = self.selector_controller.get_constants().copy()
        self.tests_variables[test_id] = self.selector_controller.get_variables().copy()
        self.tests_types[test_id] = file_mode

        
        def on_test_started():
            self.status_text.setText("Running tests...")
            # self.show_button.setEnabled(False)
            
        def on_test_finished(results):
            self.results[test_id] = results
            self.status_text.setText("Tests finished")
            if len(results) < 1:
                print("No results")
                return
            self.results_list.addWidget(ResultItem(str(parameters), self.show_graph, self, test_id))
            # self.show_button.setEnabled(True)
        
        if file_mode is None:
            print("Unsupported file type")
            return
        
        on_test_started()
        self.tests[test_id] = str(parameters)
        threading.Thread(target=tests.perform_tests, args=(test_id, self.in_file_name, on_test_finished, parameters, file_mode)).start()  
    
    @pyqtSlot()
    def open_in_file_dialog(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "${HOME}", "WAV/MP4 (*.wav *.mp4)")
        if fname[0] is not None:
            self.in_file_name = fname[0]
            self.in_file_name_label.setText(fname[0])
    
    def file_mode(self):
        if self.in_file_name.endswith(".wav"):
            return "audio"
        elif self.in_file_name.endswith(".mp4"):
            return "video"
        else:
            return None
    
    def show_graph(self, test_id): #TODO None
        mode = self.tests_types[test_id]
        if mode == "audio":
            self.show_graph_audio(test_id)
        elif mode == "video":
            self.show_graph_video(test_id)
        else:
            print("Unsupported file type")
    
    def get_results(self, test_id):
        return self.tests[test_id]
            
    def show_graph_audio(self, test_id):
        results = self.results[test_id] # first test, [0]
        
        # for i in results.items():
        #     print(i)
        
        # Convert from frozensets to dictionaries
        results = [(dict(k), v) for k, v in results.items()]
        
        # Get only the variable parameter names
        #x_keys = [x.name for x in self.selector_controller.get_variables()]
        x_keys = [x.name for x in self.tests_variables[test_id]]
        
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
        consts = [c.name for c in self.tests_constants[test_id]]
        #consts = [c.name for c in self.selector_controller.get_constants()]
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
    
    def show_graph_video(self, test_id):
        results = self.results[test_id]
        
        # Convert from frozensets to dictionaries
        results = [(dict(k), v) for k, v in results.items()]
        
        # Get only the variable parameter names
        #x_keys = [x.name for x in self.selector_controller.get_variables()]
        x_keys = [x.name for x in self.tests_variables[test_id]]
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
        #consts = [c.name for c in self.selector_controller.get_constants()]
        consts = [c.name for c in self.tests_constants[test_id]]
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