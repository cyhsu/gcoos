import xarray as xr
import numpy as np, re

fid = 'gom_discharge_1900_present.nc'
df  = xr.open_dataset(fid)

for num, river_name in enumerate(df.river_name.data):
	river_name = river_name.tolist().decode('utf-8')
	river_name = re.sub(r'_+$',' ',river_name)
	river_nam2 = river_name.replace('_',' ')

	with open('./ascii/abc_{}'.format(river_name),'w') as f:
		f.write('#- river_name     : {}\n'.format(river_nam2))
		f.write("#- river_id       : {}\n".format(df.station_id[num].data.tolist().decode('utf-8')))
		f.write("#- lat_river_mouth: {:7.3f}\n".format(df.mouth_latitude[num].data))
		f.write("#- lon_river_mouth: {:7.3f}\n".format(df.mouth_longitude[num].data))
		f.write("#- lat_station    : {:7.3f}\n".format(df.gauge_latitude[num].data))
		f.write("#- lon_station    : {:7.3f}\n".format(df.gauge_longitude[num].data))
		f.write("#- date\t\t river_discharge (m+3 day-1)\n")
		f.write("#- End\n")

		for tid, tim in enumerate(df.time.data):
			f.write('{}\t {:8.2f}\n'.format(np.datetime_as_string(tim,'D'),
												df.isel(station=num,time=tid).discharge.data) )

	#print(num, river_name)
