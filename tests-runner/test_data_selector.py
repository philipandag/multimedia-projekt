from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QDoubleSpinBox, QLabel, QHBoxLayout

class LabeledField(QWidget):
    def __init__(self, label: str, widget: QWidget):
        super(LabeledField, self).__init__()
        layout = QHBoxLayout()
        self.label = QLabel()
        self.label.setText(label)
        layout.addWidget(self.label)
        
        self.widget = widget
        layout.addWidget(self.widget)
        self.setLayout(layout)
    
    def get_widget(self):
        return self.widget
    def get_label(self):
        return self.label
    def setEnabled(self, a0):
        self.label.setEnabled(a0)
        self.widget.setEnabled(a0)
        return super().setEnabled(a0)

class TestDataSelector(QWidget):
    """
    Widget to select a range of values to test
    """
    def __init__(self, name: str, min: float = 0.0, max: float = 100.0, step: float = 10.0):
        super(TestDataSelector, self).__init__()
        layoutV = QVBoxLayout()
        layoutH = QHBoxLayout()
        
        title = QLabel()
        title.setText(name)
        self.name = name
        layoutV.addWidget(title)
        
        self.is_variable = QCheckBox()
        self.is_variable.setChecked(False)
        self.is_variable = LabeledField("Is Variable:", self.is_variable)
        layoutH.addWidget(self.is_variable)
        
        self.start_value = QDoubleSpinBox()
        self.start_value.setMinimum(min)
        self.start_value.setMaximum(max)
        self.start_value.setValue(min)
        self.start_value.setEnabled(True)
        self.start_value = LabeledField("Initial value:", self.start_value)
        layoutH.addWidget(self.start_value)
        
        self.end_value = QDoubleSpinBox()
        self.end_value.setMinimum(min)
        self.end_value.setMaximum(max)
        self.end_value.setValue(max)
        self.end_value.setEnabled(False)
        self.end_value = LabeledField("Final value:", self.end_value)
        layoutH.addWidget(self.end_value)
        
        self.step_value = QDoubleSpinBox()
        self.step_value.setMinimum(min)
        self.step_value.setMaximum(max)
        self.step_value.setValue(step)
        self.step_value.setEnabled(False)
        self.step_value = LabeledField("Step value:", self.step_value)
        layoutH.addWidget(self.step_value)

        def checkbox_listener(checkbox_state):
            self.end_value.setEnabled(checkbox_state)
            self.step_value.setEnabled(checkbox_state)
                
        self.is_variable.get_widget().stateChanged.connect(checkbox_listener)

        layoutV.addLayout(layoutH)
        self.setLayout(layoutV)
        
        self.value = self.start_value.get_widget().value()
           
    
    def set_controller(self, controller):
        self.controller = controller
    
    def __iter__(self):
        if self.is_variable.get_widget().isChecked():
            return iter([x/100.0 for x in range(int(self.start_value.get_widget().value()*100), int(self.end_value.get_widget().value()*100+1), int(self.step_value.get_widget().value()*100))])
        else:
            return iter([self.start_value.get_widget().value()])
    
class TestDataSelectorController:
    def __init__(self, max_non_const: int = 1, selectors: list = []):
        self.max_non_const = max_non_const
        self.selectors = []
        self.variable_count: int = 0
        for s in selectors:
            self.add_selector(s)
            s.is_variable.get_widget().stateChanged.connect(self.selector_changes_to)
    
    def add_selector(self, selector: TestDataSelector):
        selector.set_controller(self)
        self.selectors.append(selector)
    
    def selector_changes_to(self, new_state):
        print(new_state)
        if new_state != 0:
            if self.variable_count < self.max_non_const:
                self.variable_count += 1
                # Disable selecting any more selectors when the maximum non-constant values is reached
                if self.variable_count == self.max_non_const:
                    for s in self.selectors:
                        if not s.is_variable.get_widget().isChecked():
                            s.is_variable.setEnabled(False)
        elif new_state == 0:
            if self.variable_count > 0:
                self.variable_count -= 1
                for s in self.selectors:
                    s.is_variable.setEnabled(True)   
    
    def get_variables(self):
        return [s for s in self.selectors if s.is_variable.get_widget().isChecked()]
    def get_constants(self):
        return [s for s in self.selectors if not s.is_variable.get_widget().isChecked()]