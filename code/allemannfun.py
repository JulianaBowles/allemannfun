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
        
        s = unicode("<nav><ul>\n")
        s += self._menu.unicode()
        s += "</ul></nav>\n"
        return s

    def getTargets(self):
        for t in self._menu.getTargets():
            yield t

class AllemannFun(object):
    KEYS = ['title','author']

    def __init__(self,name,menu="",template="allemannfun.template"):
        data = self.loadFile(name)
        md = markdown.Markdown(extensions=['squareul'])
        data['contents'] = md.convert(data['contents'])
        data['date'] = time.ctime(os.path.getmtime(name))
        data['menu'] = menu
        self.template = Template(file="allemannfun.template",searchList=(data,))

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
            with open(os.path.join(args.output_dir,h),'w') as out:
                bs = BeautifulSoup(str(AllemannFun(t,menu=menu.unicode(),template=args.template)))
                out.write(bs.prettify())

    #with codecs.open('test2.html','w', encoding='utf-8') as out:
    #    out.write(menu.unicode())

    #for 

    #print readIndex(args.index)
        

    #for f in args.inputs:
    #    with open(os.path.splitext(f)[0]+'.html','w') as out:
    #        out.write(str(AllemannFun(f,template=args.template)))


    


 


