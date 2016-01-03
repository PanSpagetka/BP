#How to install:
- Install python, libpcap0.8-dev, hdparm, sqlite3, libapache2-mod-python, wireshark, tshark, gnuplot, texlive-font-utils, imagemagick
- Install Apache or other web server
- Enable Apache modules: ssl, cgi, python and mime
- Enable AddHandler cgi-script .py in mods-enabled/mime.conf
- Clone GituHub repository
- Set Apache up so it can run python scripts from cloned directory
- Run Makefile as root, need it because it uses hdparm to set up config.

#Description
This application can filter PCAP files and can view and compare result in throughput graphs.

##Time approximation
Before every action except file upload, you will get approximation about time needed to complete that action. It is just approximation, nothing more nothing less.

##File upload
Application two ways of uploading files. First you can upload file using web form on page or you can upload file direcly into /cases/CASENAME/PCAPs/origin/ directory. After you do this, file is proceed when you access case with CASENAME. Dont be worry about fact that filesize of uploaded file is much smaller then before. In inicial processing all application layer data are cut.

##Files
There are three types of files. Original (No filter applied, only striped application layer data), fitlered (With inicial case filter applied) and temporary (with custom fitler applied).

##Filters
You can filter files base on two criterias. Based on content of PCAP files or time when packets were captured. Also you can choose target of applying filter on whole case, you can choose original or filtered files. When you apply filter on case ALL temporary files will be deleted.

##Graphs
When you render graph then will be created temporary file with applied filter before it is rendered. Also you can compare multiple files in one graph.


#Files:  
Case.py - Case class.  
Filter.py - All methods for filtering files.  
config.py - Name of directories, and files, config for evaluating filters and rendering graph.  
helper.py - Manipulation with files, middle layer between db and application.  
htmlGen.py - create html tags  
init.py - Inicialize application, config file, folders. Need root privileges.  
initDB.py - Inicialize database for application.  
renderGraph.py - Rendering graph.  
saveFile.py Saving and rmoving file from application.  
SQLHelper.py - Communication with DB.  
cases.py - Case selection page.  
showCase.py - Detail of selected case page.  
showPCAPFileDetails.py - Detail of selected file page.  
