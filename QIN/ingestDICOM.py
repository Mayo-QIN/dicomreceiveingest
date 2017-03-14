#!/bin/env python

import sys, math, shutil
import os.path, glob, uuid, re
import subprocess, tempfile, datetime, traceback
import xml.etree.ElementTree as ET
from optparse import OptionParser
import ConfigParser
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

import qin

# Some help here
# Injest a single series
# ./ingestDICOM.py /qia/projects/ImageLinks/MRA-0201/MR_20070116/0004_TOF-3D_VBI_1.04MM-5-SLAB/

# Ingest a bunch of records
# find /research/images/links/ -type d -print0 | xargs -n 1 --max-procs 1 -0 ./ingestDICOM.py --db /research/images/ingested_into_tactic.db
# find /research/images/Notion/ImageStorage/2/sorted/16479588-1/  -type d -print0 | xargs -n 1 --max-procs 1 -0 ./ingestDICOM.py --f --t ingest.config 
# find /research/images/Notion/ImageStorage/2/sorted/*  -type d -mtime -1 -print0 | xargs -n 1 --max-procs 1 -0 ./ingestDICOM.py --f --t ingest.config 
# find /research/RILProcessing/ -type d -print0 | xargs -n 1 --max-procs 1 -0 ./ingestDICOM.py --db gbm.db --t ingest.config 
# find /research/images/Notion/ImageStorage/2/sorted/*  -type d -mtime -4 -print0 | xargs -n 1 --max-procs 1 -0 ./ingestDICOM.py --f --t QINdemo.config 
# print "here"

def makeFilename ( name ):
	"""Replace bad characters to make a safe filename"""
	# Spaces, parens and slashes are useful to have as underscores
	fn = name
	fn = re.sub ( "[ /()]", "_", fn )
	# Anything else gets removed
	fn = re.sub ( "[^0-9a-zA-Z._-]", "", fn )
	# Replace __ with _
	fn = re.sub ( "_+", "_", fn )
	return fn



class ingest:
	"""ingest DICOM images, creating the proper structure in TACTIC"""
	def __init__ ( self, options, config=None ):
		self.context = "image"
		self.today = date.today().strftime ( "%Y%m%d" )
		self.options = options
		print self.options
		self.config = config
		if self.options.db:
			self.db = qin.sqlDict ( self.options.db )
		else:
			self.db = qin.sqlDict ( tempfile.mktemp())

	def ingest ( self, filename ):
		# print filename
		self.directory = filename
		if filename in self.db:
			return
			
		self.stageDirectory = tempfile.mkdtemp ( prefix="ingestDICOM-" )
		# Find the middle one
		DICOMFiles = glob.glob ( os.path.join ( self.directory, "*" ) )
		DICOMFiles = sorted ( DICOMFiles )
		# print DICOMFiles
		if len(DICOMFiles) < 1:
			# print "----- No DICOM files found, skipping %s" % self.directory
			self.db[filename] = "skipped on %s" % datetime.datetime.now()
			return
		self.DICOMFile = DICOMFiles[math.trunc(len(DICOMFiles)/2.0)]
		self.DICOMFiles = DICOMFiles

		self.loadTags()
		self.createSubject()
		print "Finished creating subject!"
		self.db[filename] = "completed on %s" % datetime.now()
	
	def cleanup ( self ):
		"""Remove the temporary directory"""
		if hasattr ( self, "stageDirectory" ) and os.path.exists (self.stageDirectory):
			shutil.rmtree ( self.stageDirectory )

	def loadTags ( self ):
		self.tagFile = os.path.join ( self.stageDirectory, "tags.xml" )
		status = subprocess.call ( ["/qia/software/bin/dcm2xml", self.DICOMFile, self.tagFile] )

		self.tagTree = ET.parse ( self.tagFile )
		root = self.tagTree.getroot()
		self.tags = { "Modality": "Unknown", 
					  "StudyDate": self.today, 
					  "SeriesDate": self.today, 
					  "SeriesDescription": "Unknown", 
					  "StudyDescription": "Unknown", 
					  "SeriesNumber": str(uuid.uuid4()) }
		# Make a dictionary of tags
		for node in root.findall ( "./data-set/element" ):
			# Ignore binary or hidden tags
			if node.get("binary") != "hidden":
				# print "Found " + node.get("name") + ":" + str(node)
				self.tags[node.get("name")] = node.text or "Unknown"
		for key in self.tags.keys():
			if "Patient" in key:
				sKey = key.replace ( "Patient", "Subject")
				self.tags[sKey] = self.tags[key]
									   
		# print "Tags loaded"

	def createSubject ( self ):
		"""Insert a subject into the TACTIC database using the stored connection info.
		Subjects indexed by their subject id from the DICOM images"""
		from tactic_client_lib import TacticServerStub

		if self.config:
			print self.config.sections()
			if "TACTIC" in self.config.sections():
				self.server = TacticServerStub(server=config.get("TACTIC", "server"), project=config.get("TACTIC", "project"), user=config.get("TACTIC", "user"), password=config.get("TACTIC", "password"))
		else:
			self.server = TacticServerStub()
		# Insert Subject
		obj = { 'name': self.tags["PatientName"],
				'description': self.tags["PatientID"],
				'subjectname': self.tags["PatientName"],
				'subjectid': self.tags["PatientID"],
				'subjectsex': self.tags['PatientSex'],
				'subjectbirthdate': self.tags["PatientBirthDate"],
				'safename' : makeFilename ( self.tags["PatientName"] ) }


		data = self.matchTags ( "qin/subject", obj )
		if data['subjectbirthdate'] and data['subjectbirthdate']=='Unknown':
			# Tactic does not like when Subject birthdate is unknown 
			# We are going to use the study date - age in years to fill in an approximate patient birthday date
			StudyDate=self.tags['StudyDate']
			if 'PatientAge' in self.tags:
				AgeInYears=self.tags['PatientAge']
			else:
				AgeInYears='001Y'
			# Calculate aprrroximate birthdate
			AgeInYears=AgeInYears[1:2]
			AgeInYears=int(float(AgeInYears))
			d = datetime.strptime(StudyDate, '%Y%m%d')
			years_ago = d - relativedelta(years=AgeInYears)
			# save this back to the subject objext 
			data['subjectbirthdate'] =years_ago.strftime('%Y%m%d')
		self.subject = qin.Subject ( data, server=self.server )

		# Create the Exam
		name = self.tags["Modality"] + "_" + self.tags["StudyDate"]
		data = self.matchTags ( "qin/exam", { 'name': name, 'description': self.tags["StudyDescription"], 'safename' : makeFilename ( name ) } )
		self.exam = self.subject.createExam ( data )
		
		try:
			seriesNumber = "{0:04d}".format ( int ( self.tags["SeriesNumber"] ) )
		except:
			seriesNumber = "9999"
		name = seriesNumber + "_" + self.tags["SeriesDescription"]

		data = self.matchTags ( "qin/series", { 'name' : name, 'description' : self.tags["SeriesDescription"], 'protocolname' : 'empty', 'safename' : makeFilename ( self.tags["SeriesDescription"] ) } )
		self.series = self.exam.createSeries ( data )

		# Set any tags
		if self.config:
			for section, item in zip( ["Subject", "Exam", "Series"], [self.subject, self.exam, self.series]):
				if section in self.config.sections():
					for key in self.config.options(section):
						item.tags[key] = self.config.get(section, key)
					item.save()

		if self.series.getFilenameForContext ( self.context ) and not self.options.force:
			print "\t--- Image data exists"
		else:
			self.convertDICOM ( )

			# Upload the files using snapshots so TACTIC des the right thing in making versions
			# eg checkin = server.simple_checkin ( bucket.get('__search_key__'), 'publish', './bucket.py', mode='upload', create_icon=False, checkin_type='auto' )
			if not self.series.getFilenameForContext ( self.context ):
				self.series.checkinFile ( self.context, self.niiFile )
			if not self.series.getFilenameForContext ( "tags" ):
				self.series.checkinFile ( 'tags', self.tagFile )
			if not self.series.getFilenameForContext ( "icon" ):
				self.series.checkinFile ( 'icon', self.previewFile )
		

# Filename stuff
# i.server.eval ( "@GET(qintp/series.qintp/exam.code)" )

	def convertDICOM(self):
		"""Ingest a DICOM series pointed to by dirname"""
		dirname = self.directory
		niiDir = os.path.join ( self.stageDirectory, "nii" )
		dicomDir = os.path.join ( self.stageDirectory, "dicom" )
		os.makedirs ( dicomDir )
		if os.path.isdir ( niiDir ):
			return
		try:
			os.makedirs ( niiDir )
		except:
			print "Could not create %s directory" % niiDir
			return

		for filename in glob.glob(os.path.join(dirname, '*')):
			shutil.copy(filename, dicomDir)

		self.niiFile = os.path.join ( niiDir, "original.nii.gz" )
		self.voiFile = os.path.join ( niiDir, "original.voi.nii.gz" )
		convert = os.path.join ( self.stageDirectory, 'convert.lua' );
		fid = open ( convert, 'w' )
		
		fid.write ( "i = LoadImage ( '%s' ); SaveImage(i,'%s');\n" % (dicomDir, self.niiFile) )
		# Save a VOI
		fid.write ( "voi = MI3C.Image ( i ); voi:setAllVoxels(0.0); SaveImage(i,'%s');\n" % (self.voiFile,) )

		fid.close()
		command = "/qia/software/bin/iMI3C %s" % convert
		status = subprocess.call ( command, shell=True )
		if status != 0:
			# Try with dcmtonii
			status = subprocess.call ( "/qia/software/mricron/dcm2nii -o %s -4 y -a y -d n -e n -f y -g y -p n -i n -r n -x n %s" % (niiDir, dicomDir), shell=True )
			print 'Finished convert with status', status
			niiFiles = glob.glob ( os.path.join ( niiDir, "*.nii.gz" ) )
			self.niiFile = os.path.join ( niiDir, "original.nii.gz" )
			os.rename ( niiFiles[0], self.niiFile )
			subprocess.call ( "/bin/touch %s" % self.voiFile, shell=True )
		# Make an preview
		self.previewFile = os.path.join ( self.stageDirectory, "icon.jpg" )
		pngFile = os.path.join ( self.stageDirectory, "icon.png" )
		status = subprocess.call ( ["/qia/software/bin/dcm2pnm", "--histogram-window", "1", "--write-png", self.DICOMFile, pngFile] )
		status = subprocess.call ( ["/research/SWExternal/ImageMagicK/bin/convert", pngFile, self.previewFile] )
	
	def matchTags ( self, searchType, defaults={} ):
		validColumns = self.server.get_column_names ( searchType )
		for key in validColumns:
			# print "Found column %s" % key
			pass
		matched = defaults
		for key in self.tags.keys():
			if key.lower() in validColumns and key in self.tags and self.tags[key]:
				# print "\tMatched %s" % key.lower()
				matched[key.lower()] = self.tags[key]
		return matched
			

if __name__ == "__main__":
	parser = OptionParser ( usage='usage: %prog [options] <SeriesDirectory1> [<SeriesDirectory2>] ' )
	parser.add_option ( "-f", "--force", default=None, action="store_true", help="Force new files to be written" )
	parser.add_option ( "-d", "--db", help="filename of the SQLite3 db.  DB stores already uploaded series" )
	parser.add_option ( "-t", "--tags", help="filename of the INI-style config file.  Tag/value pairs are added at each level, [Subject], [Exam], [Series]" )

	(options, args) = parser.parse_args()
	if len(args) < 1:
		parser.print_help()
		sys.exit(1)

	config = None
	if options.tags:
		config = ConfigParser.ConfigParser()
		config.read ( options.tags )

	i = ingest(options, config=config)
	for path in args:    
		if os.path.exists(path) and os.path.isdir(path):
			try:
				i.ingest ( path )
				i.cleanup ()
			except Exception, e:
				print "Failed to process %s" % path
				print traceback.print_exc()
		else:
			print ( 'path: %s is not a directory' % path )




