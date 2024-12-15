#!/usr/bin/env python3
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMainWindow, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSlot
import sys
import tests
from test_data_selector import TestDataSelector, TestDataSelectorController
import threading

AUDIO_FILE="ENG_M.wav"
VIDEO_FILE=""
        
class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        in_file_button = QPushButton()
        in_file_button.setText("Select input file...")
        in_file_button.clicked.connect(self.open_in_file_dialog)
        layout.addWidget(in_file_button)
        
        packet_loss_selector = TestDataSelector("Packet loss", min=0.0, max=100.0, step=50.0)
        packet_loss_selector.is_variable.get_widget().setChecked(True)
        layout.addWidget(packet_loss_selector)
        rtt_selector = TestDataSelector("RTT", min=0.0, max=100.0, step=10.0)
        layout.addWidget(rtt_selector)
        reorder_selector = TestDataSelector("Reorder", min=0.0, max=100.0, step=10.0)
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
            on_test_started()
            threading.Thread(target=tests.perform_tests, args=(on_test_finished, packet_loss_selector, rtt_selector, reorder_selector)).start()        
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
            
    def show_graph(self):
        results = self.results
        
        x_keys = [x.name for x in self.selector_controller.get_variables()][:1] # TODO change to allow more than one variable
        x_values = [value for fset in results for key, value in fset  for x_key in x_keys if key == x_key]
        consts = [c.name for c in self.selector_controller.get_constants()]
        const_values = [value for fset in results for key, value in fset if key in consts]
        consts = list(zip(consts, const_values))

        plt.title("Test results" + str(consts))
        
        # Create a dictionary with the y values for each key
        # Originally the results have a list of dictionaries with the key-value pairs of {evaluation-mode: value}
        # for every measurement, we want to have a list of values for each evaluation mode to plot them in the same graph
        y_series = {}
        for d in list(results.values()):
            for key, value in d.items():
                if key not in y_series:
                    y_series[key] = []
                y_series[key].append(value)

        # The X values are not sorted, but are corresponding to the Y values
        for key, y_values in y_series.items():
            plot_data = sorted(zip(x_values, y_values))
            x_values, y_values = zip(*plot_data)
            plt.plot(x_values, y_values, label=str(key))
        plt.x_label = x_keys[0]
        plt.y_label = "MOS"
        plt.ylim(-0.5, 5.5)
        plt.legend()
        plt.show()

def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()