import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys
import os
import tempfile
import numpy as np
import time
from pymeasure.instruments.agilent import AgilentE4980
from pymeasure.log import console_log
from pymeasure.display.Qt import QtWidgets
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Procedure, Results, Metadata
from pymeasure.experiment import BooleanParameter, IntegerParameter, FloatParameter, Parameter

class E4980ALProcedure(Procedure):

    instrument = Parameter('Instrument Address', default='GPIB::17::INSTR')
    ac_voltage = FloatParameter('AC Voltage', units='V', default=0.022)
    mode = Parameter('Mode', default='RX')
    meas_time = Parameter('Measurement Time', default='SHORT')
    points = IntegerParameter('Number of Points', default=20)
    average = IntegerParameter('Number of Averages', default=1)
    start_frequency = IntegerParameter('Start Frequency',units='Hz', default=100)
    stop_frequency = IntegerParameter('Stop Frequency', units='Hz', default=100000)
    logspace = BooleanParameter('Logarithmic Sweep', default=True)
    reverse = BooleanParameter('Reverse Sweep', default=True)
    wait = FloatParameter('Wait Time', units='s', default=0.1)
    filepath = Parameter('File Path', default='./data/')
    duration = FloatParameter('Duration', units='s', default=20)


    DATA_COLUMNS = ['Data Count', 'Time', 'Frequency', 'Z\'', 'Z\"']

    def startup(self):
        log.info("Connecting to the instrument")
        self.instrument = AgilentE4980(self.instrument)
        self.instrument.reset()
        self.instrument.ac_voltage = self.ac_voltage
        self.instrument.mode = self.mode
        self.instrument.aperture(self.meas_time,averages=self.average)

    def execute(self):
        log.info("Starting measurement")
        if self.logspace:
            frequencies = np.round(np.logspace(np.log10(self.start_frequency), np.log10(self.stop_frequency), num=self.points))
        else:
            frequencies = np.round(np.linspace(self.start_frequency, self.stop_frequency, self.points))
        
        if self.reverse:
            frequencies = frequencies[::-1]
        start_time=time.time()
        data_count=0
        while time.time()-start_time < self.duration:  # Change the loop to run indefinitely until stopped by the user
            results=self.instrument.freq_sweep(frequencies)
            time_elapsed=time.time()-start_time
            for i in range(len(frequencies)):
                data={'Data Count': data_count,
                    'Time': time_elapsed,
                    'Frequency':frequencies[i],
                    'Z\'': results[0][i],
                    'Z\"': results[1][i]}
                data_count+=1
                self.emit('results', data)
                if self.should_stop():
                    # save the data

                    log.warning("Caught the stop flag in the procedure")
                    
                    break
            
class MainWindow(ManagedWindow):

    def __init__(self):
        super().__init__(
            procedure_class=E4980ALProcedure,
            inputs=['instrument', 'ac_voltage', 'mode', 'meas_time', 'points', 'average', 'start_frequency', 'stop_frequency','logspace', 'reverse', 'wait', 'duration', 'filepath'],
            displays=['instrument', 'ac_voltage', 'mode', 'meas_time', 'points', 'average', 'start_frequency', 'stop_frequency', 'logspace', 'reverse', 'wait', 'duration', 'filepath'],

            x_axis='Data Count',
            y_axis='Z\''
        )
        self.setWindowTitle('E4980AL Measurement')
        

    def queue(self):
        filename = time.strftime("%Y%m%d-%H%M%S") + '.csv'

        procedure = self.make_procedure()
        # make filepath if it doesn't exist
        if not os.path.exists(procedure.filepath):
            os.makedirs(procedure.filepath)

        if procedure.filepath[-1] != '/':
            procedure.filepath += '/'

        results = Results(procedure, procedure.filepath+filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())