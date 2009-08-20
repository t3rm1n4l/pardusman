# -*- coding: utf-8 -*-
import os
import sys
import urllib2
import piksemel
from django.core.cache import cache

'''
#Depricated database implementation

from pardusman.wizard.models import Repository as Repobase
from pardusman.wizard.models import Package as Packbase
from pardusman.wizard.models import Dependency as Depbase
from pardusman.wizard.models import Components as Compbase


from utility import xterm_title

class Console:
    def started(self, title):
        print title

    def progress(self, msg, percent):
        sys.stdout.write("\r%-70.70s" % msg)
        sys.stdout.flush()

    def finished(self):
        sys.stdout.write("\n")
'''

class ExPisiIndex(Exception):
    pass

class ExIndexBogus(ExPisiIndex):
    pass

class ExPackageMissing(ExPisiIndex):
    pass

class ExPackageCycle(ExPisiIndex):        
    pass

class RepoNotInCache(Exception):
	pass

#Package object parsed from XML package list
class Package:
    def __init__(self, node):
        self.name = node.getTagData('Name')
        self.size = int(node.getTagData('PackageSize'))
        self.inst_size = int(node.getTagData('InstalledSize'))
        self.component = node.getTagData('PartOf').replace('.','-')
        deps = node.getTag('RuntimeDependencies')
        if deps:
            self.depends = map(lambda x: x.firstChild().data(), deps.tags('Dependency'))
        else:
            self.depends = []
        self.revdeps = []


	#FIXME: Following code is ignored to match the size limitation of memcached to meet total cache object size < 1 MB
	'''
	self.node = node
        self.icon = node.getTagData('Icon')
        if not self.icon:
            self.icon = 'package'
        self.homepage = node.getTag('Source').getTagData('Homepage')
        self.version = node.getTag('History').getTag('Update').getTagData('Version')
        self.release = node.getTag('History').getTag('Update').getAttribute('release')
        self.build = node.getTagData('Build')
        self.uri = node.getTagData('PackageURI')
        self.sha1sum = node.getTagData('PackageHash')
        self.summary = ""
        self.description = ""
        for tag in node.tags():
            if tag.name() == "Summary" and tag.getAttribute("xml:lang") == "en":
                self.summary = tag.firstChild().data()
        for tag in node.tags():
            if tag.name() == "Description" and tag.getAttribute("xml:lang") == "en":
                self.description = tag.firstChild().data()
	'''


#Component parsed XML object
class Component:
    def __init__(self, node):
        self.node = node
        self.name = node.getTagData('Name').replace('.','-')
        self.packages = []
	self.node = []

    def __str__(self):
        return "Component: %s\nPackages: %s" % (self.name, ", ".join(self.packages))



#XML parsed Repository DS
class Repository:
    def __init__(self,name):
		self.name = name
		self.size = 0
		self.inst_size = 0
		self.packages = {}
		self.components = {}

    def parse_data(self, path):

        if path.endswith(".bz2"):
            import bz2
            data = file(path).read()
            data = bz2.decompress(data)
            doc = piksemel.parseString(data)
        else:
            doc = piksemel.parse(path)
	for tag in doc.tags('Package'):
            p = Package(tag)
            self.packages[p.name] = p
            self.size += p.size
            self.inst_size += p.inst_size
            if p.component not in self.components:
                self.components[p.component] = []
        for name in self.packages:
            p = self.packages[name]
            for name2 in p.depends:
                if self.packages.has_key(name2):
                    self.packages[name2].revdeps.append(p.name)
                else:
                    raise ExPackageMissing, (p.name, name2)
            if p.component in self.components:
                self.components[p.component].append(p.name)
            else:
                self.components[p.component] = []
        from pisi.graph import Digraph, CycleException
        dep_graph = Digraph()
        for name in self.packages:
            p = self.packages[name]
            for dep in p.depends:
                dep_graph.add_edge(name, dep)
        try:
            dep_graph.dfs()
        except CycleException, c:
            raise ExPackageCycle, (c.cycle)

    '''
    #Depricated implementation
    def save_to_db(self):   
        repo = Repobase(name=self.name,size=self.size,inst_size=self.inst_size)

        for p in self.packages:
            data = self.packages[p]
            package = Packbase(name=data.name,size=data.size,part_of=data.component)
            for d in data.depends:
                dependency = Depbase(name=d)
                dependency.save()
                package.dependencies.add(dependency)
                package.save()
            repo.packages.add(package)

        for c in self.components:
            data = self.components[c]
            component = Compbase(name=c)
            for p in data:
                dependency = Depbase(name=p)
                dependency.save()
                component.packages.add(dependency)
                component.save()
            repo.components.add(component)
			
        repo.save()
     

    def load_from_db(self):
        repo = Repository.objects.get(name=self.name)
        self.size = repo.size
        self.inst_size = repo.inst_size



        self.packages = repo.packages
        self.components = repo.components


    #FIXME: Database storage and retrival is very slow. A database cache is to be maintained. So we will use memcached which is awesome

    
    def make_index(self, package_list):
        doc = piksemel.newDocument("PISI")

        # since new PiSi (pisi 2) needs component info in index file, we need to copy it from original index that user specified
        indexpath = fetch_uri(self.base_uri, self.cache_dir, self.index_name, None, False)
        if indexpath.endswith(".bz2"):
            import bz2
            data = file(indexpath).read()
            data = bz2.decompress(data)
            doc_index = piksemel.parseString(data)
        else:
            doc_index = piksemel.parse(indexpath)

        # old PiSi needs obsoletes list, so we need to copy it too.
        for comp_node in doc_index.tags("Distribution"):
            doc.insertNode(comp_node)

        for name in package_list:
            doc.insertNode(self.packages[name].node)

        for comp_node in doc_index.tags("Component"):
            doc.insertNode(comp_node)

        return doc.toPrettyString()

    def make_local_repo(self, path, package_list):
        index = 0
        for name in package_list:
            p = self.packages[name]
            xterm_title("Fetching: %s - %s of %s" % (name, index, len(package_list)))
            con = Console()
            cached = fetch_uri(self.base_uri, self.cache_dir, p.uri, con)
            os.symlink(cached, os.path.join(path, os.path.basename(cached)))
            index += 1
        index = self.make_index(package_list)
        import bz2
        data = bz2.compress(index)
        import hashlib
        f = file(os.path.join(path, "pisi-index.xml.bz2"), "w")
        f.write(data)
        f.close()
        f = file(os.path.join(path, "pisi-index.xml.bz2.sha1sum"), "w")
        s = hashlib.sha1()
        s.update(data)
        f.write(s.hexdigest())
        f.close()
	'''

    #Get full dependency for a package
    def full_deps(self, package_name):
        deps = set()
        deps.add(package_name)
        def collect(name):
            p = self.packages[name]
            for item in p.depends:
                deps.add(item)
                collect(item)
        collect(package_name)
        if self.components.has_key("system-base"):
            for item in self.components["system-base"]:
                deps.add(item)
                collect(item)
        return deps

    def __str__(self):
        return """Repository: %s
Number of packages: %d
Total package size: %d
Total installed size: %d""" % (
            self.name,
            len(self.packages),
            self.size,
            self.inst_size
        )


#Memcached object for keeping the list of package selected by user and calculate size
class LivePackagePool:
	def __init__(self):

		self.packages = set()
		self.components = {}
		self.all_packages = set()
		self.required_packages = []
		self.size = 0
		self.inst_size = 0

		try:
			self.repo = cache.get('repo')
			if self.repo == None:
				raise RepoNotInCache
		except:
			raise RepoNotInCache

	def add_item(self, name):
		item = name.split('_')
		if item[-1] == 'component':
			if item[0] in self.components:
				self.components[item[0]] = self.components[item[0]] + 1
			else:
				self.components[item[0]] = 1

		if item[-1] == 'package':
			self.packages.add(item[0])
			if item[-2] in self.components:
				self.components[item[-2]] = self.components[item[-2]] + 1
			else:
				self.components[item[-2]] = 1

	def fix_components(self):
		temp_comp = self.components.copy()
		for comp in temp_comp:
			if len(self.repo.components[comp])+1 != temp_comp[comp] :
				self.components.pop(comp)



	def update_packages(self):

		self.size = 0 
		self.inst_size = 0
		
		for pkg in self.packages:
			for dep in self.repo.full_deps(pkg):
				if dep not in self.required_packages and dep != pkg:
					self.required_packages.append(dep)

		for pkg in self.packages:
			self.size = self.size + self.repo.packages[pkg].size
			self.inst_size = self.size + self.repo.packages[pkg].inst_size

		for pkg in self.required_packages:
			self.size = self.size + self.repo.packages[pkg].size
			self.inst_size = self.inst_size + self.repo.packages[pkg].inst_size


	def get_size(self):
		self.update_packages()
		return self.size
