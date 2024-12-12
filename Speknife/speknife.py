######################################################################################################
#Author: Matheus Rebello do Nascimento
#Collaborators: Luis Fernando de Oliveira, José Guilherme Pereira Peixoto
#Speknife project
######################################################################################################
import managing_files as mfiles
import detection_physics as det_phys
import statistical_analysis as stat_analy
import ploting as plot
import os

#Function to read the configuration file
def read_config(file_path, cfg):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('#'): #Ignorim first line of a file if it has a #
                continue
            line = line.strip().split()
            if len(line) > 0:
                key = line[0]
                value = line[1]
                if key in ['reference_path','base_name','reference_name']:
                    cfg[key] = value
                elif key in ['a', 'a_uncertainty', 'b', 'b_uncertainty', 'r_pearson']:
                    cfg[key] = float(value)
                elif key in ['channel_number', 'plot_type', 'normalization_number','tube_voltage','shift']:
                    cfg[key] = int(value)
                elif key in ['plot', 'save_plot', 'mca','uncertainty_analysis','tube_voltage_plot','tube_voltage_measurement','other_database']:
                    if value == 'True':
                        cfg[key] = True
                    elif value == 'False':
                        cfg[key] = False
                else:
                    if key[0] != '#':
                        print("Parâmetro não reconhecido!!!")
                        print("\t", line)

config = {'a_uncertainty': 0,'b_uncertainty' : 0,'r_pearson': 0,'plot' : False,'plot_type' : None,'normalization_number' : 0,'save_plot' : True,'mca' : False, 'tube_voltage_plot':False, 'tube_voltage_measurement':False,'other_database':False,'reference_path':None,'base_name':None,'reference_name': 'Reference quality','shift':0,'uncertainty_analysis':False}
config_mandatory = {'a' : '','b' : '','tube_voltage' : '','channel_number' : ''} 

#Reading the basic data from the configuration file
read_config('input.txt',config)
read_config('input.txt',config_mandatory)

#Check for correct values passed to the mandatory variables
for key in config_mandatory:
   if isinstance(config_mandatory[key], str) and not config_mandatory[key]:
        print("Mandatory parameter not initialized!!!")
        print(key)
        exit()

arquivos = os.listdir('working_area/')

for arquivo in arquivos:
    if  not arquivo.endswith("_corrected.txt") and not arquivo.startswith("repository"):
        caminho_arquivo = os.path.join('working_area/', arquivo)
        print('\n')
        print(f"Reading file: {arquivo}")

        spectrum_quality = arquivo  
        if config['mca'] == True:
            raw_data = mfiles.reading_spectrum_file(caminho_arquivo, config['mca'])
        else:
            energy , raw_data = mfiles.reading_spectrum_file(caminho_arquivo, config['mca'])

        #criating energy list
        energy = []
        for i in range(config_mandatory['channel_number']):
            energy.append(round(config_mandatory['a']*i+config_mandatory['b'],5)) #5 casas decimais para não exagerar

        ######################################################################################################
        # Stripping procedure
        #######################################################################################################
        
        #lists to be used
        corrected_data = raw_data.copy() #passing the values of the raw data to the correted one
        escape_corre =[0]*config_mandatory['channel_number'] #to be filled during the corretctions
        corre_compton = [0]*config_mandatory['channel_number'] 
        corre_effic = [0]*config_mandatory['channel_number'] 
        data_uncertainty = [0]*config_mandatory['channel_number']
        energy_uncertainty = [0]*config_mandatory['channel_number']

        #uncertainty of the raw espectra
        if config['uncertainty_analysis'] == True:
            energy_uncertainty, data_uncertainty = stat_analy.spectra_uncertainty(energy, energy_uncertainty, corrected_data, data_uncertainty, config['r_pearson'], config['a_uncertainty'], config['b_uncertainty'])
            print('You choose to evaluate the uncertainty \n')
            print('Processing it... \n')
        else:
            print('You choose to not evaluate the uncertainty \n')
            print('Processing it... \n')

        for i in range(len(energy)-1,-1,-1): #correcting in a reverse loop

            if (energy[i]>config_mandatory['tube_voltage']+2): #cutting off all counts with tube voltage+2 keV (to prevent pile up distortion in photoeletric corretction)
                corrected_data[i] = 0
                data_uncertainty[i] = 0
            else:

        #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
        #Escape correction --> Compton corretion --> Efficiency correction
        #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
                det_phys.escape_correction(i,energy[i], corrected_data,config_mandatory['tube_voltage'],raw_data,config_mandatory['a'],config_mandatory['b'],escape_corre,data_uncertainty)
                det_phys.compton_correction(i,energy[i],corrected_data,config_mandatory['a'],config_mandatory['b'],corre_compton,data_uncertainty, energy_uncertainty, config['a_uncertainty'], config['b_uncertainty'])
                det_phys.efficiency_correction(i, energy, corrected_data, corre_effic, data_uncertainty)

        #Analysing the spectrum by the end to the beginning and cutting off all counts after the first channel with negative values
        for i in range(config_mandatory['channel_number']-1,-1,-1):
            if (energy[i]<config_mandatory['tube_voltage']+2): #energy upper limit of tube voltage+2 keV
                if (corrected_data[i]<0):
                    for j in range(i,0,-1): # seting 0 for all counts before that channel i
                        corrected_data[j] = 0
                        data_uncertainty[j] = 0
                    break 
            else:
                continue

        #User output control
        if config['uncertainty_analysis'] == True:
            print('Experimental mean energy is {} keV'.format(round(stat_analy.mean_energy(raw_data,energy),5)))
            print('Corrected mean energy is {} keV with an uncertainty of {}'.format(round(stat_analy.mean_energy(corrected_data,energy),5),round(stat_analy.mean_energy_uncertainty(corrected_data, data_uncertainty, energy, energy_uncertainty),5)))

        else:
            print('Experimental mean energy is {} keV'.format(round(stat_analy.mean_energy(raw_data,energy),5)))
            print('Corrected mean energy is {} keV '.format(round(stat_analy.mean_energy(corrected_data,energy),5)))            

        #Tube voltage
        if config['tube_voltage_measurement'] == True:
            if config['uncertainty_analysis'] == True:
                tube_kv, tube_kv_uncertainty, r_pearson_peso =stat_analy.tube_kv(config['uncertainty_analysis'],config_mandatory['a'], config_mandatory['b'], config_mandatory['tube_voltage'], energy,energy_uncertainty, corrected_data, data_uncertainty,spectrum_quality,config['save_plot'],config['tube_voltage_plot'],config['shift'])
                print("The voltage is "+str(round(tube_kv,4))+ " kV with a uncertainty of "+ str(round(tube_kv_uncertainty,4))+ " kV")
                print('The weighted linear regress r coefficient is '+str(round(r_pearson_peso,4)))
                print('\n')
                mfiles.writing_files(energy, energy_uncertainty,raw_data,corrected_data, data_uncertainty,spectrum_quality,config_mandatory['a'], config_mandatory['b'], config_mandatory['tube_voltage'],config_mandatory['channel_number'],config['uncertainty_analysis'],config['tube_voltage_measurement'], tube_kv, r_pearson_peso ,tube_kv_uncertainty) 
            else:
                tube_kv, r_pearson =stat_analy.tube_kv(config['uncertainty_analysis'],config_mandatory['a'], config_mandatory['b'], config_mandatory['tube_voltage'], energy,energy_uncertainty, corrected_data, data_uncertainty,spectrum_quality,config['tube_voltage_plot'],config['save_plot'],config['shift'])
                print("The voltage is "+str(round(tube_kv,4))+ " kV")
                print('The weighted linear regress r coefficient is '+str(round(r_pearson,4)))
                print('\n')
                mfiles.writing_files(energy, energy_uncertainty,raw_data,corrected_data, data_uncertainty,spectrum_quality,config_mandatory['a'], config_mandatory['b'], config_mandatory['tube_voltage'],config_mandatory['channel_number'],config['uncertainty_analysis'],config['tube_voltage_measurement'],tube_kv, r_pearson)

        else:
            mfiles.writing_files(energy, energy_uncertainty,raw_data,corrected_data, data_uncertainty,spectrum_quality,config_mandatory['a'], config_mandatory['b'], config_mandatory['tube_voltage'],config_mandatory['channel_number'],config['uncertainty_analysis'],config['tube_voltage_measurement'])

        if config['plot'] == True:
            plot.spectrum_data_plot(energy, energy_uncertainty, raw_data,corrected_data,data_uncertainty,spectrum_quality, config_mandatory['tube_voltage'], config['plot_type'], config['normalization_number'],config['save_plot'], config['other_database'],config['reference_path'],config['base_name'],config['reference_name'],escape_corre,corre_effic,corre_compton)
