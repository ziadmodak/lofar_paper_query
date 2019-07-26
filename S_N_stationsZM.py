#!/usr/bin/python

"""Author: M.Iacobelli iacobelli@astron.nl"""

import fnmatch, numpy as np, os, re, sys ; import matplotlib.pyplot as plt ; import scipy.stats as stats


def usage():
    usage_string = """
    usage:  python S_N_stations.py <pipeline SASid> <save plots [Y/N]>
    This script parses and collects stations S/N statistics from a log
    file generated by the Lofar automatic pulsar (PULP) pipeline framework.
    It provides the following outputs:
    1. For the array used in the Fly's eye run:
        - list of S/N values
    2. For the array used in the Fly's eye run:
        - a plot of stations S/N, grouped per station type (i.e. CS,RS,IS)
        
    Remember to set matplotlib: docker-run.sh lofar-pipeline:trunk
    """
    print usage_string


def find_files(base, pattern):
    '''Return list of files matching pattern in base folder.'''
    return [n for n in fnmatch.filter(os.listdir(base), pattern) if
        os.path.isfile(os.path.join(base, n))]


def find_all(a_str, sub):
    """
    Find all occurrences of a substring in a string
    """
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub) # use start += 1 to find overlapping matches

#list(find_all('spam spam spam spam', 'spam')) # [0, 5, 10, 15]


def open_file_and_parse(log_summary_path):
    """
    Performs the interaction with the summary log file.
    Opens it from disk and search for pattern -label 
    Throwing a ImportError if it fails.
    """
    # Open the file raise on error
    stats_sn_log = None
    try:        #, encoding='ascii'
    	if open(log_summary_path, 'r').read().find('HBA_DUAL') > 0:
    		stat_mode = 'HBA_DUAL'
    	if open(log_summary_path, 'r').read().find('LBA_INNER') > 0:
    		stat_mode = 'LBA_INNER'
    	if open(log_summary_path, 'r').read().find('LBA_OUTER') > 0:
    		stat_mode = 'LBA_OUTER'
        stats_sn_log = open(log_summary_path, 'r').readlines()
        #
        print '\n STATION  -  S/N \n'
        stat_name = [] ; stat_sn = []
        for line in stats_sn_log:
            if ('montage -background none -pointsize' in line):
                #print line
                sequence = line.split('-label ')
                #print sequence
                for indx,substring in enumerate(sequence):
                    #print indx, substring.replace('\'','')
                    if ('CS SAP0 ' in substring.replace('\'','')):
                        newrow = substring.replace('\'','')
                        found_objname = re.search('BA(.+?)S/N ', newrow).group(1) #; print found_objname.replace('\\n','')
                        if newrow[2+6:2+8] == 'CS':
                            found_sn = re.search('S/N = (.+?) stokes', newrow).group(1)
                            stat_name.append(newrow[2+6:2+15]) ; stat_sn.append(float(found_sn))
                            print '{0}    {1}'.format(newrow[2+6:2+15],found_sn)
                        elif newrow[2+6:2+8] == 'RS':
                            found_sn = re.search('S/N = (.+?) stokes', newrow).group(1)
                            stat_name.append(newrow[2+6:2+14]) ; stat_sn.append(float(found_sn))
                            print '{0}     {1}'.format(newrow[2+6:2+14],found_sn)
                        else:
                            found_sn = re.search('S/N = (.+?) stokes', newrow).group(1)
                            stat_name.append(newrow[2+6:2+14]) ; stat_sn.append(float(found_sn))
                            print '{0}     {1}'.format(newrow[2+6:2+14],found_sn)
    except:
        # Parsing of log should succeed if written by the pipeline framework
        # In this case an exception should be allowed
        print "\n Attempted to parse '{0}' as a txt file. This failed \n".format(log_summary_path)
    # return station mode, station name and S/N as list object
    return stat_mode, stat_name, stat_sn, found_objname.replace('\\n','')


def sn_statistics(stat_name,stat_sn):
    """
    Group stations per type, characterize S/N distributions of each group.
    """
    CSstat_ID = [] ; RSstat_ID = [] ; INTstat_ID = []
    CS_sn = [] ; RS_sn = [] ; INT_sn = []
    for i in range(len(stat_name)):
        if stat_name[i][0:2] == 'CS':
            CSstat_ID.append(i) ; CS_sn.append(stat_sn[i])
        elif stat_name[i][0:2] == 'RS':
            RSstat_ID.append(i) ; RS_sn.append(stat_sn[i])
        else:
            INTstat_ID.append(i) ; INT_sn.append(stat_sn[i])
    #
    CSstat_ID = np.array(CSstat_ID) ; RSstat_ID = np.array(RSstat_ID) ; INTstat_ID = np.array(INTstat_ID)
    print '\n Found {0}CS, {1}RS and {2}INT stations \n'.format(len(CSstat_ID),len(RSstat_ID),len(INTstat_ID))
    CS_sn = np.array(CS_sn) ; RS_sn = np.array(RS_sn) ; INT_sn = np.array(INT_sn)
    if len(CS_sn) != 0:
        meanCS = np.mean(CS_sn) ; stdCS = np.std(CS_sn)
        print ' CS: <S/N> = {0} +/- {1} '.format(meanCS,stdCS)
        chisq_CS,pvalue_CS = stats.normaltest(CS_sn) # returns a 2-tuple of: the chi-squared statistic (the closer to 1 the better), the associated p-value (the smaller, e.g. <<1, the worst).
        if(pvalue_CS < 0.055):
            print 'S/N of CS; not normal distribution: p-value {0}'.format(pvalue_CS)
        else:
            print 'S/N of CS; normal distribution: chi-squared {0}, p-value {1}'.format(chisq_CS,pvalue_CS)
    #
    if len(RS_sn) != 0:
        meanRS = np.mean(RS_sn) ; stdRS = np.std(RS_sn)
        print ' RS: <S/N> = {0} +/- {1} '.format(meanRS,stdRS)
        chisq_RS,pvalue_RS = stats.normaltest(RS_sn)
        if(pvalue_RS < 0.055):
            print 'S/N of RS; not normal distribution: p-value {0}'.format(pvalue_RS)
        else:
            print 'S/N of RS; normal distribution: chi-squared {0}, p-value {1}'.format(chisq_RS,pvalue_RS)
    #
    if len(INT_sn) != 0:
        meanINT = np.mean(INT_sn) ; stdINT = np.std(INT_sn)
        print ' IS: <S/N> = {0} +/- {1} '.format(meanINT,stdINT)
        chisq_IS,pvalue_IS = stats.normaltest(INT_sn)
        if(pvalue_IS < 0.055):
            print 'S/N of IS; not normal distribution: p-value {0}'.format(pvalue_IS)
        else:
            print 'S/N of IS; normal distribution: chi-squared {0}, p-value {1}'.format(chisq_IS,pvalue_IS)
    return CSstat_ID, RSstat_ID, INTstat_ID, CS_sn, RS_sn, INT_sn


def sn_plots(OBJ_name, Stat_mode, Stat_name, CSstat_ID, RSstat_ID, INTstat_ID, CS_sn, RS_sn, INT_sn, SASid, SAVEfig):
	"""
	Plot S/N distributions per station group along with mean SN
	"""
	Stat_ID = np.array(CSstat_ID.tolist() + RSstat_ID.tolist() + INTstat_ID.tolist())
	xticks = np.arange(0,len(Stat_ID))
	plt.figure()
	if len(CS_sn) != 0:
		#plt.scatter(CSstat_ID, CS_sn, marker='o', color='g', label='S/N CS')
		plt.errorbar(CSstat_ID, CS_sn, yerr=CS_sn*0.1, fmt='go', ls='None', label='S/N CS')
		plt.axhline(y=np.mean(CS_sn), linestyle='-.', linewidth=2, color='g',label='CS only <S/N>')
		plt.axhline(y=np.mean(CS_sn)-np.std(CS_sn), linestyle='-.', linewidth=1, color='g')
		plt.axhline(y=np.mean(CS_sn)+np.std(CS_sn), linestyle='-.', linewidth=1, color='g')
	if len(RS_sn) != 0:
		#plt.scatter(RSstat_ID, RS_sn, marker='o', color='b', label='S/N RS')
		plt.errorbar(RSstat_ID, RS_sn, yerr=RS_sn*0.1, fmt='bo', ls='None', label='S/N RS')
		plt.axhline(y=np.mean(RS_sn), linestyle='--', linewidth=2, color='b',label='RS only <S/N>')
		plt.axhline(y=np.mean(RS_sn)-np.std(RS_sn), linestyle='--', linewidth=1, color='b')
		plt.axhline(y=np.mean(RS_sn)+np.std(RS_sn), linestyle='--', linewidth=1, color='b')
	if len(INT_sn) != 0:
		#plt.scatter(INTstat_ID, INT_sn, marker='o', color='r', label='S/N INT')
		plt.errorbar(INTstat_ID, INT_sn, yerr=INT_sn*0.1, fmt='ro', ls='None', label='S/N INT')
		plt.axhline(y=np.mean(INT_sn), linestyle='-', linewidth=2, color='r',label='INT only <S/N>')
		plt.axhline(y=np.mean(INT_sn)-np.std(INT_sn), linestyle='-', linewidth=1, color='r')
		plt.axhline(y=np.mean(INT_sn)+np.std(INT_sn), linestyle='-', linewidth=1, color='r')
	plt.xticks(xticks, Stat_name, rotation=90, fontsize=7)
	plt.yticks(fontsize=9)
	plt.ylabel('S/N') ; plt.ylim(ymin=0) ; plt.legend(loc=0, fontsize='small') ; plt.xlim(-1,len(Stat_ID)) ; plt.grid(True)
	plt.title('Fly\'s Eye run L%s | Target PSR %s' % (SASid,OBJ_name), fontsize='large')
        plt.tight_layout()
	if SAVEfig == 'y' or SAVEfig == 'Y': plt.savefig(save_plot_path+'/L'+str(SASid)+'_'+str(Stat_mode)+'_SNplot.png')
#	plt.show()


#
# Main routine start here
#
if __name__ == '__main__':
	if len(sys.argv) < 3:
		usage()
		exit(1)
	SASid = sys.argv[1]
	SAVEfig = sys.argv[2]
        save_plot_path = sys.argv[3]
        os.chdir(save_plot_path) # go to the output directory first so I never need to use this stupid variable again
	log_files = find_files('.', 'L*summaryCS.log')
	if len(log_files) == 0.:
        # this is the repository of pipelines logs ! IT MAY CHANGE WITH CEPX
                os.system('cp /data/projects/FE_monitoring/L'+str(SASid)+'/pulp/cs/L'+str(SASid)+'_summaryCS.tar .')
		os.system('tar -xvf L'+str(SASid)+'_summaryCS.tar')
		log_files = find_files('.', 'L*summaryCS.log')
 		print '\n Found %d summary log files; using %s \n' % (len(log_files),log_files[0])
	else:
		print '\n Found %d summary log files; using %s \n' % (len(log_files),log_files[0])
	
	# read info about stations S/N
	Stat_mode, Stat_name, Stat_SN, obj_name = open_file_and_parse(log_files[0])
	# extract some statistics per station type
	CSstat_ID, RSstat_ID, INTstat_ID, CS_sn, RS_sn, INT_sn = sn_statistics(Stat_name,Stat_SN)
	# plot values
	sn_plots(obj_name, Stat_mode, Stat_name, CSstat_ID, RSstat_ID, INTstat_ID, CS_sn, RS_sn, INT_sn, SASid, SAVEfig)
	# remove auxiliary files and folders
#	os.system('rm -f L*_summaryCS.log')
	os.system('rm -f L*_summaryCS.tar')
#	os.system('rm -f combined*.png')
#	os.system('rm -f *status*.png')
#	os.system('rm -f *.pdf')
	os.system('rm -rf stokes') 
	os.system('rm -f L*.parset')
	os.system('rm -f beam_process_node.txt')
	os.system('rm -f *-squared.txt')
	os.system('rm -f *.par')
	os.system('rm -f *~')