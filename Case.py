import os, sys, shutil, sqlite3
from config import *


class Case:
    def __init__(self, caseName, description):
        self.caseName = caseName
        self.description = description

# db...database file or server location
def loadFromDB(db, mode = 'list'):
    conn = sqlite3.connect(db)
    query = conn.execute("SELECT * FROM CASES")
    if(mode == 'list'):
        cases = []
        for row in query:
            cases.append(Case(row[1], row[2]))
    else:
        cases = {}
        for row in query:
            cases[row[1]] = Case(row[1], row[2])

    conn.close()
    return cases

def loadFromFile(fileName, mode = 'list'):
    """ load all cases from file and retruns it as a list(default) or dictionary

        Keyword arguments:
         	fileName -- file from which cases will be loaded
            mode -- select type of return list/dictionary
    """
    # load as a list
    if(mode == 'list'):
    	file = open(fileName,"r")
    cases = []
    for line in file:
        parts = line.split(';')
        if len(parts) == 2:
            cases.append(Case(parts[0], parts[1]))
        file.close()
    # load as a dictionary
    else:
        file = open(fileName,"r")
        cases = {}
        for line in file:
            parts = line.split(';')
            if len(parts) == 2:
                cases[parts[0]] = Case(parts[0], parts[1])
        file.close()
    return cases


def addCase(caseName, description):
    # add to db
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    conn.execute("INSERT INTO FILTERS VALUES(null, \'\', \'\', \'\')")
    q = conn.execute('SELECT max(ID) FROM FILTERS')
    filterID = q.fetchone()[0]
    conn.execute("INSERT INTO CASES VALUES (null,?,?,?)",(caseName, description, filterID, ))

    conn.commit()
    conn.close()

    # create directories
    path = CASES_DIR + caseName
    os.mkdir(path)
    os.mkdir(path + IMG_DIR)
    os.mkdir(path + PCAP_DIR)
    # os.mkdir(path + PCAP_DIR + 'filtered/')
    os.mkdir(path + TMP_DIR)
    os.mkdir(path + TMP_DIR + 'tmp/')
    os.mkdir(path + ORIGIN_DIR)
    os.mkdir(path + ORIGIN_DIR + 'tmp/')
    os.mkdir(path + ORIGIN_DIR + 'tmp/' + '/tmp')

'''
def addCase(caseName, description):
	""" add case to DB and create case directory with description file in CASES_DIR directory defined in config.py

		Keyword arguments:
	   	 	caseName -- name of case which will be added
			description -- description of this case
	"""
	# check if case already exist
	path = CASES_DIR + caseName
	if(os.path.isdir(path)):
		e = Error("case already exist")
		e.raiseError()
		return
	else:
		try:
			os.mkdir(path)
			os.mkdir(path + IMG_DIR)
			os.mkdir(path + PCAP_DIR)
			os.mkdir(path + TMP_DIR)
		except IOError as (errno, strerror):
			e = Error("I/O error({0}): {1}".format(errno, strerror) + '\n')
			e.raiseError()

	file = open(path+'/description.txt','w')
	file.write(description)
	file.close()
	path = CASES_DB
	file = open(path,'a')
	file.write(caseName + ';' + description + '\n')
	file.close()
'''
