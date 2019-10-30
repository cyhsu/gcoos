import numpy as np, requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from models.subs import subs

__author__='C.Y. Hsu'

class usgs:
	def __init__(self, station_id, begin_date, end_date=datetime.today()):
		self.link = 'http://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&'
		self.station_id = station_id
		self.begin_date = begin_date
		self.end_date = end_date
		self.ncout = 0

	def payload(self):
		begin_date='begin_date={}&'.format(self.begin_date.strftime('%Y-%m-%d'))
		end_date='end_date={}&'.format(self.end_date.strftime('%Y-%m-%d'))
		if self.station_id[:5] == 'FL252':
			site_no='site_no=252230081021300&referred_module=sw'
		else:
			site_no='site_no={}&referred_module=sw'.format(self.station_id)
		return self.link+begin_date+end_date+site_no, None
	
	def bs4(self):
		fid, payload = self.payload()
		self.ncout = subs.with_exception(fid,payload)
		odata, odate = [], []
		if self.ncout != 0:
			r = requests.post(fid, data=payload, timeout=5)
			for line in BeautifulSoup(r.text,'lxml').text.splitlines():
				if line[:4] == 'USGS':
					case = line.split()
					if len(case) >= 4:
						odata.append( subs.check_number(case[3])*0.028316847 )
						odate.append( datetime.strptime(case[2],'%Y-%m-%d') )
		return self.ncout, odate, odata
	

if __name__ == '__main__':
	from datetime import datetime
	check = usgs('08068000',datetime(2019,4,10))
	#check = usgs('252230081021300',datetime(2019,4,10))
	a,b,c, = check.bs4()
	print('begin_date', check.begin_date)
	print('end_date', check.end_date)
	print('ncout', a)
	print( [ (b[i1],c[i1]) for i1 in range(len(b))] )
