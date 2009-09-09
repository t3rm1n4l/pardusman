#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

import os
import sys
import urllib2
import piksemel

from utility import xterm_title

class Console:
    def started(self, title):
        print title

    def progress(self, msg, percent):
        sys.stdout.write("\r%-70.70s" % msg)
        sys.stdout.flush()

    def finished(self):
        sys.stdout.write("\n")


class ExPisiIndex(Exception):
    pass

class ExIndexBogus(ExPisiIndex):
    pass

class ExPackageMissing(ExPisiIndex):
    pass

class ExPackageCycle(ExPisiIndex):
    pass


def fetch_uri(base_uri, cache_dir, filename, console=None, update_repo=False):
    # Dont cache for local repos
    if base_uri.startswith("file://") and not filename.startswith("pisi-index.xml"):
        return os.path.join(base_uri[7:], filename)

    # Check that local file isnt older or has missing parts
    path = os.path.join(cache_dir, filename)
    if not os.path.exists(path) or (update_repo and filename.startswith("pisi-index.xml")):
        if console:
            console.started("Fetching '%s'..." % filename)
        try:
            conn = urllib2.urlopen(os.path.join(base_uri, filename))
        except ValueError:
            raise ExIndexBogus
        output = file(path, "w")
        total_size = int(conn.info()['Content-Length'])
        size = 0
        while size < total_size:
            data = conn.read(4096)
            output.write(data)
            size += len(data)
            if console:
                console.progress("Downloaded %d of %d bytes" % (size, total_size), 100 * size / total_size)
        output.close()
        conn.close()
        if console:
            console.finished()
    return path


class Package:
    def __init__(self, node):
        self.node = node
        self.name = node.getTagData('Name')
        self.icon = node.getTagData('Icon')
        if not self.icon:
            self.icon = 'package'
        self.homepage = node.getTag('Source').getTagData('Homepage')
        self.version = node.getTag('History').getTag('Update').getTagData('Version')
        self.release = node.getTag('History').getTag('Update').getAttribute('release')
        self.build = node.getTagData('Build')
        self.size = int(node.getTagData('PackageSize'))
        self.inst_size = int(node.getTagData('InstalledSize'))
        self.uri = node.getTagData('PackageURI')
        self.sha1sum = node.getTagData('PackageHash')
        self.component = node.getTagData('PartOf')
        self.summary = ""
        self.description = ""
        for tag in node.tags():
            if tag.name() == "Summary" and tag.getAttribute("xml:lang") == "en":
                self.summary = tag.firstChild().data()
        for tag in node.tags():
            if tag.name() == "Description" and tag.getAttribute("xml:lang") == "en":
                self.description = tag.firstChild().data()
        deps = node.getTag('RuntimeDependencies')
        if deps:
            self.depends = map(lambda x: x.firstChild().data(), deps.tags('Dependency'))
        else:
            self.depends = []
        self.revdeps = []
        # Keep more info: licenses, packager name

    def __str__(self):
        return """Package: %s (%s)
Version %s, release %s, build %s
Size: %d, installed %d
Part of: %s
Dependencies: %s
Reverse dependencies: %s
Summary: %s""" % (
            self.name, self.uri,
            self.version, self.release, self.build,
            self.size, self.inst_size,
            self.component,
            ", ".join(self.depends),
            ", ".join(self.revdeps),
            self.summary
        )


class Component:
    def __init__(self, node):
        self.node = node
        self.name = node.getTagData('Name')
        self.packages = []

    def __str__(self):
        return "Component: %s\nPackages: %s" % (self.name, ", ".join(self.packages))


class Repository:
    def __init__(self, uri, cache_dir):
        self.index_name = os.path.basename(uri)
        self.base_uri = os.path.dirname(uri)
        self.cache_dir = cache_dir
        self.size = 0
        self.inst_size = 0
        self.packages = {}
        self.components = {}

    def parse_index(self, console=None, update_repo=False):
        path = fetch_uri(self.base_uri, self.cache_dir, self.index_name, console, update_repo)
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

    def full_deps(self, package_name):
        deps = set()
        deps.add(package_name)
        def collect(name):
            p = self.packages[name]
            for item in p.depends:
                deps.add(item)
                collect(item)
        collect(package_name)
        if self.components.has_key("system.base"):
            for item in self.components["system.base"]:
                deps.add(item)
                collect(item)
        return deps

    def __str__(self):
        return """Repository: %s
Number of packages: %d
Total package size: %d
Total installed size: %d""" % (
            self.base_uri,
            len(self.packages),
            self.size,
            self.inst_size
        )
