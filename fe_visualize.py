#!/usr/bin/python

import os
import glob
import numpy as np
import sys
import time
import matplotlib.pyplot as plt

def usage_help():
    doc_string = """ 
Usage:
	fe_visualize.py <obs_filter> <station_group> <station(s)> <save_plot (Y/N)> <path>

Allowed Arguments:
	obs_filter: HBA_DUAL, LBA_INNER or LBA_OUTER
	station_group: CS, RS or INT for core, remote or international stations respectively 
	station(s): Names of stations separated by commas to plot the data of given stations from the station_group. ALL to plot the data of all stations from a group. The station names should follow the standard (see Examples below)
	save_plot: Y or N to save or skip saving the plot
	path: If save_plot = Y, the path where the plot will be saved 

Examples:
	fe_visualize.py HBA_DUAL CS CS001HBA1,CS031HBA0,CS501HBA0 Y /home/modak/
	
	fe_visualize.py LBA_INNER INT PL610LBA,IE613LBA N 

	fe_visualize.py LBA_OUTER RS ALL Y .

Description:
	The script will parse the pulsar pipeline output logs and look for the SNRs of all the stations that fulfill the selection criteria based on the obs_filter. station_group and station(s) arguments. For a given filter and group of stations, the plots of all required stations will be compared to the median SNR of that group.
    """
    print(doc_string)

def open_file(path_to_folder):
    with open(path_to_folder+'chi-squared.txt', 'r') as my_file:
        _chisq = my_file.readlines()
    with open(glob.glob(path_to_folder+'*_summaryCS.log')[0], 'r') as my_log:
        log_head = [next(my_log) for x in xrange(10)]
    return _chisq, log_head

def parse_files(_chisq, log_head):
    snrs = np.array([line[line.find('S/N')+4:].split()[0] for line in _chisq])
    stations = [line[line.find('SAP0'):].split('/')[1] for line in _chisq]
    mode = log_head[7].split()[0]
    return mode, np.array([stations,snrs]).T

def separate_data_deprecated(data):
    hba_list = []; lba_in_list = []; lba_out_list = []
    for i in xrange(len(data)):
        if data[i][0] == 'HBA_DUAL':
            hba_list.append(data[i][1])
        elif data[i][0] == 'LBA_INNER':
            lba_in_list.append(data[i][1])
        else:
            lba_out_list.append(data[i][1])
    return hba_list, lba_in_list, lba_out_list

def separate_data(data, obs_filter):
    data_list = []
    for i in xrange(len(data)):
        if data[i][0] == obs_filter:
            data_list.append(data[i][1])
    return data_list


def make_array(data_list):
    data_arr = np.zeros((len(data_list[0]),len(data_list)+1),dtype='|S9')
    data_arr[:,0] = data_list[0][:,0]

    for i in xrange(len(data_list)):
        for j in xrange(len(data_list[0])):
            if data_list[0][j] in data_list[i]:
                data_arr[j,i+1] = data_list[i][np.argwhere(data_list[i]==data_list[0][j])[0][0]][1]
            else:
                data_arr[j,i+1] = np.nan
    return data_arr           

if __name__ == "__main__":
    if len(sys.argv) < 4:
        usage_help()
        sys.exit(1)
    
    obs_filter = sys.argv[1]
    group = sys.argv[2]
    station_list = np.array(sys.argv[3].split(','))
    if sys.argv[4] == 'Y':
        savepath = sys.argv[5]
    elif sys.argv[4] == 'N':
        savepath = ''
 
    data = []
    globs = glob.glob('/data/projects/FE_monitoring/L*/pulp/cs/')
    globs.sort()
    for i in globs:
        chisq, head = open_file(i)
        data.append(parse_files(chisq, head))
    
    data_list = separate_data(data,obs_filter)
    data = make_array(data_list)
    
    if group=='INT':
        data = data[np.where([data[i,0][:2] != 'CS' and data[i,0][:2] != 'RS' for i in xrange(len(data))])]
    else:
        data = data[np.where([data[i,0][:2] == group for i in xrange(len(data))])]
    
    plt.figure(figsize=(19,11))
    if station_list[0] == 'ALL':
        stations = data[:,0]
        plt.title('All '+group)
    else:
        stations = station_list
        plt.title(station_list)
    plt.xlabel('Observation Number')
    plt.ylabel('SNR')
    plt.axhline(np.nanmedian(data[:,1:].astype(float)), linewidth='2', ls='--', label='Median of '+group+' = '+str(np.nanmedian(data[:,1:].astype(float))))
#    plt.axhline(np.nanmedian(data[:,1:].astype(float))+np.nanstd(data[:,1:].astype(float)), linewidth='1.5', ls='--')
#    plt.axhline(np.nanmedian(data[:,1:].astype(float))-np.nanstd(data[:,1:].astype(float)), linewidth='1.5', ls='--')
    
    for station in stations:
        yy = data[np.where(data[:,0] == station)][0,1:].astype(float)
        xx = xrange(len(yy))
        plt.errorbar(xx,yy,yy*0.1, label=station, fmt='o-.')

    plt.legend(bbox_to_anchor=(1.11,1.0),fontsize='xx-small',markerscale=0.5)

    if savepath != '':
        plt.savefig(savepath+'/'+group+'_FE_'+str(time.time())[:-3])
    else:
        plt.show()
