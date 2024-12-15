#!/usr/bin/env python3
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QMainWindow, QVBoxLayout, QDoubleSpinBox, QLabel, QHBoxLayout, QCheckBox
from PyQt6.QtCore import pyqtSlot
import sys
import tests

AUDIO_FILE="ENG_M.wav"
VIDEO_FILE=""

class TestDataSelector(QWidget):
    def __init__(self, name: str):
        super(TestDataSelector, self).__init__()
        layoutV = QVBoxLayout()
        layoutH = QHBoxLayout()
        
        title = QLabel()
        title.setText(name)
        layoutV.addWidget(title)
        
        self.should_change_checkbox = QCheckBox()
        self.should_change_checkbox.setChecked(False)
        layoutH.addWidget(self.should_change_checkbox)
        
        self.start_value = QDoubleSpinBox()
        self.start_value.setValue(0.0)
        self.start_value.setEnabled(True)
        start_label = QLabel()
        start_label.setText("Initial value")
        layoutH.addWidget(start_label)
        layoutH.addWidget(self.start_value)
        
        self.end_value = QDoubleSpinBox()
        self.end_value.setMaximum(100.)
        self.end_value.setValue(100.0)
        self.end_value.setEnabled(False)
        end_label = QLabel()
        end_label.setText("Final value")
        layoutH.addWidget(end_label)
        layoutH.addWidget(self.end_value)
        
        self.step_value = QDoubleSpinBox()
        self.step_value.setValue(10.0)
        self.step_value.setEnabled(False)
        step_label = QLabel()
        step_label.setText("Step")
        layoutH.addWidget(step_label)
        layoutH.addWidget(self.step_value)

        def checkbox_listener(checkbox_state):
            self.end_value.setEnabled(checkbox_state)
            self.step_value.setEnabled(checkbox_state)
        self.should_change_checkbox.stateChanged.connect(checkbox_listener)

        layoutV.addLayout(layoutH)
        self.setLayout(layoutV)
        
        self.value = self.start_value.value()
    

    def __iter__(self):
        return iter([x/100.0 for x in range(int(self.start_value.value()*100), int(self.end_value.value()*100+1), int(self.step_value.value()*100))])
    

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        in_file_button = QPushButton()
        in_file_button.setText("Select input file...")
        in_file_button.clicked.connect(self.open_in_file_dialog)
        layout.addWidget(in_file_button)
        
        packet_loss_selector = TestDataSelector("Packet loss")
        layout.addWidget(packet_loss_selector)
        
        start_button = QPushButton()
        start_button.setText("Start tests")
        def start_button_listener():
            print("Starting tests")
            tests.perform_tests(packet_loss_selector)
            
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