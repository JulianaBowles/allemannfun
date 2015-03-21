#!/usr/bin/env python
from Cheetah.Template import Template
import sys
import re
import os.path, time
import argparse
import markdown
import codecs
from collections import OrderedDict
from BeautifulSoup import BeautifulSoup
import calendar
import string
import Image

WIDTHS = {'l':800,'m':400,'s':200}
MEDIA = {'l':'1000px','m':'480px'}

class MenuItem(object):
    def __init__(self,name="",target="#"):        
        self.target = target
        self.name = name
        self.children = OrderedDict()

    def add(self,name,target):
        # make sure we are getting a list
        assert isinstance(name,list)

        t = target.strip()
        if t=="":
            t = "#"

        n = name[0].strip()
        if n not in self.children:
            self.children[n] = MenuItem(n)
            
        if len(name) > 1:
            self.children[n].add(name[1:],t)
        else:
            self.children[n].target = t

    def unicode(self):
        s = unicode("")
        if self.name != "":
            s += "<li>\n<a href=\"%s\">%s</a>\n"%(self.target,self.name)
        if len(self.children)>0:
            if self.name != "":
                s +="<ul>\n"
            for n in self.children:
                s += self.children[n].unicode()
            if self.name != "":
                s +="</ul>\n"
        if self.name != "":
            s += "</li>\n"
        return s

    def select(self,depth=0):
        s = unicode("")
        if self.name != "":
            s+="<option value=\"%s\" >%s %s</option>\n"%(self.target,depth*"-",self.name)
            d=1
        else:
            d=0
        if len(self.children)>0:
            for n in self.children:
                s += self.children[n].select(depth=depth+d)
        return s

        
    def getTargets(self):
        for n in self.children:
            for t in self.children[n].getTargets():
                yield t
        yield self.target

class Menu(object):

    def __init__(self,idxname):
        self._menu = MenuItem()
        with codecs.open(idxname,'r', 'utf-8') as idx:
            i=0
            for line in idx.readlines():
                l = line.split(':')
                i=i+1
                if len(l)<2:
                    print 'Warning line %d of index file %s does not contain a :\n%s'%(i,idxname,line)
                    continue
                self._menu.add(l[1].strip().split('/'),l[0].strip())
    

    def unicode(self):
        
        s = unicode("<ul>\n")
        s += self._menu.unicode()
        s += "</ul>\n"
        # the select box
        s += "<form name=\"menuform\">\n"
        s += "<select name=\"menu2\" onChange=\"top.location.href = this.form.menu2.options[this.form.menu2.selectedIndex].value; return false;\">\n"
        s += "<option value=\"\" selected=\"selected\">Goto ...</option>\n"
        s += self._menu.select()
        s += "</select></form>\n"
        return s

    def getTargets(self):
        for t in self._menu.getTargets():
            yield t

class AllemannFun(object):
    KEYS = ['title','author','type']

    def __init__(self,name,menu="",template="allemannfun.template",outdir=None):
        self.outdir = outdir
        data = self.loadFile(name)
        data['contents'] = self.process(data)
        data['date'] = time.ctime(os.path.getmtime(name))
        data['menu'] = menu
        self.template = Template(file="allemannfun.template",searchList=(data,))

    def process(self,data):
        res = ''
        if data['type'] == 'Bilder':
            outdir = os.path.join(self.outdir,'images')
            res = unicode("</div>\n")
            for line in data['contents'].split('\n'):
                l = line.split()
                if len(l) > 0:
                    img = l[0]
                    caption = string.join(l[1:])
                    if not os.path.isfile(img):
                        print 'Error, cannot find image %s'%img
                        continue
                    res += "<div align =\"center\" class=\"sixteen columns\">\n<picture>\n"
                    bname = os.path.splitext(os.path.basename(img))[0]
                    for w in WIDTHS:
                        outim = os.path.join(outdir,bname+'_'+w+'.jpg')
                        if not os.path.isfile(outim):
                            im = Image.open(img)
                            a = float(im.size[1])/float(im.size[0])
                            im.thumbnail((WIDTHS[w],WIDTHS[w]*a),Image.ANTIALIAS)
                            im.save(outim, "JPEG")
                    for w in MEDIA:
                        res += '<source srcset="%s" media="(min-width: %s)">\n'%(os.path.join("images",bname+'_'+w+'.jpg'),MEDIA[w])
                    res += '<img src="%s" alt="%s">\n'%(os.path.join("images",bname+'_s'+'.jpg'),caption)
                        
                    res += "</picture>\n</div>\n"
            res+="<div>\n"
        else:
            md = markdown.Markdown(extensions=['squareul'])
            res = md.convert(data['contents'])
        return res
        
    def loadFile(self,name):
        data = {"contents":""}
        for k in self.KEYS:
            data[k] = ""
        key = re.compile('^#\s*(\w+)\s*:\s*(.*)$')
        with codecs.open(name,'r', 'utf-8') as input:
            for line in input.readlines():
                line = line.strip()
                l= key.match(line)
                if l!=None:
                   k,v = l.groups()
                   if k in self.KEYS:
                       data[k] = v
                   else:
                       print 'warning, unknown key %s'%k
                else:
                    data['contents'] += line + '\n'
        return data

    def __str__(self):
        return str(self.template)

class Kalender(AllemannFun):
    KEYS = ['title','author','year']

    def process(self,data):

        DAYS = "MDMDFSS"
        MONTHS = ["Januar","Februar",u'M\xe4rz',"April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
        year = int(data['year'])
        dates = {}
        for line in data['contents'].split('\n'):
            line = line.strip()
            if len(line)>0:
                dates[line[:10]] = line[10:].strip()
                
        cal = calendar.Calendar()

        s = unicode("</div>\n")

        for m in range(0,12):
            cm = (m+7)%12+1
            cy = (m+7)//12+year
            s += "<div align =\"center\" class=\"four columns\">\n"
            s += "<table class=\"cal\">\n"
            # the month
            s += "<tr><th colspan=\"7\">%s %d</th></tr>\n"%(MONTHS[cm-1],cy)
            # the days of the week
            s += "<tr>"
            for d in DAYS:
                s+="<th>%s</th>"%d
            s += "</tr>\n"
            # loop over the days in the month
            alldays = 0
            for md,wd in calendar.Calendar().itermonthdays2(cy,cm):
                if alldays%7==0:
                    s+="<tr>"
                k= "%02d-%02d-%d"%(md,cm,cy)
                if k in dates:
                    if dates[k]=="":
                        extra=' class="afday"'
                    else:
                        extra=' class="afspecial" title=\"%s\"'%(dates[k])
                else:
                    extra=''
                    #print k,dates[k]
                s+="<td%s>"%extra
                if md!=0:
                    s+="%d"%md
                s+="</td>"
                if alldays%7==6:
                    s+="</tr>\n"
                alldays+=1
                
            s += "</table>\n"
            s += "</div>\n"
        
        
        #for md,wd in calendar.Calendar().itermonthdays2(2014,12):
        #    print md,wd

        s += "<div class=\"sixteen columns content\">"
        return s
    

    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument("index",metavar='FILE',help="the index file")
    parser.add_argument("-t","--template",default="allemannfun.template",help="template to use")
    parser.add_argument("-o","--output-dir",default="../site/",help="the output directory")
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        parser.error('no such directory %s'%args.output_dir)

    menu = Menu(args.index)

    inputs = []
    for h in menu.getTargets():
        t = os.path.splitext(h)[0]+'.txt'
        if os.path.exists(t):
            if t == 'kalender.txt':
                page = Kalender(t,menu=menu.unicode(),template=args.template)
            else:
                page = AllemannFun(t,menu=menu.unicode(),template=args.template,outdir=args.output_dir)
            with open(os.path.join(args.output_dir,h),'w') as out:
                bs = BeautifulSoup(str(page))
                #out.write(bs.prettify())
                out.write(str(page))

    #with codecs.open('test2.html','w', encoding='utf-8') as out:
    #    out.write(menu.unicode())

    #for 

    #print readIndex(args.index)
        

    #for f in args.inputs:
    #    with open(os.path.splitext(f)[0]+'.html','w') as out:
    #        out.write(str(AllemannFun(f,template=args.template)))


    


 


