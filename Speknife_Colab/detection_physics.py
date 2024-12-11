import managing_files as mfiles
import numpy as np

def channel_exceeded_verificator(channel_requested,channel_number):
    if channel_requested > channel_number:
        return True #If the escape correction requests channels beyond the existing ones, the factor is set to zero.
    else:
         return False

def escape_correction(i, energy, corrected_data,tube_voltage,raw_data,a,b,escape_corre,data_uncertainty):
    #Function of the escape correction coefficients
    nk_cd_alfa = 0.0205+0.4823*np.exp(-(energy+23.17)/20.3418)
    nk_cd_beta = 0.0137+0.1792*np.exp(-(energy+26.09)/13.2184)
    nk_te_alfa = 0.0127+0.5177*np.exp(-(energy+27.47)/15.1622)			
    nk_te_beta = 0.0049+0.1737*np.exp(-(energy+30.99)/13.3532)
		
	#Channel of the Energy E+Ek to be used for the correction 
    canal_E_Ekalfa_cd = round((energy+23.2-b)/a) #Rounds to the nearest integer to obtain the channel
    canal_E_Ekbeta_cd = round((energy+26.1-b)/a) 
    canal_E_Ekalfa_te = round((energy+27.5-b)/a)
    canal_E_Ekbeta_te = round((energy+31.0-b)/a)

	#Automation of the corrections by the tube kV, setting factors to zero that are not reached due to kV with energy lower than the k-edge of Cd and Te
    if  (tube_voltage < 23.17):
            nk_cd_alfa = 0
            nk_cd_beta = 0
            nk_te_alfa = 0
            nk_te_beta = 0

    if  (tube_voltage >= 23.17 and tube_voltage < 26.09): 
            nk_cd_beta = 0
            nk_te_alfa = 0
            nk_te_beta = 0

    if  (tube_voltage >= 26.09 and tube_voltage < 27.47): 
            nk_te_alfa = 0
            nk_te_beta = 0

    if  (tube_voltage <= 27.47 and tube_voltage > 30.99): 
            nk_te_beta = 0

    #Calculating escape fractions
    if  (energy > tube_voltage-23.17): #There is no escape count to remove

        photoelectric_factor = 0
        
    elif(energy < tube_voltage-23.17 and energy > tube_voltage-26.09): #Prevents the code from randomly assuming a count value due to canal_E_Ekalfa_cd exceeding the original one
        photoelectric_factor = nk_cd_alfa*raw_data[canal_E_Ekalfa_cd]
        escape_uncertainty = nk_cd_alfa*data_uncertainty[canal_E_Ekalfa_cd]
        data_uncertainty[i] = np.sqrt(data_uncertainty[i]**2+escape_uncertainty**2)
    
    elif(energy < tube_voltage-26.09 and energy > tube_voltage-27.47): 
        photoelectric_factor = nk_cd_alfa*raw_data[canal_E_Ekalfa_cd]+nk_cd_beta*raw_data[canal_E_Ekbeta_cd]
        escape_uncertainty = np.sqrt((nk_cd_alfa*data_uncertainty[canal_E_Ekalfa_cd])**2+(nk_cd_beta*data_uncertainty[canal_E_Ekbeta_cd])**2)
        data_uncertainty[i] = np.sqrt(data_uncertainty[i]**2+escape_uncertainty**2)

    elif(energy < tube_voltage-27.47 and energy > tube_voltage-30.99): 
        photoelectric_factor = nk_cd_alfa*raw_data[canal_E_Ekalfa_cd]+nk_cd_beta*raw_data[canal_E_Ekbeta_cd]+nk_te_alfa*raw_data[canal_E_Ekalfa_te]
        escape_uncertainty = np.sqrt((nk_cd_alfa*data_uncertainty[canal_E_Ekalfa_cd])**2+(nk_cd_beta*data_uncertainty[canal_E_Ekbeta_cd])**2+(nk_te_alfa*data_uncertainty[canal_E_Ekalfa_te])**2)
        data_uncertainty[i] = np.sqrt(data_uncertainty[i]**2+escape_uncertainty**2)

    else: #corrige tudo
        photoelectric_factor = nk_cd_alfa*raw_data[canal_E_Ekalfa_cd]+nk_cd_beta*raw_data[canal_E_Ekbeta_cd]+nk_te_alfa*raw_data[canal_E_Ekalfa_te]+nk_te_beta*raw_data[canal_E_Ekbeta_te]
        escape_uncertainty = np.sqrt((nk_cd_alfa*data_uncertainty[canal_E_Ekalfa_cd])**2+(nk_cd_beta*data_uncertainty[canal_E_Ekbeta_cd])**2+(nk_te_alfa*data_uncertainty[canal_E_Ekalfa_te])**2+(nk_te_beta*data_uncertainty[canal_E_Ekbeta_te])**2)
        data_uncertainty[i] = np.sqrt(data_uncertainty[i]**2+escape_uncertainty**2)

    corrected_data[i]=raw_data[i]-photoelectric_factor #replacing to the new correted values
    escape_corre[i] = photoelectric_factor

def compton_correction(i,energy,corrected_data,a,b,corre_compton,data_uncertainty, energy_uncertainty, a_uncertainty, b_uncertainty):
    nist_energy, nist_abs = mfiles.reading_files('/content/drive/MyDrive/Speknife_Colab/theoretical_functions_data/compton_nist.txt')#opening nist data of absorption coeficient
    
    #Compton correction functions
    compton_edge = (2*(energy**2))/(2*energy+511) #Compton Edge Energy
    compton_edge_channel = round((compton_edge-b)/a) 

    #uncertainty of the compton edge energy
    compton_edge_uncertainty = (4*energy*(2*energy+511)-2*(2+511)*(energy**2))*energy_uncertainty[i]/(2*energy+511)**2
    compton_edge_channel_uncertainty = np.sqrt((compton_edge_uncertainty/a)**2+(b_uncertainty/a)**2+(((compton_edge-b)/a**2)*a_uncertainty)**2)
    
    if (compton_edge_channel>0): 
        #Happens for the initial channels and therefore we do nothing
        for j in range(len(nist_energy)-1): 
            if  (energy == nist_energy[j]): 	
                for k in range(compton_edge_channel,-1,-1):
                    corrected_data[k]=corrected_data[k]-(nist_abs[j]*corrected_data[compton_edge_channel])/compton_edge_channel
                    corre_compton[k]=(nist_abs[j]*corrected_data[compton_edge_channel])/(compton_edge_channel)+corre_compton[k]	
                    data_uncertainty[k] = np.sqrt( (nist_abs[j]*data_uncertainty[compton_edge_channel]/compton_edge_channel)**2 + (data_uncertainty[compton_edge_channel]*compton_edge_channel_uncertainty/compton_edge_channel**2)**2)
                        
            #Case where linear interpolation between nearby points is necessary
            elif   (energy > nist_energy[j] and energy < nist_energy[j+1]):
                    x_interp = [nist_energy[j],nist_energy[j+1]]
                    y_interp = [nist_abs[j],nist_abs[j+1]]
                    fator_compton_interpolado = np.interp(energy,x_interp,y_interp)	

                    #Calculating the efficiency correction
                    for k in range(compton_edge_channel,0,-1):
                        corrected_data[k]=corrected_data[k]-(fator_compton_interpolado*corrected_data[compton_edge_channel])/compton_edge_channel
                        corre_compton[k]=(fator_compton_interpolado*corrected_data[compton_edge_channel])/(compton_edge_channel)+corre_compton[k]
                        data_uncertainty[k] = np.sqrt( (nist_abs[j]*data_uncertainty[compton_edge_channel]/compton_edge_channel)**2 + (data_uncertainty[compton_edge_channel]*compton_edge_channel_uncertainty/compton_edge_channel**2)**2)

def efficiency_correction(i, energy, corrected_data,corre_effic,data_uncertainty): 
    effic_energy, effic_data = mfiles.reading_files('/content/drive/MyDrive/Speknife_Colab/theoretical_functions_data/eficiencia_ATomal.txt')
    if(energy[i]<5):
        corrected_data[i]=0 #Cutting off all counts below 5 keV in the spectrum

    elif (energy[i]>=5 and energy[i]<=150):

    #Finding the energy range to which my i refers in the efficiency file
        for j in range(len(effic_data)):
            if(energy[i] == effic_energy[j]): 
                corre_effic[i]=(corrected_data[i]/effic_data[j])-corrected_data[i]
                corrected_data[i]=(corrected_data[i]/effic_data[j])
                break #sai do loop
            
            #Case where linear interpolation between nearby points is necessary
            elif(energy[i] > effic_energy[j] and energy[i] < effic_energy[j+1]):

                #Calculation of interpolation
                x_interp = [effic_energy[j],effic_energy[j+1]]
                y_interp = [effic_data[j],effic_data[j+1]]
                eficiencia_interpolada = np.interp(energy[i],x_interp,y_interp)
                    
                corre_effic[i]=(corrected_data[i]/eficiencia_interpolada)-corrected_data[i]
                corrected_data[i]=(corrected_data[i]/eficiencia_interpolada)   
                data_uncertainty[i] = data_uncertainty[i]/eficiencia_interpolada   
