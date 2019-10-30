import numpy as np
import requests

__author__ = 'C.Y. Hsu'

class subs:
	def check_number(number):
		try:
			return float(number.replace(',',''))
		except:
			return np.nan
	
	def with_exception(fid, payload=None):
		try: 
			r = requests.post(fid, data=payload, timeout=5)
			return 1
		except requests.exceptions.Timeout as errt:
			print( ' Error (Timeout): {}'.format(errt) )
			return 0 
		except requests.exceptions.ConnectionError as errc:
			print( ' Error (Connecting): {}'.format(errt) )
			return 0 
		except requests.exceptions.HTTPError as errh:
			print( ' Error (Http): {}'.format(errt) )
			return 0 
	
