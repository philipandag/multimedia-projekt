#!/usr/bin/env python3
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMainWindow, QVBoxLayout
from PyQt6.QtCore import pyqtSlot
import sys
import tests
from test_data_selector import TestDataSelector, TestDataSelectorController

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
        
        packet_loss_selector = TestDataSelector("Packet loss", min=0.0, max=100.0, step=10.0)
        layout.addWidget(packet_loss_selector)
        rtt_selector = TestDataSelector("RTT", min=0.0, max=100.0, step=10.0)
        layout.addWidget(rtt_selector)
        reorder_selector = TestDataSelector("Reorder", min=0.0, max=100.0, step=10.0)
        layout.addWidget(reorder_selector)
        self.selector_controller = TestDataSelectorController(max_non_const=1, selectors=[packet_loss_selector, rtt_selector, reorder_selector])
        
        start_button = QPushButton()
        start_button.setText("Start tests")
        def start_button_listener():
            results = tests.perform_tests(packet_loss_selector, rtt_selector, reorder_selector)
            for r in results:
                print(r)
            
        start_button.clicked.connect(start_button_listener)
        layout.addWidget(start_button)
        
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    @pyqtSlot()
    def open_in_file_dialog(self):
        fname = QFileDialog.getOpenFileName(self, "Open File", "${HOME}", "Audio Files (*.wav)")
        print(fname)
        if fname[0] is not None:
            self.in_file_name = fname

def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()