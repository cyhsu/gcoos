from netCDF4 import Dataset, num2date, date2num
from datetime import datetime
import numpy as np

fid = 'gom_discharge_1900_present.nc'
nc = Dataset(fid)
tm = nc.variables['time']
tim= num2date(tm[:],tm.units)
river_name = nc.variables['river_name'][:]
river_id  = nc.variables['station_id'][:]
discharge = nc.variables['discharge'][:]
gauge_lat = nc.variables['gauge_latitude'][:]
gauge_lon = nc.variables['gauge_longitude'][:]
mouth_lat = nc.variables['mouth_latitude'][:]
mouth_lon = nc.variables['mouth_longitude'][:]
river_id  = [str(river_id[i],'ascii') for i in range(len(river_id)) ]
river_name_backup = river_name
river_name= [str(river_name[i],'ascii').replace('__',' ').replace('_ ','').replace(' ','') for i in range(len(river_id))]

for i in range(len(river_id)):
	name = river_name[i]
	rdc = discharge[:,i]
	idx,= np.where(~rdc.mask)
	rdc = rdc.filled()
	if name[-1]=='_': name = name[:-1]
	openfile = open('./ascii/'+name,'w')
	openfile.write("#- river_name     : %s\n" % name)
	openfile.write("#- river_id       : %s\n" % river_id[i])
	openfile.write("#- lat_river_mouth: %7.3f\n" % mouth_lat[i])
	openfile.write("#- lon_river_mouth: %7.3f\n" % mouth_lon[i])
	openfile.write("#- lat_station    : %7.3f\n" % gauge_lat[i])
	openfile.write("#- lon_station    : %7.3f\n" % gauge_lon[i])
	openfile.write("#- date\t\t river_discharge (m+3 day-1)\n")
	openfile.write("#- End\n")
	for num in range(idx[0],len(rdc)):
		openfile.write(tim[num].strftime('%Y-%m-%d')+"\t %8.2f\n" %(rdc[num]) )
	openfile.close()
