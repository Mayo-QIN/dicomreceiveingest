from tactic_client_lib import TacticServerStub
import util
import logging
import datetime


class TObject(object):
	logger = logging.getLogger ( 'TObject' )

	"""Search and return a list of subjects"""
	@classmethod
	def search ( cls, expression=None, filters=[], server=None ):
		TObject.logger.debug ( "Search with cls: {}, expression: {} filters: {}".format(cls,expression,filters) )
		server = server or TacticServerStub()
		columns = server.get_column_names ( cls.stype )
		if expression != None:
			TObject.logger.debug ("Evaluating expression {}".format(expression))
			objects = server.eval ( expression )
		elif filters != None:
			TObject.logger.debug ("Filtering with {}".format(filters))
			objects = server.query ( cls.stype, filters=filters, columns=columns )
		
		return [ cls(data=x,server=server) for x in objects ]

	@classmethod
	def getBySearchKey ( cls, search_key, server= None):
		server= server or TacticServerStub()
		clinTags=server.get_by_search_key(search_key)
		return cls(data=clinTags, server=server)


	"""Create a new Subject, must have a Patient ID which will be created as needed."""
	def __init__ ( self, data, server=None ):
		if not data:
			raise "Must set data for the exam"
		self.server = server or TacticServerStub()

		self.data = data
		self.__dict__.update (data)
		self._tags = None

	def _createTag(self,tag):
		if len(tag['text_value']):
			# print' __________________________________________________________________text found'

			self._tags[tag['key']] = tag['text_value']
		else:
			# print' _________________________________________________________________valey found'

			self._tags[tag['key']] = tag['numeric_value']
		# _tag_keys is a dict of tuples to search key and original value
		self._tag_keys[tag['key']] = (tag['__search_key__'], self._tags[tag['key']] )

	"""Get the objects info"""
	@property
	def tags(self):
		if not self._tags:
		  self._tags = {}
		  self._tag_keys = {}
		  tags = self.server.get_all_children(self.__search_key__, self.stype + "_info" )
		  for tag in tags:
			self._createTag ( tag )
		return self._tags

	"""Create an object from a search key"""
	@classmethod
	def fromKey ( cls, key, server=None ):
		server = server or TacticServerStub()
		object = server.get_by_search_key ( key )
		return cls(data=object, server=server)

	@classmethod
	def create ( stype, data, parent_key=None, server=None ):
		server = server or TacticServerStub()
		return server.insert ( stype, data, parent_key=parent_key )

	"""Write the object back into tactic"""
	def save ( self ):
		data = self.data.copy()
		for key in data.keys():
			if key != "__search_key__" and key != "data":
				data[key] = self.__dict__[key]
			if data[key] == None:
				data.pop ( key, None)
		# Remove the status, if present
		data.pop ( 's_status', None)
		self.data = self.server.update ( self.__search_key__, data=data )
		# util.createOrUpdate ( self.server, self.stype, data, self.getSearchFilter() )
		# Save our tags
		if self._tags:
			for key in self._tags.keys():
				data = { 'key': key}    
				if isinstance(self._tags[key], float) or isinstance(self._tags[key], int):
					data['numeric_value'] = self._tags[key]
				else:
					data['text_value'] = self._tags[key]                    
				# Entry in _tag_keys
				if key in self._tag_keys:
					# did it change?
					if self._tags[key] != self._tag_keys[key][1]:
						# Save it back
						self.server.update ( self._tag_keys[key][0], data=data )
				else:
					# Added later
					tag = self.server.insert ( self.stype + "_info", data, parent_key=self.__search_key__)
					self._createTag ( tag )


	"""Return a list of snapshots"""
	def getSnapshots ( self ):
		snapshots = self.server.get_all_children ( self.__search_key__, 'sthpw/snapshot', filters=[('is_current', True)] )
		self.snapshots = [TObject(snapshot, server=self.server) for snapshot in snapshots]
		return self.snapshots 

	def getContextMap ( self ):
		self.getSnapshots();
		self.context = {}
		for snapshot in self.snapshots:
			self.context[snapshot.context] = snapshot
		return self.context

	def getFilenameForContext ( self, context ):
		self.getContextMap()
		if not self.context.has_key ( context ):
			return None
		paths = self.server.get_paths ( self.__search_key__, context=context, version=-1, file_type='*', versionless=True)
		# Returns a map of paths, grab the client lib path
		return paths['client_lib_paths']


	"""Checkin file to a particular context"""
	def checkinFile ( self, context, filename ):
		return self.server.simple_checkin ( self.__search_key__, context, filename,  is_current=True,mode='upload', create_icon=False, checkin_type='auto',file_type='nii.gz')
		

	
