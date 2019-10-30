import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
from netCDF4 import Dataset, num2date, date2num
from datetime import datetime, timedelta
matplotlib.use('Agg')

#- PRE-REQUEST PARAMETER
os.system('rm ./png/*.png')

fid = 'gom_discharge_1900_present.nc'
nc = Dataset(fid)
tm = nc.variables['time']; tim= num2date(tm[:],tm.units)
river_id  = nc.variables['station_id'][:]
river_id  = [str(river_id[i], 'ascii') for i in range(len(river_id)) ]
rivername= nc.variables['river_name'][:]
rivername= [str(rivername[i],'ascii').replace('__',' ').replace('_ ','').replace(' ','') for i in range(len(river_id))]
discharge = nc.variables['discharge'][:]

idx = [i for i in range(len(tim)) if (tim[i].month!=2) or (tim[i].day!=29) ]
discharge_no_229 = discharge[idx]
discharge_no_229.fill_value = np.nan
discharge_no_229 = discharge_no_229.filled()
dymean  = np.roll(np.array([[ np.nanmean(discharge_no_229[i::365,j]) \
                          for j in range(len(river_id))]
                          for i in range(365)]),212,0)

time_x = datetime(datetime.today().year,1,1); dt = timedelta(days=1)
adt= (datetime.today() - time_x).days
time_dymean = [ time_x + dt * i for i in range(365)]
time_current= [ time_x + dt * i for i in range(adt)]
plt.figure(figsize=(17,4))


for rid in range(len(river_id)):
   river_name = rivername[rid]
   if river_name[-1] == '_': river_name = river_name[:-1]
   plt.plot(time_dymean,dymean[:,rid],label="Long-term Daily Mean")
   plt.plot(time_current,discharge_no_229[-len(time_current):,rid],label="Current Year")
   ax = plt.legend(loc='upper left')
   ax.get_frame().set_alpha(0.5)
   plt.title('Daily River Discharge : '+river_name.replace('_',' '),fontsize=14)
   pic_name = './png/'+river_name+'.png'
   plt.ylabel('$m^3 day^{-1}$',fontsize=14)
   plt.savefig(pic_name,dpi=300)
   plt.clf()
   #print( river_name, pic_name)
