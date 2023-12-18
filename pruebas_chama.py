"""
The following example uses WNTR (https://wntr.readthedocs.io) with Chama to 
optimize the placement of sensors that minimizes detection time of 
contaminant in a water distribution system where the exact location of the
injection is unknown. Simulation data is created using trace simulations in WNTR.  
This data could also be generated using contaminant injection simulations 
and could be translated into other metrics (e.g. extent of 
contamination or population impacted).  Each junction is defined as a feasible
sensor location. The impact formulation is used to optimize sensor placement.
"""

import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import chama
import wntr

def get_selected_sensors(inp_file, num_sensors):
    wn = wntr.network.WaterNetworkModel(inp_file)

    tanques = [node for node in wn.nodes if wn.nodes[node].node_type == 'Tank']
    bombas = [link for link in wn.links if wn.links[link].link_type == 'Pump']
    valvulas = [link for link in wn.links if wn.links[link].link_type == 'Valve']

    nodos_criticos = tanques.copy()

    for component in bombas + valvulas:
        link = wn.get_link(component)
        start_node = link.start_node.name
        end_node = link.end_node.name
        nodos_criticos.extend([start_node, end_node])

    scenario_names = nodos_criticos
    sim = wntr.sim.EpanetSimulator(wn)
    sim.run_sim(save_hyd=True)
    wn.options.quality.parameter = 'TRACE'
    signal = pd.DataFrame()
    for inj_node in scenario_names:
        print(inj_node)
        wn.options.quality.trace_node = inj_node
        sim_results = sim.run_sim(use_hyd = True)
        trace = sim_results.node['quality']
        trace = trace.stack()
        trace = trace.reset_index()
        trace.columns = ['T', 'Node', inj_node]
        signal = signal.combine_first(trace)
    signal.to_csv('signal.csv')
    
    # Define feasible sensors using location, sample times, and detection threshold
    sensor_names = nodos_criticos
    sample_times = np.arange(0, wn.options.time.duration, wn.options.time.hydraulic_timestep)
    threshold = 20
    sensors = {}
    for location in sensor_names:
        position = chama.sensors.Stationary(location)
        detector = chama.sensors.Point(threshold, sample_times)
        stationary_pt_sensor = chama.sensors.Sensor(position, detector)
        sensors[location] = stationary_pt_sensor
    
    # Extract minimum detection time for each scenario-sensor pair
    det_times = chama.impact.extract_detection_times(signal, sensors)
    det_time_stats = chama.impact.detection_time_stats(det_times)
    min_det_time = det_time_stats[['Scenario','Sensor','Min']]
    min_det_time.rename(columns = {'Min':'Impact'}, inplace = True)
    min_det_time.loc[:, 'Impact'] = min_det_time['Impact'].astype(float)
    
    # Run sensor placement optimization to minimize detection time using 0 to 5 sensors
    #   The impact for undetected scenarios is set at 1.5x the max sample time
    #   Sensor cost is defined uniformly using a value of 1.  This means that
    #   sensor_budget is equal to the number of sensors to place
    scenario_characteristics = pd.DataFrame({'Scenario': scenario_names,
                                             'Undetected Impact': sample_times.max()*1.5})
    sensor_characteristics = pd.DataFrame({'Sensor': sensor_names,'Cost': 1})
    sensor_budget = list(range(len(nodos_criticos) + 1))
    print(sensor_budget)
    results = {}
    for n in sensor_budget:
        impactform = chama.optimize.ImpactFormulation()
        results[n] = impactform.solve(min_det_time, sensor_characteristics, 
                                      scenario_characteristics, n)
    
    # Plot objective for each sensor placement
    objective_values =[results[n]['Objective']/3600 for n in sensor_budget]
    fig, ax1 = plt.subplots()
    ax1.plot(sensor_budget, objective_values, 'b', marker='.')
    ax1.set_xlabel('Number of sensors')
    ax1.set_ylabel('Expected time to detection (hr)')
    
    # Plot selected sensors, when using 5 sensors
    n = num_sensors
    selected_sensors = results[n-1]['Sensors']
    selected_sensors.insert(0, "J269")
    wntr.graphics.plot_network(wn, node_attribute=selected_sensors, 
                               title='Selected sensors, n = f"{n}"')
    
    # Plot detection time for each scenario, when using n sensors
    assessment = results[n]['Assessment']
    assessment.set_index('Scenario', inplace=True)
    wntr.graphics.plot_network(wn, node_attribute=assessment['Impact']/3600, 
                               title='Detection time (hr), n = f"{n}"')
    return selected_sensors

# Simple test to ensure results don't change
#♣assert results[n]['Objective'] == 549535.8247422681
#assert selected_sensors == ['J219', 'J360', 'J487']