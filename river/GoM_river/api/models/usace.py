import numpy as np, requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from models.subs import subs

__author__='C.Y. Hsu'

class usace:
	def __init__(self, station_id, begin_date, end_date=datetime.today()):
		self.link = 'http://rivergages.mvr.usace.army.mil/WaterControl' 
		self.station_id = station_id
		self.begin_date = begin_date
		self.end_date = end_date
		self.ncout = 0

	def payload(self):
		fid = self.link+'/shefgraph-historic.cfm?sid={}Q'.format(self.station_id)
		payload = {	'fld_from1':self.begin_date.strftime('%m/%d/%Y'),
						'fld_to1'  :self.end_date.strftime('%m/%d/%Y'),
						'fld_param':'QR','fld_type1':'Table' }
		return fid, payload
	
	def bs4(self):
		fid, payload = self.payload()
		self.ncout = subs.with_exception(fid, payload)
		odata, odate = [], []
		if self.ncout != 0:
			r = requests.post(fid, data=payload, timeout=5)
			#for style in BeautifulSoup(r.text,'lxml').select('.style3'):
			for style in BeautifulSoup(r.text,'html.parser').select('.style3'):
				#print(style.text.split()[:3])
				[date, time, data] = style.text.split()[:3]
				odata.append( subs.check_number(data)*0.028316847 )
				odate.append( datetime.strptime(date,'%m/%d/%Y') )

		return self.ncout, odate, odata


if __name__ == '__main__':
	from datetime import datetime
	check = usace('01100',datetime(2019,2,16))
	#check = usace('03045',datetime(2019,2,16))
	a,b,c, = check.bs4()
	#for i1 in range(len(b)): print(b[i1], c[i1])
