def genHead(title):
	headStr = "<head>\n"
	headStr += '<meta charset="utf-8">\n'
	headStr += '<title>' + title + "</title>\n"
	headStr += '<link rel="stylesheet" type="text/css" href="bootstrap/css/bootstrap.min.css">\n'
	headStr += '<link rel="stylesheet" type="text/css" href="bootstrap/css/app.css">\n'
	headStr += '<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.10/css/jquery.dataTables.min.css">\n'
	headStr += '<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>'
	headStr += '<script src="bootstrap/js/bootstrap.min.js"></script>'
	headStr += '<script src="https://cdn.datatables.net/1.10.10/js/jquery.dataTables.min.js"></script>'
	headStr += '<script src="js/script.js"></script>'
	headStr += '<script src = "//cdn.datatables.net/plug-ins/1.10.10/type-detection/file-size.js"></script>'
	headStr += '<script src="//cdn.datatables.net/plug-ins/1.10.7/sorting/file-size.js"></script>'
	headStr += '<script type="text/javascript">  $(document).ready(function() {'
	headStr += "        $('table.display').dataTable( {"
	headStr += '            "columnsDefs": ['
	headStr += '             { "type": "file-size", "targets": 1 }'
	headStr += '            ]'
	headStr += '        } );'
	headStr += '    } );</script>'
	# Should enable touch zooming and ensure proper rendering on mobile devices.
	headStr += '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
	headStr += "</head>\n"
	return headStr
def genBegining(title):
	return "<!DOCTYPE html>\n<html>" + genHead(title) + "<body style='overflow-x: hidden'>\n"
def genEnd():
	return "</body></html>"

def genHref(link,text = "test"):
	return '<p><a href="' + link +'">'+text+'</a></p>'
#pagesToRender contains curently displayed pages,
def genBackButton(pagesToRender, caseName = None):
	formStr = '<form class="form-horizontal" action="main.py" method="post"><input type="hidden" name="pagesToRender" '
	if "default" in pagesToRender:
		return ""
	if "cases" in pagesToRender:
		formStr += 'value="default">'
	elif "case" in pagesToRender:
		formStr += 'value="cases">'
	elif "showFile" in pagesToRender:
		if caseName:
			formStr += 'value="case:saveFile"><input type="hidden" name="caseName" value="'+caseName+'">'
	formStr += '<div class="form-group">'
	formStr += '<input type="submit" value="Back" class="btn btn-default"></div></form>'
	return formStr

def genBreadcrumb(pagesToRender, caseName = None, fileName = None):
	breadcrumb = '<ol class = "breadcrumb">'
	if "cases" in pagesToRender:
		breadcrumb += '<li class="active">Cases</li>'
	elif "case" in pagesToRender:
		if caseName:
			breadcrumb += '<li><a href="main.py?pagesToRender=cases">Cases</a></li>'
			breadcrumb += '<li class="active">'+caseName+'</li>'
	elif "showFile" in pagesToRender:
		if caseName and fileName:
			breadcrumb += '<li><a href="main.py?pagesToRender=cases">Cases</a></li>'
			breadcrumb += '<li><a href="main.py?caseName='+caseName+'&pagesToRender=case:saveFile">'+caseName+'</a></li>'
			breadcrumb += '<li class="active">'+fileName+'</li>'
		elif caseName:
			breadcrumb += '<li><a href="main.py?pagesToRender=cases">Cases</a></li>'
			breadcrumb += '<li class="active">'+caseName+'</li>'

	breadcrumb += '</ol>'
	return breadcrumb

def genBootstrapJS():
	return '<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script><script src="bootstrap/js/bootstrap.min.js"></script><script src="bootstrap/bootstrap-table.js"></script> <script src="https://cdn.datatables.net/1.10.10/js/jquery.dataTables.min.js"></script><script src="js/script.js"></script>'

def generateProgresBar():
    script = '<div class="col-md-12"><div name="progres-div" class="progress col-md-6" style="display:none"><div id="progress-bar" class="progress-bar" role="progressbar" style="width:0%"></div></div></div>'
    return script
if __name__ == '__main__':
	printHead("test")
