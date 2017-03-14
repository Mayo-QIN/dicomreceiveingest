from tactic_client_lib import TacticServerStub
import util
import logging
from TObject import *
from Exam import *
from SubjectInfo import *

class Subject(TObject):
    logger = logging.getLogger ( 'Subject' )
    stype = "qin/subject"

    """Create a new Subject, must have a Patient ID which will be created as needed."""
    def __init__ ( self, data=None, server=None ):
        Subject.logger.setLevel(logging.DEBUG)
        self.server = server or TacticServerStub()
        if not data.has_key ( 'subjectname') and data.has_key ( 'patientname'):
            data['subjectname'] = data['patientname']
        if not data.has_key ( 'subjectid') and data.has_key ( 'patientid'):
            data['subjectid'] = data['patientid']

        if not data.has_key ( 'subjectname' ) and not data.has_key ( 'subjectid' ) and not data:
            raise 'Must have subjectname and subjectid'
        # Tactic will be looking for a 'safename'
        if not data.has_key ( 'safename' ):
            # Connect and create!
            Subject.logger.debug ( "Finding the subject %s", data['subjectname'] )
            data['safename'] = util.makeFilename ( data['subjectname'] )
            Subject.logger.debug ( data )
        if not data.has_key ( 'code' ):
            d = util.createOrUpdate ( self.server, Subject.stype, data, [("subjectname", data['subjectname']), ("subjectid", data['subjectid'])] )
        else:
            d = data
        TObject.__init__ ( self, d, server )

    def getExams ( self ):
        if not self.__dict__.has_key('exams'):
            self.exams = Exam.search ( filters=[('subject_code',self.code)],server=self.server)
        return self.exams

    def createExam ( self, data ):
        if not data.has_key ( 'studyinstanceuid'):
            raise "Exam must have a studyinstanceuid"
        if not data.has_key ( 'safename'):
            name = getattr ( data, 'Modality', 'unknown' ) + "_" + getattr ( data, "StudyDate", 'unknown' )
            data['safename'] = util.makeFilename ( name )
        return Exam ( util.createOrUpdate ( self.server, Exam.stype, data, [('studyinstanceuid', data['studyinstanceuid'])], parent_key=self.__search_key__ ), server=self.server)

    def getInfo ( self ):
        if not self.__dict__.has_key('info'):
            self.info = SubjectInfo.search ( filters=[('subject_code',self.code)] )
        return self.info
