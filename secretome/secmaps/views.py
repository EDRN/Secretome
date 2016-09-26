from django.shortcuts import render
import csv

# Create your views here.

from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext, loader
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator
from django.shortcuts import render, render_to_response
from django.core.files.uploadhandler import MemoryFileUploadHandler
from django.core.files.uploadedfile import InMemoryUploadedFile, UploadedFile
from os import remove
from django.core.files import File

from .forms import HguidForm, NameForm, PostForm, Hguid2Form, UploadFileForm

from .models import Dbids, Hguids, MappedIds, HguidsFrequencies, MappedHguids
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import shutil 

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Default page lengths
dbpagelen = 30
hgupagelen = 30

@csrf_exempt

##############################################################################
def index(request):
    """Prints the main index page using template index.html

    The passing of the DatabaseNames is likely a relic. Commenting out.
    """
#    DatabaseNames_list = Dbids.objects.all()
    template = loader.get_template('secmaps/index.html')
    context = RequestContext(request)
#        'DatabaseNames_list': DatabaseNames_list,
#        'BASE_RELPATH': settings.BASE_RELPATH,
#        })
    return HttpResponse(template.render(context))

##############################################################################
def displayfilenamewithwts(request):
    """Returns filenames with wts.

    Likely defunct as we use new types of wts
    Used with testform
    Retaining for now.
    TTL until comments from Secretome team
    """
    hids = request.FILES.get('file1', None)
    wts = request.FILES.get('file2', None)
    return HttpResponse(str(hids) + str(wts))

##############################################################################
def displayhguidsfromfile(request):
    """Displays HGUids from a list along with their database presence and scores

    Takes an input filename and treating its contents as HGUids, provides
    links and scores for each.
    Splitting of ids is done on comma and newline. Spaces are ignored.

    The rowmat part is superceded. Commented parts retained until we hear
    from Secretome folks
    """

# Wts for dbs provided here. This mode is likely to go away
    dbwts  = {'clark': 1.03, 'GO:0005576': 1.1, 'GO:0016020': 1.2, 
      'gpcr.org_family': 1.4, 'gpcr.org_structure': 1.33, 'signal': 1.44, 
      'spd': 1.6, 'Stanford': 1.7, 'Stanford_addl_list1': 1.92, 
      'Stanford_addl_list2': 1.75, 'uniprot_secreted1': 1.67, 'Zhang': 1.31}
##    rowmat = []

# Read file and strip it into a list of HGUids
    y = request.FILES['file']
    default_storage.save('tempfiles/' + str(y), ContentFile(y.read()))
    mytempfile = settings.MEDIA_ROOT + '/tempfiles/' + str(y)
    with open(mytempfile, 'r') as f:
         x = f.read()
    newx = x.replace('\n',',')
    newx2 = newx.replace(',,',',')
    x = newx2
    HGUidslist = x.rstrip(',').split(',')

# Start creating the output
# Should use append format of concat ''.join(httplist)
    httplist = cssheader() + topmenu() + mainmenu() 
    httplist = httplist + '<DIV ALIGN="center">'
    httplist = httplist + '<B>Details for selected HGU ids</B><BR>'
    httplist = httplist + '<TABLE CLASS="sortable TFTABLE">'
    httplist = httplist + '<TR><TH>id</TH><TH class="rotate"><DIV><SPAN>Found in</SPAN></DIV></TH><TH class="rotate"><DIV><SPAN>Found times</SPAN></DIV></TH>'
    header_row = ['id','Found in','Found times']
    for key in dbwts:
        httplist = httplist + '<TH class="rotate"><DIV><SPAN>' + key + '</SPAN></DIV></TH>'
        header_row.append(key)
    httplist = httplist + '<TH>Score</TH>'
    header_row.append('Score')
##    rowmat.append(header_row)
    httplist = httplist + '</TR>'
    for hguid in HGUidslist:
        hguid = hguid.strip()
        hguidd3 = '<A HREF="' + settings.BASE_RELPATH + 'plotd3/' + hguid + '">' + hguid + '</A>'
        HguidsFrequencies_list = HguidsFrequencies.objects.filter(mapped_hguid=hguid)
        HguidsDB_list = MappedHguids.objects.filter(mapped_hguid=hguid)
        if len(HguidsFrequencies_list.values('num_sources')):
            numsources = HguidsFrequencies_list.values('num_sources')[0]['num_sources']
            numtimes = HguidsFrequencies_list.values('times_mapped')[0]['times_mapped']
        else:
            numsources = 0
            numtimes = 0
        ylist = []
        for y in HguidsDB_list.values('mapped_db'):
            ylist.append(y['mapped_db'])
        xsum = 0
##        rowmatlist = [hguid, numsources, numtimes]
        xlist = []
        for x in dbwts:
            if x in ylist:
                cumnum = MappedIds.objects.filter(mapped_hguid=hguid,mapped_db=x).count()
                appstr = '<A HREF="' + settings.BASE_RELPATH + 'get_beforemapping_names/' + x + '/' + hguid + '">' + str(cumnum) + '</A>'
                xlist.append(appstr)
#                rowmatlist.append('1')
                xsum = xsum + dbwts[x]
            else:
                xlist.append('0')
##                rowmatlist.append('0')
        xsum = "%.2f" % xsum
##        rowmatlist.append(xsum)
##        rowmat.append(rowmatlist)
        template = loader.get_template('secmaps/hguids_ind.html')
        context = RequestContext(request, {
                'hguid': hguidd3,
                'numsources': numsources,
                'numtimes': numtimes,
                'xlist': xlist,
                'xsum': xsum,
                })
        httplist = httplist + template.render(context)
    httplist = httplist + '</TABLE>'
    httplist = httplist + '<A HREF="' + settings.BASE_RELPATH + 'csv_view/' + ','.join(HGUidslist) + '">Download CSV</A>' 
#        httplist = httplist +  rowmat[0][0]
    httplist = httplist + mainmenu()
    httplist = httplist + '</DIV>'
    httplist = httplist + '</BODY></HTML>'
    remove(mytempfile)
    return HttpResponse(httplist)

##############################################################################
def handle_uploaded_file(f):
    """Create temp file out of an uploaded file

    Used x.out in tempfiles as the default
    TODO: May have to use non-absolute filename to avoid clashes
    """
    with open('tempfiles/x.out', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

##############################################################################
def copywtfile(request):
    """Allow user to upload a wt file

    Copy it to secmaps/copywtfile
    TODO: CHECK: Should it have a BASEREF defined?
    This is likely not being used. 
    The inelegant multihguid2 is being used
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('/success/url/')
    else:
        form = UploadFileForm()
    return render(request, 'secmaps/copywtfile.html', {'form': form})

##############################################################################
def usage(request):
    """Uses the usage template showing various options"""
    httplist = ''
    httplist = cssheader() + topmenu() + mainmenu()
    template = loader.get_template('secmaps/usage.html')
    context = RequestContext(request, { })
    httplist = httplist + template.render(context)
    httplist = httplist + mainmenu()
    httplist = httplist + '</BODY></HTML>'
    return HttpResponse(httplist)

##############################################################################
def databases(request):
    """Prints list of databases and could of ids through a template

    Includes NONE. Should these be removed?
    """
    DatabaseNames_list = Dbids.objects.all()
    httplist = ''
    httplist = cssheader() + topmenu() + mainmenu() 
    httplist = httplist + '<DIV ALIGN="center">'
    httplist = httplist + '<B>Secretome Databases</B>'
    httplist = httplist + '<TABLE CLASS="sortable TFTable">'
    httplist = httplist + '<TR><TH>Database</TH><TH>count</TH></TR>'
    for db in DatabaseNames_list.values('dbid'):
        dbid = db['dbid']
        rowcount = MappedIds.objects.filter(mapped_db=dbid).count()
        template = loader.get_template('secmaps/database_sing.html')
        context = RequestContext(request, {
            'dbid': dbid,
            'rowcount': rowcount,
            })
        httplist = httplist + template.render(context)
    httplist = httplist + '</TABLE>'
    httplist = httplist + mainmenu()
    httplist = httplist + '</DIV>'
    httplist = httplist + '</BODY></HTML>'
    return HttpResponse(httplist)

##############################################################################
def database_detail(request,dbname,page,dbpagelen=dbpagelen):
    """Provides details on a selected database through a template

    Uses default dbpagelen defined globally. Can be changed
    """
    flist = Paginator(MappedIds.objects.filter(mapped_db = dbname),dbpagelen)
#    print int(page)
    if int(page) > int(flist.num_pages) or int(page) < 1:
        return HttpResponse("Not that many pages")
    else:
        if int(page) > 1:
            menuaddl = '<A HREF="' + settings.BASE_RELPATH + 'databases/%s/%d/%d">Prev page </A>' %(dbname,int(page)-1,int(dbpagelen))
        else:
            menuaddl = ""
        if int(page) < int(flist.num_pages):
            menuaddr = '<A HREF="' + settings.BASE_RELPATH + 'databases/%s/%d/%d">Next page </A>' %(dbname,int(page)+1,int(dbpagelen))
        else:
            menuaddr = ""
        menuaddm = 'Page %d (of %d)' % (int(page),int(flist.num_pages))
        menuadd = menuaddl + menuaddm + menuaddr
        httplist = ''
        httplist = cssheader() + topmenu() + mainmenu() 
        httplist = httplist + '<DIV ALIGN="center">'
        httplist = httplist + '<B>Database: %s<BR></B>' % dbname 
        httplist = httplist + menuadd
        httplist = httplist + '<TABLE CLASS="sortable TFTable">'
        httplist = httplist + '<TR><TH>Gene/Protein ID</TH><TH>Mapped Affymetrix HGU133plus2 ID</TH></TR>'
#        print(flist.page(page).object_list.values()[0]['mapped_hguid_id'])
        template = loader.get_template('secmaps/dbdetail_page.html')
        context = RequestContext(request, {
            'flist': flist.page(page).object_list,
            })
        httplist = httplist + template.render(context)
        httplist = httplist + '</TABLE>'
        httplist = httplist + menuadd
        httplist = httplist + mainmenu()
        httplist = httplist + '</DIV>'
        httplist = httplist + '</BODY></HTML>'
        return HttpResponse(httplist)

##############################################################################
def hguids(request,page):
    """Provides list of HGUids"""
    flist = Paginator(Hguids.objects.all(),dbpagelen)
#    print int(page)
    if int(page) > int(flist.num_pages) or int(page) < 1:
        return HttpResponse("Not that many pages")
    else:
        if int(page) > 1:
            menuaddl = '<A HREF="' + settings.BASE_RELPATH + 'hguids/%d">Prev page </A>' %(int(page)-1)
        else:
            menuaddl = ""
        if int(page) < int(flist.num_pages):
            menuaddr = '<A HREF="' + settings.BASE_RELPATH + 'hguids/%d"> Next page</A>' %(int(page)+1)
        else:
            menuaddr = ""
        menuaddm = 'Page %d' % (int(page))
        menuadd = menuaddl + menuaddm + menuaddr
        httplist = ''
        httplist = cssheader() + topmenu() + mainmenu() 
        httplist = httplist + '<DIV ALIGN="center">'
        httplist = httplist + '<B>List of HGU133plus2 ids in the Secretome database</B><BR>'
        httplist = httplist + menuadd
        httplist = httplist + '<TABLE ALIGN="center" CLASS="sortable TFTable">'
        httplist = httplist + '<TR><TH>HGU id</TH></TR>'
        template = loader.get_template('secmaps/hguids_page.html')
        context = RequestContext(request, {
            'flist': flist.page(page).object_list,
            })
        httplist = httplist + template.render(context)
        httplist = httplist + '</TABLE>'
        httplist = httplist + menuadd
        httplist = httplist + mainmenu()
        httplist = httplist + '</DIV>'
        httplist = httplist + '</BODY></HTML>'
        return HttpResponse(httplist)

#class HFDetailView(DetailView):
#
#    model = HguidsFrequencies
#
#    def get_context_data(self, **kwargs):
#        context = super(HFDetailView, self).get_context_data(**kwargs)
#        return context

##############################################################################
def search_multihguid(request):
    """Returns number of dbs a list of HGUids are present in - along with number of appearances

    Takes a set of default wts defined below
    Also links to d3 graphics
    The rowmat part is superceded and can go. TTL comments from Secretome group about wts.
    """
    dbwts  = {'clark': 1.03, 'GO:0005576': 1.1, 'GO:0016020': 1.2, 'gpcr.org_family': 1.4, 'gpcr.org_structure': 1.33, 'signal': 1.44, 'spd': 1.6, 'Stanford': 1.7, 'Stanford_addl_list1': 1.92, 'Stanford_addl_list2': 1.75, 'uniprot_secreted1': 1.67, 'Zhang': 1.31}
##    rowmat = []
    if 'hguids' in request.GET:
        message = 'You searched for: %r' % request.GET['hguids']
        HGUidslist = request.GET['hguids'].rstrip(',').split(',')
        httplist = cssheader() + topmenu() + mainmenu() 
        httplist = httplist + '<DIV ALIGN="center">'
        httplist = httplist + '<B>Details for selected HGU ids</B><BR>'
        httplist = httplist + '<TABLE CLASS="sortable TFTABLE">'
        httplist = httplist + '<TR><TH>id</TH><TH class="rotate"><DIV><SPAN>Found in</SPAN></DIV></TH><TH class="rotate"><DIV><SPAN>Found times</SPAN></DIV></TH>'
        header_row = ['id','Found in','Found times']
        for key in dbwts:
            httplist = httplist + '<TH class="rotate"><DIV><SPAN>' + key + '</SPAN></DIV></TH>'
            header_row.append(key)
        httplist = httplist + '<TH>Score</TH>'
        header_row.append('Score')
##        rowmat.append(header_row)
        httplist = httplist + '</TR>'
        for hguid in HGUidslist:
            hguid = hguid.strip()
            hguidd3 = '<A HREF="' + settings.BASE_RELPATH + 'plotd3/' + hguid + '">' + hguid + '</A>'
            HguidsFrequencies_list = HguidsFrequencies.objects.filter(mapped_hguid=hguid)
            HguidsDB_list = MappedHguids.objects.filter(mapped_hguid=hguid)
            if len(HguidsFrequencies_list.values('num_sources')):
                numsources = HguidsFrequencies_list.values('num_sources')[0]['num_sources']
                numtimes = HguidsFrequencies_list.values('times_mapped')[0]['times_mapped']
            else:
                numsources = 0
                numtimes = 0
            ylist = []
            for y in HguidsDB_list.values('mapped_db'):
                ylist.append(y['mapped_db'])
            xsum = 0
##            rowmatlist = [hguid, numsources, numtimes]
            xlist = []
            for x in dbwts:
                if x in ylist:
                    cumnum = MappedIds.objects.filter(mapped_hguid=hguid,mapped_db=x).count()
                    appstr = '<A HREF="' + settings.BASE_RELPATH + 'get_beforemapping_names/' + x + '/' + hguid + '">' + str(cumnum) + '</A>'
                    xlist.append(appstr)
#                    rowmatlist.append(cumnum)
                    xsum = xsum + dbwts[x]
                else:
                    xlist.append('0')
##                    rowmatlist.append('0')
            xsum = "%.2f" % xsum
##            rowmatlist.append(xsum)
##            rowmat.append(rowmatlist)
            template = loader.get_template('secmaps/hguids_ind.html')
            context = RequestContext(request, {
                'hguid': hguidd3,
                'numsources': numsources,
                'numtimes': numtimes,
                'xlist': xlist,
                'xsum': xsum,
                })
            httplist = httplist + template.render(context)
        httplist = httplist + '</TABLE>'
        httplist = httplist + '<A HREF="' + settings.BASE_RELPATH + 'csv_view/' + request.GET['hguids'] + '">Download CSV</A>' 
        httplist = httplist + mainmenu()
        httplist = httplist + '</DIV>'
        httplist = httplist + '</BODY></HTML>'
        return HttpResponse(httplist)
    else:
        message = 'You submitted an empty form.'
    return HttpResponse(message)

##############################################################################
def cssheader():
    """Just the CSS header"""
    mystr = "<HTML>"
    mystr = mystr + '<HEAD>'
    mystr = mystr + '<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">'
    mystr = mystr + '<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css">'
    mystr = mystr + '<link rel="stylesheet" href="' + settings.STATIC_URL + 'css/secmaps.css">'
    mystr = mystr + '<script src="' + settings.STATIC_URL + 'css/sorttable.js"></script>'
    mystr = mystr + '</HEAD>'
    mystr = mystr + '<BODY>'
    return mystr

##############################################################################
def topmenu():
    """Just the top menu - excludes main menu"""
    mystr = '<P>'
    mystr = mystr + '<IMG SRC=' + settings.STATIC_URL + 'images/edrn.png>'
    mystr = mystr + '<H2>The Secretome Project</H2>'
    return mystr

##############################################################################
def mainmenu():
    """The main menu"""
    mystr = '<P>'
    mystr = mystr + '<DIV ALIGN="center">['
    mystr = mystr + '<a href="' + settings.BASE_RELPATH + '">Home</a>|'
    mystr = mystr + '<a href="' + settings.BASE_RELPATH + 'usage">Usage</a>|'
    mystr = mystr + '<a href="' + settings.BASE_RELPATH + 'databases">Databases</a>|'
    mystr = mystr + '<a href="' + settings.BASE_RELPATH + 'hguids/1">HGU 133plus2 Ids</a>|'
    mystr = mystr + '<form action="' + settings.BASE_RELPATH + 'search-multihguid/" method="get">'
    mystr = mystr + '<input type="text" name="hguids">'
    mystr = mystr + '<input type="submit" value="Search HGU133plus2 IDs">'
    mystr = mystr + '</form>'
    mystr = mystr + '|<form enctype="multipart/form-data" method="post" action="' + settings.BASE_RELPATH + 'displayhguidsfromfile"><input id="id_file" name="file" type="file" /><input type="submit" value="Submit" /> </form>'
    mystr = mystr + ']</DIV>'
    mystr = mystr + '<P>'
    return mystr

##############################################################################
def csv_view(request,hguidinlist):
    """Creates the HttpResponse object with the appropriate CSV header

    Some duplication with a couple of other functions. 
    Subject to refactoring.
    """
    dbwts  = {'clark': 1.03, 'GO:0005576': 1.1, 'GO:0016020': 1.2, 'gpcr.org_family': 1.4, 'gpcr.org_structure': 1.33, 'signal': 1.44, 'spd': 1.6, 'Stanford': 1.7, 'Stanford_addl_list1': 1.92, 'Stanford_addl_list2': 1.75, 'uniprot_secreted1': 1.67, 'Zhang': 1.31}
    rowmat = []
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="details.csv"'

    HGUidslist = hguidinlist.split(',')
    header_row = ['id','Found in','Found times']
    for key in dbwts:
        header_row.append(key)
    header_row.append('Score')
    rowmat.append(header_row)
    for hguid in HGUidslist:
        hguid = hguid.strip()
        HguidsFrequencies_list = HguidsFrequencies.objects.filter(mapped_hguid=hguid)
        HguidsDB_list = MappedHguids.objects.filter(mapped_hguid=hguid)
        if len(HguidsFrequencies_list.values('num_sources')):
            numsources = HguidsFrequencies_list.values('num_sources')[0]['num_sources']
            numtimes = HguidsFrequencies_list.values('times_mapped')[0]['times_mapped']
        else:
            numsources = 0
            numtimes = 0
        ylist = []
        for y in HguidsDB_list.values('mapped_db'):
            ylist.append(y['mapped_db'])
        xsum = 0
        rowmatlist = [hguid, numsources, numtimes]
        for x in dbwts:
            if x in ylist:
                cumnum = MappedIds.objects.filter(mapped_hguid=hguid,mapped_db=x).count()
                rowmatlist.append(cumnum)
                xsum = xsum + dbwts[x]
            else:
                rowmatlist.append('0')
        xsum = "%.2f" % xsum
        rowmatlist.append(xsum)
        rowmat.append(rowmatlist)
    writer = csv.writer(response)
    for row in rowmat:
        writer.writerow(row)

    return response


##############################################################################
def get_beforemapping_names(request,dbname,hguid):
    """Returns before_mapping names along with uniprot ids

    Following sql query is used for the purpose:
    select before_mapping from secmaps_mappedids where mapped_hguid like '202493_x_at' 
      and mapped_db like 'GO:0005576';
    """
    message = 'You searched for: %r' % hguid
    httplist = cssheader() + topmenu() + mainmenu() 
    httplist = httplist + '<DIV ALIGN="center">'
    httplist = httplist + '<B>Before Mapping Names for HGU id ' + hguid + ' in db ' + dbname + '</B><BR>'
    httplist = httplist + '<TABLE CLASS="sortable TFTABLE">'
    httplist = httplist + '<TR><TH>Before Mapping</TH></TR>'
    beforemappings_list = MappedIds.objects.filter(mapped_hguid=hguid,mapped_db=dbname)
    for y in beforemappings_list:
        httplist = httplist + '<TR><TD><A HREF=http://www.uniprot.org/uniprot/' + str(y.before_mapping) + '>' + str(y.before_mapping) + '</A></TD></TR>'
    httplist = httplist + '</TABLE>'
    httplist = httplist + mainmenu()
    httplist = httplist + '</DIV>'
    httplist = httplist + '</BODY></HTML>'
    return HttpResponse(httplist)

##############################################################################
def get_json(hguid):
	"""Creates a json file that provides links to dbs and genes from HGNC id

	Makes use of a file called bigger_table in secretome_uploads
	The file was created through an API to uniprot by David
	If possible all this should be made more elegant

	The dbwts used here are not the same as used elsewhere. These are in inverse
	proportion to number of ids in a database.
	The wts are later combined with frequencies to provid a better weighing.

	The json file is later used with d3 to make connectivity plots
	"""
	details = {}
	for line in open(settings.MEDIA_ROOT + "/bigger_table","r"):
		rows = line.rstrip().split()
		if rows[0] in details:
			details[rows[0]] = details[rows[0]] + ",%s %s %s" % (rows[1],rows[2],rows[3])
		else:
			details[rows[0]] = "%s %s %s" % (rows[1],rows[2],rows[3])

	dbwts = {"clark":        0.510, "GO:0005576":    0.224, "GO:0016020":    0.044, "gpcr.org_family":       0.548, "gpcr.org_structure":    3.571, "signal":        1.086, "spd":   0.167, "Stanford":      0.276, "Stanford_addl_list1":   0.896, "Stanford_addl_list2":   1.570, "uniprot_secreted1":     0.200, "Zhang": 0.145}
	sumscore = 0
	dbscores = []
	knowndb = ""
	thisdb = 0
	dbs = 0
	hgncs = {}
	myjson = '{"name": "%s", "children": [{' % hguid
	for el in details[hguid].split(','):
		(db, hgnc, gene) = el.rstrip().split()
		if db != knowndb:		# Change of db - could be first
			dbs = dbs + 1
			if thisdb == 0:		# First db encountered
				thisdb = 1
			else:			# New db but not first
				myjson =myjson + "]},{"
				this_score = dbwts[knowndb]*hgncs[knowndb]*len(dbgenes)
				dbscores.append([knowndb,dbwts[knowndb],hgncs[knowndb],dbgenes,this_score])
				sumscore = sumscore + this_score
			knowndb = db
			hgncs[db] = 1
			dbgenes = {}
			dbgenes[gene] = 1
			myjson =myjson +  '"name": "%s", "children": [' % db
			myjson =myjson +  '{"name": "%s", "children": [{"name": "%s"}]}' % (hgnc, gene)
		else:				# Same db as before
			hgncs[db] = hgncs[db] + 1
			myjson =myjson +  ',{"name": "%s", "children": [{"name": "%s"}]}' % (hgnc, gene)
			if gene not in dbgenes:
				dbgenes[gene] = 1
			else:			# New gene
				dbgenes[gene] = dbgenes[gene] + 1
	myjson= myjson + "]}]}"
	this_score = dbwts[knowndb]*hgncs[knowndb]*len(dbgenes)
	dbscores.append([knowndb,dbwts[knowndb],hgncs[knowndb],dbgenes,this_score])# The final db
	sumscore = sumscore + this_score

	return (myjson,dbscores,sumscore)

##############################################################################
def get_json2(hguid):
        """Creates a json file that provides links to dbs and genes from HGNC id

        Makes use of a file called bigger_table in secretome_uploads
        The file was created through an API to uniprot by David
        If possible all this should be made more elegant

        The json file is later used with d3 to make sankey plot
        """
        details = {}
#        for line in open(settings.MEDIA_ROOT + "/bigger_table","r"):
        for line in open("/Users/aam/Django/secretome_uploads/bigger_table","r"):
                rows = line.rstrip().split()
                if rows[0] in details:
                        details[rows[0]] = details[rows[0]] + ",%s %s %s" % (rows[1],rows[2],rows[3])
                else:
                        details[rows[0]] = "%s %s %s" % (rows[1],rows[2],rows[3])

	names = [hguid]
	links =[]
	vals = {}
        myjson = '\'{"nodes": [' 
        for el in details[hguid].split(','):
                (db, hgnc, gene) = el.rstrip().split()
		if db not in names:
			names.append(db)
			link_tup = (0,names.index(db))
			links.append(link_tup)
			vals[db] = 1
		else:
			vals[db] += 1
		if hgnc not in names:
			names.append(hgnc)
		link_tup = (names.index(db),names.index(hgnc))
		links.append(link_tup)
		if gene not in names:
			names.append(gene)
		link_tup = (names.index(hgnc),names.index(gene))
		links.append(link_tup)

	for el in range(len(names)):
		myjson += '{"name":"%s"},' % names[el]
	myjson = myjson[:-1] + '], "links":[ '
	for el in range(len(links)):
		value = 1
		if links[el][0] == 0:
			value = vals[names[links[el][1]]]
		myjson += '{"source":%s,"target":%s,"value":%s},' % (links[el][0],links[el][1],value)
	myjson = myjson[:-1] + ' ]}\''

        return (myjson)

##############################################################################
def plotd3(request,hguid):
        """Use d3.js to show connectivity for a given HGU id"""
        message = 'You searched for: %r' % hguid
        httplist = cssheader() + topmenu() + mainmenu() 
        httplist = httplist + '<DIV ALIGN="center">'
        (myjson, dbscores, sumscore) = get_json(hguid)
        myjson2 = get_json2(hguid)
        httplist = httplist + '</DIV>'
        httplist = httplist + '<DIV ALIGN="center">'

        template = loader.get_template('secmaps/scores.html')
        context = RequestContext(request, {
            'hguid': hguid,
            'dbscores': dbscores,
            'sumscore': sumscore,
            })
        httplist = httplist + template.render(context)
        httplist = httplist + '</DIV>'
        httplist = httplist + '<DIV ALIGN="center">'

        template = loader.get_template('secmaps/plot_sankey.html')
        context = RequestContext(request, {
            'hguid': hguid,
            'myjson': myjson2,
            })
        httplist = httplist + template.render(context)
        httplist = httplist + '</DIV>'
        httplist = httplist + '<DIV ALIGN="center">'

        template = loader.get_template('secmaps/plotd3.html')
        context = RequestContext(request, {
            'hguid': hguid,
            'myjson': myjson,
            })
        httplist = httplist + template.render(context)

        httplist = httplist + '</DIV>'
        httplist = httplist + '<DIV ALIGN="center">'
        httplist = httplist + mainmenu()
        httplist = httplist + '</DIV>'
        httplist = httplist + '</BODY></HTML>'
        return HttpResponse(httplist)

###############################################################
def search_multihguid2(request,hguids,wtfile):
    """Allow users to use their own wts (old weighing scheme)

    The usage page suggests changing url to execute this
    Very inelegant
    Needs to be refactored if this method of weighing is to be used
    Deferred until feedback from Secretome team

    The rowmat bits can go. Commented out for now
    """
    mytempfile = settings.MEDIA_ROOT + '/tempfiles/' + wtfile
    with open(mytempfile, 'r') as f:
         x = f.read()
    dbwts = {}
    keyval = x.split('\n')
    for i in range(len(keyval)-1):
        (key,val) = keyval[i].split('=')
        message = key + str(i)
        dbwts[key] = val

##    rowmat = []
    if 'hguids':
        message = 'You searched for: %r' % hguids
        HGUidslist = hguids.rstrip(',').split(',')
        httplist = cssheader() + topmenu() + mainmenu() 
        httplist = httplist + '<DIV ALIGN="center">'
        httplist = httplist + '<B>Details for selected HGU ids</B><BR>'
        httplist = httplist + '<TABLE CLASS="sortable TFTABLE">'
        httplist = httplist + '<TR><TH>id</TH><TH class="rotate"><DIV><SPAN>Found in</SPAN></DIV></TH><TH class="rotate"><DIV><SPAN>Found times</SPAN></DIV></TH>'
        header_row = ['id','Found in','Found times']
        for key in dbwts:
            httplist = httplist + '<TH class="rotate"><DIV><SPAN>' + key + '</SPAN></DIV></TH>'
            header_row.append(key)
        httplist = httplist + '<TH>Score</TH>'
        header_row.append('Score')
##        rowmat.append(header_row)
        httplist = httplist + '</TR>'
        for hguid in HGUidslist:
            hguid = hguid.strip()
            HguidsFrequencies_list = HguidsFrequencies.objects.filter(mapped_hguid=hguid)
            HguidsDB_list = MappedHguids.objects.filter(mapped_hguid=hguid)
            if len(HguidsFrequencies_list.values('num_sources')):
                numsources = HguidsFrequencies_list.values('num_sources')[0]['num_sources']
                numtimes = HguidsFrequencies_list.values('times_mapped')[0]['times_mapped']
            else:
                numsources = 0
                numtimes = 0
            ylist = []
            for y in HguidsDB_list.values('mapped_db'):
                ylist.append(y['mapped_db'])
            xsum = 0
##            rowmatlist = [hguid, numsources, numtimes]
            xlist = []
            for x in dbwts:
                if x in ylist:
                    cumnum = MappedIds.objects.filter(mapped_hguid=hguid,mapped_db=x).count()
                    appstr = '<A HREF="' + settings.BASE_RELPATH + 'get_beforemapping_names/' + x + '/' + hguid + '">' + str(cumnum) + '</A>'
                    xlist.append(appstr)
                    xsum = xsum + float(dbwts[x])
                else:
                    xlist.append('0')
##                    rowmatlist.append('0')
            xsum = "%.2f" % xsum
##            rowmatlist.append(xsum)
##            rowmat.append(rowmatlist)
            template = loader.get_template('secmaps/hguids_ind.html')
            context = RequestContext(request, {
                'hguid': hguid,
                'numsources': numsources,
                'numtimes': numtimes,
                'xlist': xlist,
                'xsum': xsum,
                })
            httplist = httplist + template.render(context)
        httplist = httplist + '</TABLE>'
        httplist = httplist + '<A HREF="' + settings.BASE_RELPATH + 'csv_view/' + hguids + '">Download CSV</A>' 
        httplist = httplist + mainmenu()
        httplist = httplist + '</DIV>'
        httplist = httplist + '</BODY></HTML>'
        return HttpResponse(httplist)
    else:
        message = 'You submitted an empty form.'
    return HttpResponse(message)

##############################################################################
def copywtfileres(request):
    """Allow user to upload a wt file

    Copy it to secmaps/copywtfile
    TODO: CHECK: Should it have a BASEREF defined?
    This is likely not being used. 
    The inelegant multihguid2 is being used
    """
    y = request.FILES['file']
    default_storage.save('tempfiles/' + str(y), ContentFile(y.read()))
    httplist = cssheader() + topmenu() + mainmenu() 
    httplist = httplist + 'The wtfile ' + str(y) + ' was copied'
    return HttpResponse(httplist)
