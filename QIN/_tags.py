
try:
	from tactic_client_lib import TacticServerStub
	import logging
	from TObject import *
	from Exam import *
	from Series import *
	import Subject
	import time
except ImportError:
	print  "error"

class clinicaltags(object):
	""" Basic generic class to add and delete tags from TACTIC.

	TAGs can be associated with a Subject, a Series, or an Exam level contained in TACTIC.

	This class will give the ability to add, delete, update and get the TAGs from each level.

	Keep in mind TAGS are basically python dictionaries. 


	Parameters: 

	codetype: Code type can be one of the following.
				exam_code
				subject_code
				series_code
				search_key
	level: Level can be (based on our Tactic Schema).
				Subject
				Exam
				Series
	Project: Project name.
				default qin
	allowed: A dictionary containing all the allowed tags for the projects included inside tactic. Class should provide basic documentations for Allowed values and TAG names."""
	logger = logging.getLogger('TAGS')
	logger.setLevel(logging.INFO)
	# create file handler which logs even debug messages
	# create console handler with a higher log level
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	# add the handlers to the logger
	logger.addHandler(ch)
	logger.info('---------------------------------')
	logger.info('Date %s'%time.strftime("%d/%m/%Y"))
	logger.info('Time %s'%time.strftime("%H:%M:%S"))
	logger.info('---------------------------------')
	logger.info('Start ')
	## This is a dictionary of the available TAGs in TACTIC
	allowed={'Panos', 'test'}
	server = TacticServerStub()
		
	def __init__(self, name, value, code):
		self.name=name
		self.value=value
		self.code=code
		self.server = TacticServerStub()

	def getTag(self):
		if self.name in self.allowed:
			Subject1=self.server.get_by_search_key( self.code )
			return  Subject1.tags
		else :
			logger.info('The value %s is not allowed '% self.vale)
	def delTag(self):
		Subject1=self.server.get_by_search_key( self.code )
		Subject1[0].tagspop(self.name, None)
		Subject1[0].save()
		return 0
	def addTag(self):
		if self.name in self.allowed:
			Subject1=server.get_by_search_key( self.code )
			Subject1[0].tags.update({self.name:self.value})
			Subject1[0].save()
		else :
			logger.info('The value %s is not allowed '% self.vale)
	def updateTag(self):
		if self.name in self.allowed:
			Subject1=server.get_by_search_key( self.code )
			Subject1[0].tags.update({self.name:self.value})
			Subject1[0].save()
			return 0
		else :
			logger.info('The value %s is not allowed '% self.vale)

"""
Example:

from  _tags import clinicaltags
tag1=clinicaltags('Panos', '0','qin/subject?project=qin&code=SUBJECT00515' )
tag1.getTag()

"""


