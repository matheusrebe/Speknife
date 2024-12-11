import matplotlib.pyplot as plt
import numpy as np
import managing_files as mfiles

def normalization_type(n,data_list,corrected_data_uncertainty=None):
    '''
    Define the type of normalization each plot will have. No normalization 0, normalization by the max value 1, normalization by the total counts 2
    '''
    if corrected_data_uncertainty is None:
        corrected_data_uncertainty = [0]*len(data_list)
    
    if (n==1):
        max_value = max(data_list)
        for i in range(len(data_list)):	
            data_list[i]=data_list[i]/max_value	
            corrected_data_uncertainty[i] = corrected_data_uncertainty[i]/max_value	  

    elif (n==2):
        sum = 0
        for i in range(len(data_list)):
            sum = data_list[i]+sum
        for i in range(len(data_list)):	
            data_list[i]=data_list[i]/sum	
            corrected_data_uncertainty[i] = corrected_data_uncertainty[i]/sum

    return data_list

def spectrum_data_plot(energy, energy_uncertainty, raw_data,corrected_data,data_uncertainty,spectrum_quality,tube_voltage, plot_type, normalization_number,save_plot, other_database,reference_path,base_name,reference_name,escape_corre, corre_effic,corre_compton):
    '''
    Define the type of each plot will have. Only raw data 0; comparison betewenn raw and corrected 1; only corrected data 2; uncertainty error bar plot 3; Corrected data, raw data and subtractions made by the corrections 4
    '''
    title = spectrum_quality.split('_')
    if (plot_type == 0): #only raw data
        plt.plot(energy,normalization_type(normalization_number, raw_data),label='Raw data')
        if other_database == True:
            reference_energy, reference_data=mfiles.reading_files(reference_path+base_name+str(tube_voltage)+'.txt')
            plt.plot(reference_energy,normalization_type(normalization_number, reference_data), linestyle = '-.',color ='darkgreen',label = reference_name)
        plt.xlim(0,tube_voltage+1)
        plt.ylim(bottom=0)
        plt.ylabel('Counts')
        plt.xlabel('Energy [keV]')
        plt.title(title[0], fontweight='bold')
        plt.legend(frameon=False) 
        plt.tight_layout()
        if save_plot==True:
            plt.savefig(spectrum_quality+'_raw_data.png')
        plt.show()
    elif (plot_type == 1): #comparison betewenn raw and corrected
        plt.plot(energy,normalization_type(normalization_number, raw_data), linestyle = '--',color ='orange', label = 'Raw data')
        plt.plot(energy,normalization_type(normalization_number, corrected_data),linestyle = '-',color ='royalblue', label = 'Corrected data')
        if other_database == True:
            reference_energy, reference_data=mfiles.reading_files(reference_path+base_name+str(tube_voltage)+'.txt')
            plt.plot(reference_energy,normalization_type(normalization_number, reference_data), linestyle = '-.',color ='darkgreen',label = reference_name)
        plt.xlim(0,tube_voltage+1)
        plt.ylim(bottom=0)
        plt.ylabel('Counts')
        plt.xlabel('Energy [keV]')
        plt.title(title[0], fontweight='bold')
        plt.legend(frameon=False) 
        plt.tight_layout()
        if save_plot==True:
            plt.savefig(spectrum_quality+'_corrected_raw.png')
        plt.show()
    elif (plot_type == 2): #only corrected data
        normalization_type(normalization_number, corrected_data)
        plt.plot(energy,corrected_data,linestyle = '-',color ='royalblue', label ='Corrected data')
        if other_database == True:
            reference_energy, reference_data=mfiles.reading_files(reference_path+base_name+str(tube_voltage)+'.txt')
            plt.plot(reference_energy,normalization_type(normalization_number, reference_data), linestyle = '-.',color ='darkgreen',label = reference_name)
        plt.xlim(0,tube_voltage+1)
        plt.ylim(bottom=0)
        plt.ylabel('Counts')
        plt.xlabel('Energy [keV]')
        plt.title(title[0], fontweight='bold')
        plt.legend(frameon=False)
        plt.tight_layout()
        if save_plot==True:
            plt.savefig(spectrum_quality+'_corrected.png')
        plt.show()
    elif (plot_type == 3): #uncertainty plot
        plt.errorbar(energy, normalization_type(normalization_number, corrected_data,data_uncertainty), xerr=energy_uncertainty, yerr=data_uncertainty, color='royalblue', linestyle='',linewidth=1, capsize=2, label ='Corrected data')
        if other_database == True:
            reference_energy, reference_data=mfiles.reading_files(reference_path+base_name+str(tube_voltage)+'.txt')
            plt.plot(reference_energy,normalization_type(normalization_number, reference_data), linestyle = '-.',color ='darkgreen',label = reference_name)
        plt.xlim(0,tube_voltage+1)
        plt.ylim(bottom=0)
        plt.ylabel('Counts')
        plt.xlabel('Energy [keV]')
        plt.title(title[0], fontweight='bold')
        plt.legend(frameon=False)
        plt.tight_layout()
        if save_plot==True:
            plt.savefig(spectrum_quality+'_corrected_uncertainty'+'.png')
        plt.show()
    elif (plot_type == 4): #Corrected data, raw data and subtractions made by the corrections
        plt.plot(energy,normalization_type(0, raw_data), linestyle = '--',color ='orange', label = 'Raw data')
        plt.plot(energy,corrected_data,linestyle = '-',color ='royalblue', label = 'Corrected data')
        plt.plot(energy,escape_corre, linestyle = '-.',color ='darkgreen',label = 'Escape correction')
        plt.plot(energy, corre_effic, linestyle = '-.',color ='black',label = 'Efficiency correction')
        plt.plot(energy, corre_compton, linestyle = '-.',color ='red',label = 'Compton correction')
        plt.xlim(0,tube_voltage+1)
        plt.ylim(bottom=0)
        plt.ylabel('Counts')
        plt.xlabel('Energy [keV]')
        plt.title(title[0], fontweight='bold')
        plt.legend(frameon=False)
        plt.tight_layout()
        if save_plot==True:
            plt.savefig(spectrum_quality+'_corrected.png')
        plt.show()

def tube_kv_plot(uncertainty_analysis,x,y,a,b,a_ajuste, b_ajuste,spectrum_quality,x_uncertainty, y_uncertainty, channel, total_canais_ajuste, shift,save_plot):
    if uncertainty_analysis == True:
        title = spectrum_quality.split('_')
        x_plot = np.array(np.arange(a*(channel-total_canais_ajuste+shift)+b, a*(channel+shift)+b, 0.01))
        plt.errorbar(x, y, xerr=x_uncertainty, yerr=y_uncertainty, color='green', ecolor='darkgreen', linestyle='', capsize=2)
        plt.plot(x_plot, a_ajuste*x_plot+b_ajuste, linestyle='-', color='royalblue')
        plt.ylim(bottom=0)
        plt.ylabel('Counts')
        plt.xlabel('Energy [keV]')
        plt.title('Tube Voltage - '+ title[0], fontweight='bold')
        plt.tight_layout()
        if save_plot==True:
            plt.savefig('tube_kv_'+spectrum_quality+'.png')
        plt.show()

    else:
        title = spectrum_quality.split('.')
        x_plot = np.array(np.arange(a*(channel-total_canais_ajuste+shift)+b, a*(channel+shift)+b, 0.01))
        plt.scatter(x,y,color='green')
        plt.plot(x_plot, a_ajuste*x_plot+b_ajuste, linestyle='-', color='royalblue')
        plt.ylim(bottom=0)
        plt.ylabel('Contagem')
        plt.xlabel('Energia [keV]')
        plt.title('Tube Voltage - '+ title[0], fontweight='bold')
        plt.tight_layout()
        if save_plot==True:
            plt.savefig('tube_kv_'+spectrum_quality+'.png')
        plt.show()