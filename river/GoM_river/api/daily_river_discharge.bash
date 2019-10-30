#!/bin/bash
source /Users/cyhsu/conda/bin/activate nco

CWD='/Users/cyhsu/dev/river/api'
PNG='/Users/cyhsu/dev/river/api/png'
TXT='/Users/cyhsu/dev/river/api/ascii'
BUP='/Users/cyhsu/dev/river/api/bkup'

if [ ! -d "${PNG}" ]; then 
	echo "png file in ${PNG} is not existed"
	echo "...Create one now..."
	mkdir ${PNG}
fi

cd ${CWD}

echo " " >> ./tmp/GCTest.out; echo " " >> ./tmp/GCTest.out; echo " " >> ./tmp/GCTest.out
date >> ./tmp/GCTest.out
echo "convert online data to nc" >> ./tmp/GCTest.out
ipython ${CWD}/api_webcrawler.py >> ./tmp/GCTest.out

echo "convert nc data to ascii" >> ./tmp/GCTest.out 
#ipython ./api_nc2txt.py
ipython ${CWD}/river_nc2ascii_individual.py

date > ./tmp/png.out
echo "plotting the dataset...." >> ./tmp/png.out
echo "river_daily_annual_plot.py should be working" >> ./tmp/png.out
ipython ./river_daily_annual_plot.py >> ./tmp/png.out

tar zcf ./gomriver2.tar.Z ./ascii

#- moving bkup netcdf file to bkup directory
mv *bkup*nc ${BUP}

#- leaves time stamp for record.
date >> ${CWD}/tmp/GCTest.out

#- System check
date >> ./River_System_Test

#conda /Users/cyhsu/conda/bin/deactivate
exit
