#How to install:
- Install python, libpcap0.8-dev, hdparm, sqlite3, libapache2-mod-python, wireshark, tshark, gnuplot, texlive-font-utils, imagemagick
- Install Apache or other web server
- Enable Apache modules: ssl, cgi, python and mime
- Enable AddHandler cgi-script .py in mods-enabled/mime.conf
- Clone GituHub repository
- Set Apache up so it can run python scripts from cloned directory
- Run Makefile as root, need it because it uses hdparm to set up config.


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
