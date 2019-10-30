import numpy as np, pandas as pd, requests, os
from bs4 import BeautifulSoup
from netCDF4 import Dataset, num2date, date2num
from datetime import datetime, timedelta
from glob import glob

def check_number(number):
	try:
		return float(number.replace(',',''))
	except:
		return np.nan

fid = 'gom_discharge_1900_present.nc'
bkup= 'gom_discharge_1900_present_bkup_{}.nc'.format(datetime.today().strftime('%Y_%m_%d'))
os.system('cp {} {}'.format(fid,bkup))

try : 
	nc = Dataset(fid,'r+')
except:
	os.system('rm {}; cp {} {}'.format(fid, bkup,fid))
	nc = Dataset(fid,'r+')

tm = nc.variables['time']
tim = num2date(tm[:], tm.units)
rid= nc.variables['station_id'][:]
rid= [str(i,'ascii') for i in rid]
rdc= nc.variables['discharge']


for id in range(len(rid)):
	info_rdc = []; info_tim = []
	print('river id : ',rid[id][:5])
	if rid[id][:5] == '01100':
		fid = 'http://rivergages.mvr.usace.army.mil/WaterControl/shefgraph-historic.cfm?sid=01100Q'
		payload = {
		'fld_from1':tim[-60].strftime('%m/%d/%Y'),
		'fld_to1'  :datetime.today().strftime('%m/%d/%Y'),
		'fld_param':'QR','fld_type1':'Table'
		}

		for style in BeautifulSoup(requests.post(fid,data=payload).text,'lxml').select('.style3'):
			[date,time,data] = style.text.split()
			info_rdc.append(check_number(data)*0.028316847)
			info_tim.append(datetime.strptime(date,'%m/%d/%Y'))
			#print(datetime.strptime(date,'%m/%d/%Y'), check_number(data)*0.028316847)
	elif rid[id][:5] == '03045':
		fid = 'http://rivergages.mvr.usace.army.mil/WaterControl/shefgraph-historic.cfm?sid=03045Q'
		payload = {
		'fld_from1':tim[-60].strftime('%m/%d/%Y'),
		'fld_to1'  :datetime.today().strftime('%m/%d/%Y'),
		'fld_param':'QR','fld_type1':'Table'
		}

		for style in BeautifulSoup(requests.post(fid,data=payload).text,'lxml').select('.style3'):
			[date,time,data] = style.text.split()
			info_rdc.append(check_number(data)*0.028316847)
			info_tim.append(datetime.strptime(date,'%m/%d/%Y'))
	elif rid[id][:5] == 'FL252':
		fid='http://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&'
		begin_date='begin_date='+tim[-60].strftime('%Y-%m-%d')+'&'
		end_date='end_date='+datetime.today().strftime('%Y-%m-%d')+'&'
		site_no='site_no=252230081021300&referred_module=sw'
		fid = fid + begin_date+end_date+site_no
		for line in BeautifulSoup(requests.get(fid).text,'lxml').text.splitlines():
			if line[:4] == 'USGS':
				case = line.split()
				if len(case) >= 4:
					rtim = datetime.strptime(case[2],'%Y-%m-%d')
					try:
						new_discharge = check_number(case[3])*0.028316847
						if float(case[3]) > 0 : info_rdc.append(new_discharge)
						if float(case[3]) <=0 : info_rdc.append(0.)
						info_tim.append(rtim)
					except:
						pass
	else:
		fid='http://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&'
		begin_date='begin_date='+tim[-60].strftime('%Y-%m-%d')+'&'
		end_date='end_date='+datetime.today().strftime('%Y-%m-%d')+'&'
		site_no='site_no='+rid[id]+'&referred_module=sw'
		fid = fid + begin_date+end_date+site_no
		for line in BeautifulSoup(requests.get(fid).text,'lxml').text.splitlines():
			if line[:4] == 'USGS':
				case = line.split()
				if len(case) >= 4:
					rtim = datetime.strptime(case[2],'%Y-%m-%d')
					try:
						new_discharge = check_number(case[3])*0.028316847
						if float(case[3]) > 0 : info_rdc.append(new_discharge)
						if float(case[3]) <=0 : info_rdc.append(0.)
						info_tim.append(rtim)
					except:
						pass

	if len(info_tim) > 0 :
		dt = timedelta(days=1)
		timeindex = pd.date_range(tim[-60].strftime('%Y-%m-%d'), 
										  (datetime.today()).strftime('%Y-%m-%d'), freq='D')
										  #(datetime.today()-dt*1).strftime('%Y-%m-%d'), freq='D')
		df0 = pd.DataFrame(np.array(info_rdc), index=info_tim,columns=['discharge']).resample('D')
		df0 = df0.reindex(timeindex)
		new_rdc = df0['discharge'].values
		new_tim = np.array([datetime.strptime(df0.index.format('utc')[1+i],\
									'%Y-%m-%d') for i in range(len(new_rdc))])
		new_tm  = date2num(new_tim,tm.units)
		new_rdc = np.ma.masked_array(new_rdc,np.isnan(new_rdc),fill_value=-999)
		idx0, = np.where(tim == new_tim[0])[0]
		idx1  = idx0+len(new_rdc)
		tm[idx0:idx1] = new_tm
		rdc[idx0:idx1,id] = new_rdc
		nc.setncattr('history', 'created on : Tue Mar 15 18:31:45 2016, latest updated : '+
										 datetime.today().strftime('%a %b %d %H:%M:%S %Y'))
nc.close()
