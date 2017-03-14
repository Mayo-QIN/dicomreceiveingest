import os,os.path,UserDict
from sqlite3 import dbapi2 as sqlite

class sqlDict(UserDict.DictMixin):
    ''' dbdict, a dictionnary-like object for large datasets (several Tera-bytes) '''
   
    def __init__(self,dictName):
        self.db_filename = dictName
        self.con = sqlite.connect(self.db_filename)
        self.con.execute("create table if not exists data (key PRIMARY KEY,value)")
   
    def __contains__(self, key):
        row = self.con.execute("select value from data where key=?",(key,)).fetchone()
        return not not row 

    def __getitem__(self, key):
        row = self.con.execute("select value from data where key=?",(key,)).fetchone()
        if not row: raise KeyError
        return row[0]
   
    def __setitem__(self, key, item):
        if self.con.execute("select key from data where key=?",(key,)).fetchone():
            self.con.execute("update data set value=? where key=?",(item,key))
        else:
            self.con.execute("insert into data (key,value) values (?,?)",(key, item))
        self.con.commit()
              
    def __delitem__(self, key):
        if self.con.execute("select key from data where key=?",(key,)).fetchone():
            self.con.execute("delete from data where key=?",(key,))
            self.con.commit()
        else:
             raise KeyError
            
    def keys(self):
        return [row[0] for row in self.con.execute("select key from data").fetchall()]