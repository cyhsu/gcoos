import numpy as np, pandas as pd, os
from models.usgs import usgs
from models.usace import usace
from netCDF4 import Dataset, num2date, date2num
from datetime import datetime, timedelta

fid = 'gom_discharge_1900_present.nc'
bkup= datetime.today().strftime('%Y_%m_%d')
bkup= 'gom_discharge_1900_present_bkup_{}.nc'.format(bkup)
os.system('cp {} {}'.format(fid,bkup))

nc = Dataset(fid,'r+')
tm = nc.variables['time']
tim = num2date(tm[:], tm.units)
rid= nc.variables['station_id'][:]
rid= [str(i,'ascii') for i in rid]
rdc= nc.variables['discharge']

begin_date = tim[-60]
end_date = datetime.today()
tidx = pd.date_range(begin_date.strftime('%Y-%m-%d'), 
							end_date.strftime('%Y-%m-%d'), freq='D')

for num, station_id in enumerate(rid):
	ncout = 0
	print( 'river id: {}'.format(station_id) )
	if station_id[:5] == '01100' or station_id[:5] == '03045':
		river = usace(station_id[:5], begin_date)
		ncout, ncdate, ncdata = river.bs4()
	else:
		if station_id[:5] == 'FL252':
			river = usgs('252230081021300', begin_date)
			ncout, ncdate, ncdata = river.bs4()
		else:
			river = usgs(station_id, begin_date)
			ncout, ncdate, ncdata = river.bs4()

	if (ncout != 0) & (len(ncdate) > 0):
		df0 = pd.DataFrame(ncdata, index=ncdate,
				columns=['discharge']).resample('D').asfreq().reindex(tidx)

		new_rdc = df0['discharge'].values
		new_tim = np.array([datetime.strptime(df0.index.format('utc')[1+i],\
									'%Y-%m-%d') for i in range(len(new_rdc))])

		new_tm  = date2num(new_tim,tm.units)
		new_rdc = np.ma.masked_array(new_rdc,np.isnan(new_rdc),fill_value=-999)
		idx0, = np.where(tim == new_tim[0])[0]
		idx1  = idx0+len(new_rdc)
		tm[idx0:idx1] = new_tm
		rdc[idx0:idx1,num] = new_rdc

history = 'created on : Tue May 15 18:31:45 2016.'
history = history + ' Last updated: {}.'.format(end_date.today().strftime('%a %b %d %H:%M:%S %Y'))
nc.setncattr('history', history)
nc.close()
