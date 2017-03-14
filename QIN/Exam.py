from tactic_client_lib import TacticServerStub
import util
import logging
from TObject import *
from Series import *
import Subject

class Exam(TObject):
    logger = logging.getLogger ( 'Exam' )
    stype = "qin/exam"

    """Create a new Exam, must have a Patient ID which will be created as needed."""
    def __init__ ( self, data=None, server=None ):
        Exam.logger.setLevel(logging.DEBUG)
        if not data:
            raise "Must set data for the exam"
        TObject.__init__ ( self, data, server )

    def getSeries ( self ):
     #    print dir(self)
     #    print dir(self.__dict__.has_key)
    	# print self.__dict__.has_key('series')
        # if self.__dict__.has_key('series'):
        #     self.series = Series.search ( filters=[('exam_code',self.code)], server=self.server )
        #     return self.series
        # else:
        expression = "@SOBJECT(qin/subject.qin/exam['code','%s'].qin/series)"%(self.code)
        self.series =Series.search (expression=expression, server=self.server )
        return self.series


    def getSubject(self):
        return Subject.Subject.fromKey ( self.server.build_search_key ( Subject.Subject.stype, self.subject_code), server=self.server)

    def createSeries ( self, data ):
        if not data.has_key ( 'seriesinstanceuid'):
            raise "Series must have a seriesinstanceuid"
        if not data.has_key ( 'safename'):
            seriesNumber = "{0:04d}".format ( int ( getattr ( data, "SeriesNumber", "9999" ) ) )
            name = seriesNumber + "_" + getattr ( data, "SeriesDescription", "unknown" )
            data['safename'] = util.makeFilename ( name )
        return Series ( util.createOrUpdate ( self.server, Series.stype, data, [('seriesinstanceuid', data['seriesinstanceuid'])], parent_key=self.__search_key__ ), server=self.server)




