function getSelectValues(select) {
  var result = [];
  var options = select && select.options;
  var opt;
  for (var i=0, iLen=options.length; i<iLen; i++) {
    opt = options[i];
    if (opt.selected) {
      result.push(opt.value || opt.text);
    }
  }
  return result;
}
function toHHMMSS(n) {
    var sep = ':',
        n = parseFloat(n),
        hh = parseInt(n / 3600);
    n %= 3600;
    var mm = parseInt(n / 60),
        ss = parseInt(n % 60);
    return pad(hh,2)+sep+pad(mm,2)+sep+pad(ss,2);
    function pad(num, size) {
        var str = num + "";
        while (str.length < size) str = "0" + str;
        return str;
    }
}
function getSumTime(arg, baseTime) {
    var selectedValues = getSelectValues(document.getElementById("additionalFiles"));
    var b = arg.split(';');
    var files = {};
    var sum = baseTime;
    for(i = 0; i < b.length; i++){
     pom = b[i].split(':');
     files[pom[0]] = pom[1];
    }
    for(i = 0; i < selectedValues.length; i++)
    {
        sum = eval('sum + parseInt(files[selectedValues[i]])');
    }
    document.getElementById("renderGraph").title = 'Approximate time to render graph is: ' + toHHMMSS(sum);
    document.getElementById("renderDetailedGraph").title = 'Approximate time to render graph is: ' + toHHMMSS(sum);
    return sum;
}
function setWidth(total, start){
    var d = new Date();
    var n = d.getTime();
    current = eval( (n - start) / 1000);console.log(current);
    proc = String(eval(100*current/total));
    document.getElementById("progress-bar").style.width = proc.concat("%");}
function startProgresBar(seconds){
        var d = new Date();
        var n = d.getTime();
        document.getElementsByName("progres-div")[0].removeAttribute("style");
        setInterval(setWidth, 1000, seconds, n);
}
