import cgi
import cgitb, os, Case, SQLHelper, helper, htmlGen, sqlite3, syslog
from htmlGen import *
from config import *

# load cases from file
def loadCases():
    return Case.loadFromDB(DATABASE)

# add new case to DB
def addCase(caseName, caseDescription):
    conn = sqlite3.connect(DATABASE)
    conn.execute('pragma foreign_keys=ON')
    q = conn.execute('SELECT ID FROM CASES WHERE NAME == ?',(caseName,))
    exists = q.fetchone()
    conn.close()
    if exists:
        return ("<strong>Error!</strong> Case with this name already exists.", "danger")
    Case.addCase(caseName, caseDescription)
    return ("<strong>Success!</strong> Case was successfully added.", "success")

# return size of new, unprocessed file in case
def getSizeOfNewFilesInCase(caseName):
    originFiles = SQLHelper.loadFiles(caseName, 'origin')
    #files in directory
    files = [f for f in os.listdir(CASES_DIR + caseName + ORIGIN_DIR) if os.path.isfile(os.path.join(CASES_DIR + caseName + ORIGIN_DIR, f))]
    files = map(lambda fileName: 'origin/'+ fileName, files)
    newFiles = [file for file in files if file not in originFiles]
    # check if files was overwritten
    overwritten = 0
    originFiles = SQLHelper.loadFiles(caseName, 'origin', additionalColumn = ',SIZE')
    for file in originFiles:
        if os.path.isfile(CASES_DIR + caseName + PCAP_DIR + file[0]):
            fileSize = os.path.getsize(CASES_DIR + caseName + PCAP_DIR + file[0])
            if file[1] != fileSize:
                overwritten += fileSize
    return sum(os.path.getsize(CASES_DIR+ caseName + PCAP_DIR + f) for f in newFiles) + overwritten if newFiles or overwritten != 0 else ""

def render():
    # load all cases from file and create links to them
    cases = loadCases()
    print '<h1>Cases:</h1>'
    print '<hr/>'
    print '<h2>Available cases</h2>'
    print '<div class="col-md-3">'
    print '<div class="form-group">'
    for case in cases:
        sizeOfNewFiles = getSizeOfNewFilesInCase(case.caseName)
        syslog.syslog("PCAP APP: CASES OWERWRITE FILE  ended: "+str(sizeOfNewFiles))
        title = "No new files."
        if sizeOfNewFiles:
            style = 'style="color:red;"'
            approximateTime = helper.getFilterFileTime(sizeOfNewFiles)
            s = ' - ' + helper.sizeof_fmt(sizeOfNewFiles) + ' of new files.'
            title = 'Apply filters on new files may take up to ' + helper.getReadableTimeInfo(approximateTime)
            print '<a href = "main.py?caseName='+case.caseName+'&pagesToRender=case:saveFile"'+style+'class="list-group-item" onclick="startProgresBar('+str(approximateTime)+')" title="'+title+'">' + case.caseName + s +'</a>'
        else:
            print '<a href = "main.py?caseName='+case.caseName+'&pagesToRender=case:saveFile"class="list-group-item" title="'+title+'">' + case.caseName + '</a>'
    print '</div>'
    print htmlGen.generateProgresBar()
    print '<hr/>'
    print '<h2>Add new case</h2>'
    # form which is used for adding new case
    formStr = '<form action="main.py" method="post">\n'
    formStr += '<div class="form-group">'
    formStr += '<label>Case Name:</label>'
    formStr += '<input type="text" name="caseName" class="form-control" placeholder="Please enter: Case Name"></div>\n'
    formStr += '<div class="form-group">'
    formStr += '<label>Case Description:</label></div>'
    formStr += '<div class="form-group">'
    formStr += '<textarea name="caseDescription" class="form-control" placeholder="Please enter: Case Description"></textarea></div>\n'
    formStr += '<input type="hidden" name="pagesToRender" value="cases">\n'
    formStr += '<input type="hidden" name="actions" value="addCase">\n'
    formStr += '<input type="submit" value="Submit" class="btn btn-default pull-right"></a></form>\n'
    print formStr
