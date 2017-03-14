from tactic_client_lib import TacticServerStub
import util
import logging
from TObject import *
import Exam
from Subject import *

class Series(TObject):
    logger = logging.getLogger ( 'Series' )
    stype = "qin/series"

    def getExam(self):
    	print Exam.Exam.stype
    	return Exam.Exam.fromKey ( self.server.build_search_key ( Exam.Exam.stype, self.exam_code), server=self.server)

    def __repr__(self):
      return "SeriesDescription: {}\nKeywords: {}\nCode: {}\nSearchKey: {}\n".format ( self.seriesdescription, self.keywords, self.code, self.__search_key__)