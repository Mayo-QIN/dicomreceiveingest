from tactic_client_lib import TacticServerStub
import util
import logging
from TObject import *

class SubjectInfo(TObject):
    logger = logging.getLogger ( 'SubjectInfo' )
    stype = "qin/subject_info"


    """Search and return a list of subjects"""
    @classmethod
    def search ( cls, filters=[] ):
        SubjectInfo.logger.debug ( "Search with cls: %s" % cls )
        server = TacticServerStub()
        objects = server.query ( cls.stype, filters=filters )
        # Here we do something different
        si = SubjectInfo ( objects )
        return si
    
    def __init__ ( self, objects):
        self.data = {}
        self.objects = {}
        print objects[0]
        for o in objects:
            key = o["key"]
            self.objects[key] = o
            if o["text_value"] != None:
                self.data[key] = o["text_value"]
            else:
                self.data[key] = float ( o["numeric_value"] )
            
        
    
