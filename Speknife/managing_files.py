import statistical_analysis as stat_analy

def reading_spectrum_file(name_file,is_mca): 
    contagem = []
    if is_mca == True:
        with open(name_file, 'r', encoding='latin-1') as file:
            inside_data_section = False
            for line in file:
                #Remove whitespace at the beginning and end of the line.
                line = line.strip()

                if line == '<<DATA>>':
                    inside_data_section = True
                    continue

                if line == '<<END>>':
                    break  
                    
                if inside_data_section == True:
                    contagem.append(int(line))
    else:
        #If it is not MCA, call another reading function (assuming it exists).
        contagem = reading_files(name_file)

    return contagem

def reading_files(name_file):
    colum_0 = []
    colum_1 =[]
    file = open(name_file,'r')
    data = file.readlines()
    for line in data:
        if line.startswith('#'): #Ignorim first line of a file if it has a #
            continue
        else:
            line = line.strip().split()
            if (len(line)==1):  #Case where there is only one column of data
                colum_0.append(float(line[0]))
                
            elif (len(line)==2): #Case where there is 2 column of data 
                colum_0.append(float(line[0]))
                colum_1.append(float(line[1]))
                
            else:
                 print('The function from managing files only support txt files with two columns of data. For other configuration make some changes in managing_files.py')

    if (len(line)==1):
        return colum_0 

    else:  
        return colum_0, colum_1 

def writing_files(energy=0,energy_uncertainty=0,raw_data=0, corrected_data=0, data_uncertainty=0 ,spectrum_quality=0, a=0, b=0, tube_voltage=0,channel_number=0,uncertainty_analysis = 0,tube_voltage_measurement=0,tube_kv = 0, r_pearson = 0, tube_kv_uncertainty = 0): #todos os valores são zero por padrão para evitar bug
    if uncertainty_analysis == True and tube_voltage_measurement == True:
        file = open('working_area/'+spectrum_quality.replace('.mca','')+'_corrected.txt','w')
        file.writelines("###################################################################################################################\n")
        file.writelines("#Corrected data of the spectrum from the file "+spectrum_quality+"\n")
        file.writelines("###################################################################################################################\n")
        file.writelines('#\n')
        file.writelines('#Input Parameters declared\n')
        file.writelines('#\n')
        file.writelines('#Linear coefficient a = '+str(a)+ ' keV and linear coefficient b = '+str(b)+' keV\n')
        file.writelines('#Tube Voltage '+str(tube_voltage)+' kV' +'\n')
        file.writelines('#Total number of channels '+str(channel_number)+'\n')
        file.writelines("#------------------------------------------------------------------------------------------------------------------\n")
        file.writelines("#The mean energy before was {} keV and the correted is {} keV with an uncertainty of {} \n".format(round(stat_analy.mean_energy(raw_data,energy),5),round(stat_analy.mean_energy(corrected_data,energy),5),round(stat_analy.mean_energy_uncertainty(corrected_data, data_uncertainty, energy, energy_uncertainty),5)))
        file.writelines("#The tube voltage is {} kV with an uncertainty of {} and pearson coefficient {} \n".format(round(tube_kv,4),round(tube_kv_uncertainty,4),r_pearson))          
        file.writelines("#------------------------------------------------------------------------------------------------------------------\n")
        file.writelines('#\n')
        file.writelines("#Energy (keV); energy uncertainty (keV); counts; counts uncertainty\n")
    
        for i in range(len(corrected_data)):
            file.writelines(str(energy[i])+' , '+str(round(energy_uncertainty[i],4))+' , '+str(round(corrected_data[i],4))+' , '+str(round(data_uncertainty[i],4))+'\n')
        file.close()

    elif uncertainty_analysis == True and tube_voltage_measurement == False:
            file = open('working_area/'+spectrum_quality.replace('.mca','')+'_corrected.txt','w')
            file.writelines("###################################################################################################################\n")
            file.writelines("#Corrected data of the spectrum from the file "+spectrum_quality+"\n")
            file.writelines("###################################################################################################################\n")
            file.writelines('#\n')
            file.writelines('#Input Parameters declared\n')
            file.writelines('#\n')
            file.writelines('#Linear coefficient a = '+str(a)+ ' keV and linear coefficient b = '+str(b)+' keV\n')
            file.writelines('#Tube Voltage '+str(tube_voltage)+' kV' +'\n')
            file.writelines('#Total number of channels '+str(channel_number)+'\n')
            file.writelines("#------------------------------------------------------------------------------------------------------------------\n")
            file.writelines("#The mean energy before was {} keV and the correted is {} keV with an uncertainty of {} \n".format(round(stat_analy.mean_energy(raw_data,energy),5),round(stat_analy.mean_energy(corrected_data,energy),5),round(stat_analy.mean_energy_uncertainty(corrected_data, data_uncertainty, energy, energy_uncertainty),5)))
            file.writelines("#------------------------------------------------------------------------------------------------------------------\n")
            file.writelines('#\n')
            file.writelines("#Energy (keV); energy uncertainty (keV); counts; counts uncertainty\n")
        
            for i in range(len(corrected_data)):
                file.writelines(str(energy[i])+' , '+str(round(energy_uncertainty[i],4))+' , '+str(round(corrected_data[i],4))+' , '+str(round(data_uncertainty[i],4))+'\n')
            file.close()
    
    elif uncertainty_analysis == False and tube_voltage_measurement == True:
        file = open('working_area/'+spectrum_quality.replace('.mca','')+'_corrected.txt','w')
        file.writelines("###################################################################################################################\n")
        file.writelines("#Corrected data of the spectrum from the file "+spectrum_quality+"\n")
        file.writelines("###################################################################################################################\n")
        file.writelines('#\n')
        file.writelines('#Input Parameters declared\n')
        file.writelines('#\n')
        file.writelines('#Linear coefficient a = '+str(a)+ ' keV and linear coefficient b = '+str(b)+' keV\n')
        file.writelines('#Tube Voltage '+str(tube_voltage)+' kV' +'\n')
        file.writelines('#Total number of channels '+str(channel_number)+'\n')
        file.writelines("#------------------------------------------------------------------------------------------------------------------\n")
        file.writelines("#The mean energy before was {} keV and the correted is {} keV \n".format(round(stat_analy.mean_energy(raw_data,energy),5),round(stat_analy.mean_energy(corrected_data,energy),5)))
        file.writelines("#The tube voltage is {} kV and pearson coefficient {} \n".format(round(tube_kv,4),r_pearson)) 
        file.writelines("#------------------------------------------------------------------------------------------------------------------\n")
        file.writelines('#\n')
        file.writelines("#Energy (keV); counts\n")

        for i in range(len(corrected_data)):
            file.writelines(str(energy[i])+' , '+str(round(corrected_data[i],4))+'\n')
        file.close()
        
    elif uncertainty_analysis == False and tube_voltage_measurement == False:
        file = open('working_area/'+spectrum_quality.replace('.mca','')+'_corrected.txt','w')
        file.writelines("###################################################################################################################\n")
        file.writelines("#Corrected data of the spectrum from the file "+spectrum_quality+"\n")
        file.writelines("###################################################################################################################\n")
        file.writelines('#\n')
        file.writelines('#Input Parameters declared\n')
        file.writelines('#\n')
        file.writelines('#Linear coefficient a = '+str(a)+ ' keV and linear coefficient b = '+str(b)+' keV\n')
        file.writelines('#Tube Voltage '+str(tube_voltage)+' kV' +'\n')
        file.writelines('#Total number of channels '+str(channel_number)+'\n')
        file.writelines("#------------------------------------------------------------------------------------------------------------------\n")
        file.writelines("#The mean energy before was {} keV and the correted is {} keV \n".format(round(stat_analy.mean_energy(raw_data,energy),5),round(stat_analy.mean_energy(corrected_data,energy),5)))
        file.writelines("#------------------------------------------------------------------------------------------------------------------\n")
        file.writelines('#\n')
        file.writelines("#Energy (keV); counts\n")

        for i in range(len(corrected_data)):
            file.writelines(str(energy[i])+' , '+str(round(corrected_data[i],4))+'\n')
        file.close()