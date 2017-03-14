from tactic_client_lib import TacticServerStub
import datetime, re


def createOrUpdate ( server, searchType, data, filters, parent_key=None, print_status=True ):
    """Create the object only if it cannot be found by the filters"""
    object = server.query ( searchType, filters=filters )
    if print_status:
        print ( "----- Found " + str(len(object)) + " objects for " + searchType + " " + str(filters) )
    if len(object) == 0:
        return server.insert ( searchType, data, parent_key=parent_key )
    elif len(object) == 1:
        searchKey = server.build_search_key ( searchType, object[0]['code'] )
        return server.update ( searchKey, data=data, parent_key=parent_key )
    else:
        raise Exception ( "Found multiple rows in " + searchType + " matching filters: " + str(filters) )


def toDate ( date ):
    return datetime.datetime.strptime ( date, "%Y-%m-%d %H:%M:%S.%f" )

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

"""For a given search type, match column names, etc"""
def matchTags ( searchType, tags, defaults={}, server=None ):
    validColumns = self.server.get_column_names ( searchType )
    matched = defaults
    for key in tags.keys():
        if key.lower() in validColumns and key in self.tags and self.tags[key]:
            # print "\tMatched %s" % key.lower()
            matched[key.lower()] = tags[key]
    return matched
