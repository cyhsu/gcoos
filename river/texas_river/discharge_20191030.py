import numpy as np, requests
import matplotlib.pyplot as plt, pandas as pd
import cartopy.crs as ccrs, cartopy.feature as cf
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

plt.style.use('seaborn-paper')										

#--------------------------------------------------------------
#----- Modifying your datetime here.                      -----
#--------------------------------------------------------------

download_date_starts_at = '2017-07-01'
download_date_ends_at = '2017-11-30'


#--------------------------------------------------------------
#--------------------------------------------------------------

#- Function
def check_number(number):											
	try:				
		return float(number.replace(',',''))			 
	except:
		return np.nan									

#- Parameters											
bdate = 'begin_date={}&'.format(download_date_starts_at)		#- begin date of the data flow  
edate = 'begin_date={}&'.format(download_date_ends_at)		#- end date of the data flow
pdtim = pd.date_range(start=download_date_starts_at,
							 end=download_date_ends_at,
							 freq='15min')

####-bdate = 'begin_date=2017-07-01&' #- begin date of the data flow										
####-edate = 'end_date=2017-11-30&' #- end date of the data flow											
####-pdtim = pd.date_range(start='2017-07-01', end='2017-11-30',
####-							 freq='15min')
			
#- Main Code		 
site_so, site_no, site_ds = [], [], []
with open('specific-river') as fid:								
	for num, line in enumerate(fid.readlines()):		 
		spin = line.split(':')
		site_so.append(':'.join(spin[:-1]))
		site_no.append(spin[-1].split(',')[0].strip())
		site_ds.append(' '.join(spin[-1].split(',')[1:]).strip())

geoinfo_link = 'https://waterdata.usgs.gov/nwis/inventory/?site_no={:s}&agency_cd=USGS'
site_link = 'http://nwis.waterdata.usgs.gov/tx/nwis/uv/?cb_00060=on&format=rdb&'
site_link = site_link + bdate + edate + 'site_no={}&referred_module=sw'
sites = {}			
for num_no, no in enumerate(site_no):		
	a = requests.get(geoinfo_link.format(no))	
	for num, line in enumerate(BeautifulSoup(a.text,'lxml').find_all('div',
	 									{'id':'stationTable'})[0].text.splitlines()):
		if	'Latitude' in line :
			strings = line.split()
			lat = float(strings[1][:-1][:2]) + \
		 		float(strings[1][:-1][3:5])/60. + \
		 		float(strings[1][:-1][6:8])/3600. 
			lon = float(strings[3][:-1][:2]) + \
		 		float(strings[3][:-1][3:5])/60. + \
		 		float(strings[3][:-1][6:8])/3600.; 
			lon = -1. * lon
			print('{}, {:.02f}, {:.02f}'.format(no, lat, lon)) 
			break		
	
	
	fid = site_link.format(no)
	print('site information link: {}\n'.format(fid))

	rat, tim = [], []	
	a = requests.get(fid)

	#-- if the website is existed, 
	#-- 	start to work on the site by BeautifulSoup.
	if not 'No sites' in a.text:
		for line in BeautifulSoup(a.text,'lxml').text.splitlines():					 
			if line[:4] == 'USGS':									
				strings = line.split()	
				if len(strings) >= 4:					 
					tim.append(datetime.strptime(strings[2] + ' ' + strings[3],
															'%Y-%m-%d %H:%M'))
					rate = check_number(strings[5]) * 0.028316847										
					rat.append( rate ) 
	
		####--- If sum of the river discharge is larger than 0, seeing whether there is inflow ( Negative Discharge Rate)
		###if np.nansum(rat) > 0:
		###	if np.where( np.array(rat) < 0.): print('Negative Discharge Rate is existed') 
			
		sites[no] = {'lon' : lon, 'lat' : lat, 'id' : no,
						 'description':site_ds[num_no], 'reservoir': site_so[num_no], 
						 'data':{'date': tim, 'discharge': rat}}
						
	#	if num_no == 2: break	

np.savez('discharge_{}-{}.npz'.format(download_date_starts_at, 
												  download_date_ends_at),
			sites = sites)

####--- 
### np.savez('discharge_20170701-20171130.npz',sites = sites)

import xarray as xr
ds = []
for num, key in enumerate(sites.keys()):
	df = pd.DataFrame.from_dict(sites[key]['data']).drop_duplicates(['date']).set_index('date').reindex(pdtim)
	df = xr.Dataset.from_dataframe(df)
	df['lon'] = sites[key]['lon']
	df['lat'] = sites[key]['lat']
	df['site_id'] = sites[key]['id']
	df['reservoir'] = sites[key]['reservoir']
	df['site_name'] = sites[key]['description']
	df = df.expand_dims('sites')
	ds.append( df )

ds = xr.concat(ds,'sites')
ds.to_netcdf('river_discharge_in_texas.nc')
	

####--- print-out test.
###for no in range(ds.site_id.size): 
###	pds = ds.isel(sites=no) 
###	sid = pds.site_id.data.item().strip() 
###	slon= pds.lon.data 
###	slat= pds.lat.data 
###	voir= ': '.join(np.flip(pds.reservoir.data.item().split(':'))).strip() 
###	name= pds.site_name.item().strip() 
###	tim1= pds.sel(index=slice('2017-08-25','2017-09-04')).discharge.sum().data 
###	tim2= pds.sel(index=slice('2017-09-05','2017-09-28')).discharge.sum().data 
###	tim3= pds.sel(index=slice('2017-09-29','2017-11-07')).discharge.sum().data 
###	print('{:50s}, {:8s}, {:8.3f}, {:8.3f}, {:12.3f}, {:12.3f}, {:12.3f}, {}'.format(name, 
###	      sid, slon, slat, tim1, tim2, tim3, voir)) 

