import numpy as np
import ploting as plot

def spectra_uncertainty(energy, energy_uncertainty, data, data_uncertainty,r_pearson, a_uncertainty, b_uncertainty):
    data_uncertainty = []
    energy_uncertainty = []
    for i in range(len(data)):
        data_uncertainty.append(np.sqrt(data[i]))
        energy_uncertainty.append(np.sqrt(((i*a_uncertainty)**2+b_uncertainty**2+2*r_pearson*i*a_uncertainty*b_uncertainty)+(energy[101]-energy[100])**2/12))
    return energy_uncertainty , data_uncertainty

def mean_energy(spectrum_data,energy):
    mean_energy = np.average(energy, weights=spectrum_data)
    
    return mean_energy

def mean_energy_uncertainty(data, data_uncertainty, energy, energy_uncertainty): 
    uncertainty = []
    uncertainty = 0
    for i in range(len(data)):
        uncertainty = (((energy[i]-mean_energy(data,energy))*data_uncertainty[i])/(sum(data)))**2 + ((data[i]*energy_uncertainty[i])/(sum(data)))**2 + uncertainty
 
    return np.sqrt(uncertainty) 

def tube_kv(uncertainty_analysis,a, b, tube_voltage, energy,energy_uncertainty, data, data_uncertainty, spectrum_quality,save_plot,tube_voltage_plot,shift): 
    channel = round((tube_voltage-b)/a) 
    total_canais_ajuste = 15
    if uncertainty_analysis == True:
        x = np.array(energy[channel-total_canais_ajuste+shift:channel+shift]) 
        x_uncertainty = np.array(energy_uncertainty[channel-total_canais_ajuste+shift:channel+shift])
        y = np.array(data[channel-total_canais_ajuste+shift:channel+shift])
        y_uncertainty = np.array(data_uncertainty[channel-total_canais_ajuste+shift:channel+shift])
            
        #Conventional linear regression to determine the linear coefficient before transferring the uncertainty to y for the weighted linear fit
        a_convencional = (np.mean(x*y)-np.mean(y)*np.mean(x))/np.var(x)

        #transferring the uncertainty to y for the weighted linear fit
        transfered_uncertainty = np.sqrt(y_uncertainty**2+(a_convencional*x_uncertainty)**2)

        ################################################################################################
        ######                              Ajuste linear com pesos                               ######   
        ################################################################################################

        sum = 0
        for i in range(len(x)):
            sum = 1 / transfered_uncertainty[i]**2 + sum
        sigmao = np.sqrt(1 / sum)

        #Means
        x_med_pond = np.average(x, weights=(sigmao / transfered_uncertainty)**2)
        x2_med_pond = np.average(x**2, weights=(sigmao / transfered_uncertainty)**2)
        y_med_pond = np.average(y, weights=(sigmao / transfered_uncertainty)**2)
        xy_med_pond = np.average(x * y, weights=(sigmao / transfered_uncertainty)**2)

        #Weighted variance of x
        suma_varx_2 = 0
        for i in range(len(x)):
            suma_varx_2 = ((x[i] - x_med_pond) / transfered_uncertainty[i])**2 + suma_varx_2
            varx_2 = (sigmao**2) * suma_varx_2  #The sigmao factors in, so it can only be multiplied at the end (it is constant).

        #Weighted variance of y
        suma_vary_2 = 0
        for i in range(len(x)):
            suma_vary_2 = ((y[i] - y_med_pond) / transfered_uncertainty[i])**2 + suma_vary_2
            vary_2 = (sigmao**2) * suma_vary_2  #The sigmao factors in, so it can only be multiplied at the end (it is constant).

        a_peso = (xy_med_pond - x_med_pond * y_med_pond) / varx_2
        b_peso = y_med_pond - a_peso * x_med_pond
        incerteza_a_peso = sigmao / np.sqrt(varx_2)
        incerteza_b_peso = incerteza_a_peso * np.sqrt(x2_med_pond)
        r_pearson_peso = (a_peso * np.sqrt(varx_2)) / np.sqrt(vary_2)
        r_ab = -(x_med_pond*(incerteza_a_peso)**2)/(incerteza_a_peso*incerteza_b_peso)
        
        tube_kv = -b_peso/a_peso
        tube_kv_uncertainty =np.sqrt(((b_peso*incerteza_a_peso)/(a_peso**2))**2+(incerteza_b_peso/a_peso)**2-2*r_ab*b_peso*incerteza_a_peso*incerteza_b_peso/(a_peso)**3)

        if tube_voltage_plot == True:
            plot.tube_kv_plot(uncertainty_analysis,x,y,a,b,a_peso, b_peso,spectrum_quality,x_uncertainty, y_uncertainty, channel, total_canais_ajuste, shift,save_plot)

        return tube_kv, tube_kv_uncertainty, round(r_pearson_peso,4)
    
    else:
        x = np.array(energy[channel-total_canais_ajuste+shift:channel+shift]) 
        x_uncertainty = np.array(energy_uncertainty[channel-total_canais_ajuste+shift:channel+shift])
        y = np.array(data[channel-total_canais_ajuste+shift:channel+shift])
        y_uncertainty = np.array(data_uncertainty[channel-total_canais_ajuste+shift:channel+shift])
            
        a_convencional = (np.mean(x*y)-np.mean(y)*np.mean(x))/np.var(x)
        b_convencional = np.mean(y) - a_convencional*np.mean(x)
        r_pearson = (np.mean(x*y)-np.mean(y)*np.mean(x))/(np.std(x)*np.std(y))
        tube_kv = -b_convencional/a_convencional

        if tube_voltage_plot == True:
            plot.tube_kv_plot(uncertainty_analysis,x,y,a,b,a_convencional, b_convencional,spectrum_quality,x_uncertainty, y_uncertainty, channel, total_canais_ajuste, shift,save_plot)

        return tube_kv, round(r_pearson,4)