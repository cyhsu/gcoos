#-- Mission 
#--    Purpose: Generated metadata info for each dataset
#--    Reason: For annual Report
#--    Request: Felimon Gayanilo [Felimon.Gayanilo@tamucc.edu]
#--    Request Date: 2021-05-13, Late Afternoon
#--    Completed Date: 2021-05-14
#--    Contributor: Chuan-Yuan Hsu [chsu1@tamu.edu; franke.cyhsu@gmail.com]
#--    CopyRight: @Chuan-Yuan Hsu, GCOOS, TAMU Oceanography
#--    Requirement: requests, pandas, BeautilfulSoup

import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

#-- User Interface
#--     Extract META-URLs from ERDDAP [GulfHub]
URL = 'http://gulfhub-data.gcoos.org/erddap/info/index.html?page=1&itemsPerPage=10000'

#--     META INFO REQUESTS
#--         This is attribute of metadata, you can add/remove based on your request
headers = [
  'datasetID',
  'acknowledgement',
  'cdm_data_type',
  'cdm_profile_variables',
  'cdm_timeseries_variables',
  'contributor_name',
  'creator_institution',
  'creator_name',
  'geospatial_lat_max',
  'geospatial_lat_min',
  'geospatial_lon_max',
  'geospatial_lon_min',
  'geospatial_vertical_max',
  'geospatial_vertical_min',
  'geospatial_vertical_positive',
  'geospatial_vertical_resolution',
  'geospatial_vertical_units',
  'instrument',
  'platform',
  'platform_name',
  'program',
  'project',
  'Southernmost_Northing',
  'standard_name_vocabulary',
  'station_type',
  'subsetVariables',
  'summary',
  'time_coverage_duration',
  'time_coverage_end',
  'time_coverage_resolution',
  'time_coverage_start',
  'title',
  'water_depth',
  'wmo_platform_code',
 ]

#-- Main Program
page= requests.get(URL)
soup= BeautifulSoup(page.text, 'html.parser')

#--   Start from index[1], since index[0] is "listAllDataset"
meta_urls = soup.find_all('a',
	{'rel':'chapter',
	 'rev':'contents',
	 'title':"Click to see a list of this dataset's variables and the complete list of metadata attributes.",
	})[1:]


#-  META-URLs to Pandas
Rows = []
for num, meta_url in enumerate(meta_urls):
  row = []
  url = meta_url.get_attribute_list('href')[0]

  #-- headers[0]
  row.append(url.split('/')[-2])

  #-- headers[1:]
  df = pd.read_html(url)[-1]
  for header in headers[1:]:
    try: 
      attribute=df[df['Attribute Name'] == header].Value.values[0]
      print(header, attribute)
      row.append(attribute)
    except:
      row.append('')

  if len(row) > 0:
    Rows.append(row)
    
dd = pd.DataFrame(Rows, columns=headers)

#- Pandas to Pretty Json
dd.to_json('GulfHub_dataID_attr_table.json', 
           orient='index',
           indent=2)
