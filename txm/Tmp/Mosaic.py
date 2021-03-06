#!/usr/bin/env python


######## User input #######
ThePath = 'C:\\epics\\data\\Manip\\201310\\Fitt\\EF02\\'
Start_pos_Mos_X = 487.5
Start_pos_Mos_y = 4

##########################





# starting position:
import Mosaic as mos
PV_ThePath = 'XF:05ID-ES:X2B{Cam:1}TIF:FilePath'
PV_samx = 'XF:05ID1-ES:X2B{Stg:XY-Ax:X}Mtr'
PV_samy = 'XF:05ID1-ES:X2B{Stg:XY-Ax:Y}Mtr.VAL'

caput(PV_ThePath, ThePath, datatype=DBR_CHAR_STR, wait=True)	# set the path where the data will be saved
caput(PV_samx, Start_pos_Mos_X, wait=True, timeout=500)					# move samx for the dark field acquisition
caput(PV_samy, Start_pos_Mos_y, wait=True, timeout=500)					# move samx for the dark field acquisition


################ Start of the mosaic funtion

def mosaic(nCol, nRow, hor_mos_step, vert_mos_step, dwell_rad, nRad, dwell_ff, nff, ff_pos, df_pos, sleeptime, total_time_acq, ThePath):

#
#   Command for test: mosaic(3, 5, 2.5, 2.5, 0.4, 3, 0.18, 2, [14, 504], [8,504], 10, 22, ThePath)

#   script: mosaic(nCol, nRow, hor_mos_step, vert_mos_step, dwell_rad, nRad, dwell_ff, nff, ff_pos, df_pos, sleeptime, total_time_acq, ThePath)
#		nCol: # of colomns in the mosaic
#		nRow: # of row in the mosaic
#		hor_mos_step: horizontal step of the sample stage for the mosaic acquisition (mm)
#		vert_mos_step: vertical step of the sample stage for the mosaic acquisition (mm)
#		dwell_rad: dwell time for the radio in seconds
#		dwell_ff: dwell time for the flat fields in seconds
#		ff_pos: location of samx for flat field acquisitions
#		df_pos: location of samx for dark field acquisitions
#		sleeptime: pause length after each mosaic (minutes)
#		total_time_acq: overall time above which the scan stop (hours)
#		ThePath: 

	start = time.time()	# trigger the clock
	
	# PV declaration:
	PV_samx = 'XF:05ID1-ES:X2B{Stg:XY-Ax:X}Mtr'
	PV_samy = 'XF:05ID1-ES:X2B{Stg:XY-Ax:Y}Mtr.VAL'
	PV_dwelltime = 'XF:05ID-ES:X2B{Cam:1}AcquireTime'
	PV_prefix = 'XF:05ID-ES:X2B{Cam:1}TIF:FileName'			# 
	PV_radio_index = 'XF:05ID-ES:X2B{Cam:1}TIF:FileNumber'	# next file index
	PV_trigger = 'XF:05ID-ES:X2B{Cam:1}Acquire'
	PV_save = 'XF:05ID-ES:X2B{Cam:1}TIF:WriteFile'
	
	# Create variables:
	curr_samx_pos = caget(PV_samx)				# get the current horizontal sample position
	curr_samy_pos = caget(PV_samy)				# get the current vertical sample position
	
	sleeptime = sleeptime * 60					# conversion of sleeptime from minutes to seconds
	total_time_acq = total_time_acq * 3600		# conversion of total acqu time from hours to seconds
	
	# CCD parameters:
	nHPix = 2560
	nVPix = 2160
	PixSize = 6.5
	Mag = 5
	
	# Vectors position:
#	X_coord = linspace(curr_samx_pos, curr_samx_pos + (nCol-1)*nHPix*PixSize/Mag, nCol)
#	Y_coord = linspace(curr_samy_pos, curr_samy_pos + (nRow-1)*nVPix*PixSize/Mag, nRow)
	X_coord = linspace(curr_samx_pos, curr_samx_pos + hor_mos_step * (nCol-1), nCol)
	Y_coord = linspace(curr_samy_pos, curr_samy_pos + vert_mos_step * (nRow-1), nRow)
	
	# Dark field acquisitions
	caput(PV_samx, df_pos[1], wait=True, timeout=500)					# move samx for the dark field acquisition
	caput(PV_samy, df_pos[0], wait=True, timeout=500)					# move samx for the dark field acquisition
	caput(PV_dwelltime, dwell_ff, wait=True, timeout=500)						# set the dwell time of the snapshot
	caput(PV_trigger, 1, wait=True, timeout=500)						# trigger the snapshot
	print '*** dark field acq with ff dwell time'
	FileName = 'Mosaic_df_forff_%ims' % (dwell_ff*1000)								# create the file name for the dark field
	caput(PV_prefix, FileName, datatype=DBR_CHAR_STR, wait=True, timeout=500)	# create the file name for the next snapshot saving
	caput(PV_save, 1, wait=True, timeout=500)									# save the dark field snapshot

	caput(PV_dwelltime, dwell_rad, wait=True)						# set the dwell time of the snapshot
	caput(PV_trigger, 1, wait=True, timeout=500)									# trigger the snapshot
	print '*** dark field acq with radio dwell time'
	FileName = 'Mosaic_df_forRad_%ims' % (dwell_rad*1000)					# create the file name for the dark field
	caput(PV_prefix, FileName, datatype=DBR_CHAR_STR, wait=True, timeout=500)	# create the file name for the next snapshot saving
	caput(PV_save, 1, wait=True, timeout=500)									# save the dark field snapshot


	iMos = 0
	continu = 1
	while continu:
		iMos+=1
		print ' '
		print '#### Mosaic number %i ####' % iMos
		print ' '
		
		# Flat field acquisitions (1 / mosaic)
		caput(PV_samx, ff_pos[1], wait=True, timeout=500)						# move samx for the flat field acquisition
		caput(PV_samy, ff_pos[0], wait=True, timeout=500)						# move samx for the flat field acquisition
		caput(PV_dwelltime, dwell_ff, wait=True, timeout=500)						# set the dwell time of the snapshot
		ff_count=0
		for iff in range(1, nff+1):
			ff_count+=1
			print '*** ff acq %i' % iff
			FileName = 'Mosaic_ff_%i_%i' % (iMos, iff)
			caput(PV_trigger, 1, wait=True, timeout=500)									# trigger the snapshot
			caput(PV_prefix, FileName, datatype=DBR_CHAR_STR, wait=True, timeout=500)	# create the file name for the next snapshot saving
			caput(PV_save, 1, wait=True, timeout=500)									# save the flat field snapshot

		# Start the mosaic acquisition
		for iRow in range(1, nRow+1):
			caput(PV_samy,  Y_coord[iRow-1], wait=True, timeout=500)
			print '*** move samy ', Y_coord[iRow-1]

			for iCol in range(1, nCol+1):
				caput(PV_samx,  X_coord[iCol-1], wait=True, timeout=500)
				print '*** move samx ', X_coord[iCol-1]
				caput(PV_dwelltime, dwell_rad, wait=True, timeout=500)						# set the dwell time of the snapshot
				radio_count = 0
				for iRad in range(1, nRad+1):
					radio_count+=1
					caput(PV_trigger, 1, wait=True, timeout=500)					# trigger the snapshot
					print '*** col %i row %i ; radio acq %i' % (iCol, iRow, iRad)
					FileName = 'Mosaic_%i_%i_%i_%i' % (iMos, iRow, iCol, iRad)
					caput(PV_prefix, FileName, datatype=DBR_CHAR_STR, wait=True, timeout=500)	# create the file name for the next snapshot saving
					caput(PV_save, 1, wait=True, timeout=500)									# save the snapshot for the radio

		elapsed = (time.time() - start)		# calculate elapsed time after each mosaic
		if elapsed >= total_time_acq:		# check the total acq time has not elapsed
			continu=0						# if elapsed, the loop while is killed
		print '*** In pause for %i minutes' % (sleeptime/60)
		time.sleep(sleeptime)
		
	caput(PV_samx, df_pos[1], wait=True, timeout=500)					# move samx for the dark field acquisition
	caput(PV_samy, df_pos[0], wait=True, timeout=500)					# move samx for the dark field acquisition

		


