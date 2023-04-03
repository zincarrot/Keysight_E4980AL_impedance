import numpy as np
import time
from pymeasure.experiment.experiment import Experiment
from pymeasure.instruments.agilent import AgilentE4980
from E4980AL import E4980ALProcedure
import numpy as np
from matplotlib import pyplot as plt

#%% configuration
e4980a = AgilentE4980("GPIB0::17::INSTR")
e4980a.ac_voltage = 0.022
e4980a.mode = "RX"
e4980a.aperture('short', averages=1)

datafile='test.csv'
sweep_type='LIN'
start_freq=20
stop_freq=100000
sweep_reverse=True
num_points=15

if sweep_type=='LIN':
    frequencies = np.linspace(start_freq, stop_freq, num_points)
elif sweep_type=='LOG':
    frequencies = np.logspace(np.log10(start_freq), np.log10(stop_freq), num_points)
if sweep_reverse:
    frequencies = frequencies[::-1]


title="E4980AL Test"
procedure = E4980ALProcedure()
experiment = Experiment(title, procedure)
experiment.start()
for i in range(100):
    # sleep
    time.sleep(0.1)
    # get data

