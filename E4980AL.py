import pyvisa


class E4980AL(object):

    def __init__(self, resource_name='GPIB0::17::INSTR'):
        self.inst = self.connect_gpib(resource_name)

    def connect_gpib(resource_name='GPIB0::17::INSTR'):
        # Connect to GPIB, reutrns instrument object
        rm = pyvisa.ResourceManager()
        rm.list_resources()
        inst = rm.open_resource(resource_name)

        print('connected to: ' + inst.query('*IDN?'))

        return inst

    def set_meas_type(self, meas_type='RX'):
        # Set measurement type
        self.inst.write('CORR:LOAD:TYPE ' + meas_type)

   