class NgSpiceSim:
    def __init__(self, circuit_name, netlist, output_variables):
        self.circuit_name = circuit_name
        self.netlist = netlist
        self.output_variables = output_variables
        self.analysis_commands = []  # Store analysis commands
        self.output_file = 'sim_data.txt'
        self.log_file = 'sim_output.log'
        self.cir_file = f'{circuit_name}.cir'
        self.data = None

    def add_op_analysis(self):
        self.analysis_commands.append('op')

    def add_tran_analysis(self, tstep, tstop):
        self.analysis_commands.append(f"tran {tstep} {tstop}")

    def add_ac_analysis(self, type_of_sweep, points, fstart, fstop):
        # type_of_sweep: DEC, LIN, OCT
        self.analysis_commands.append(f"ac {type_of_sweep} {points} {fstart} {fstop}")

    def add_dc_analysis(self, source, start, stop, step):
        self.analysis_commands.append(f"dc {source} {start} {stop} {step}")

    def build_controls(self):
        analysis = "\n".join(self.analysis_commands)
        controls = f"""
.{analysis}
.control
run
wrdata {self.output_file} {' '.join(self.output_variables)}
quit
.endc
"""
        return controls

    def write_circuit(self):
        cir_txt = f"""
* {self.circuit_name}
{self.netlist}
{self.build_controls()}
.end
"""
        with open(self.cir_file, 'w') as f:
            f.write(cir_txt)

    def run_simulation(self):
        self.write_circuit()
        subprocess.run(['ngspice', '-b', '-o', self.log_file, self.cir_file])

    def load_results(self):
        self.data = np.loadtxt(self.output_file, skiprows=1)
        self.results = {var: self.data[:, idx] for idx, var in enumerate(self.output_variables)}
        return self.results



# Define netlist
netlist = """
V1 in 0 AC 1
R1 in out 1k
C1 out 0 1uF
"""

# Outputs
outputs = ['frequency', 'v(out)', 'v(in)']

# Create simulator
sim = NgSpiceSim(circuit_name="RC_Bode", netlist=netlist, output_variables=outputs)

# Add an AC sweep analysis
sim.add_ac_analysis('DEC', 100, '1', '10Meg')

# Run it
sim.run_simulation()

# Load results
results = sim.load_results()

# Plot
import matplotlib.pyplot as plt
plt.semilogx(results['frequency'], 20*np.log10(np.abs(results['v(out)'])), label='V(out)')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude [dB]')
plt.grid(True, which="both")
plt.title('RC Circuit Frequency Response')
plt.legend()
plt.show()













