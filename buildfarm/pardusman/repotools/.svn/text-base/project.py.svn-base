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
import piksemel

import packages

# no i18n yet
def _(x):
    return x

default_live_exclude_list = """
lib/rcscripts/
usr/include/
usr/lib/python2.6/lib-tk/
usr/lib/python2.6/idlelib/
usr/lib/python2.6/bsddb/test/
usr/lib/python2.6/lib-old/
usr/lib/python2.6/test/
usr/lib/klibc/include/
usr/qt/4/include/
usr/share/aclocal/
usr/share/doc/
usr/share/info/
usr/share/sip/
usr/share/man/
usr/share/groff/
usr/share/dict/
var/db/pisi/
var/cache/pisi/packages/
var/cache/pisi/archives/
var/tmp/pisi/
var/pisi/
tmp/pisi-root/
var/log/comar.log
var/log/pisi.log
root/.bash_history
"""

default_install_exclude_list = """
lib/rcscripts/
usr/include/
usr/lib/cups/
usr/lib/python2.6/lib-tk/
usr/lib/python2.6/idlelib/
usr/lib/python2.6/distutils/
usr/lib/python2.6/bsddb/test/
usr/lib/python2.6/lib-old/
usr/lib/python2.6/test/
usr/lib/python2.6/site-packages/PyQt4/QtAssistant.so
usr/lib/python2.6/site-packages/PyQt4/QtDesigner.so
usr/lib/python2.6/site-packages/PyQt4/QtHelp.so
usr/lib/python2.6/site-packages/PyQt4/QtNetwork.so
usr/lib/python2.6/site-packages/PyQt4/QtOpenGL.so
usr/lib/python2.6/site-packages/PyQt4/QtScript.so
usr/lib/python2.6/site-packages/PyQt4/QtSql.so
usr/lib/python2.6/site-packages/PyQt4/QtTest.so
usr/lib/python2.6/site-packages/PyQt4/QtWebKit.so
usr/lib/python2.6/site-packages/PyQt4/QtXml.so
usr/lib/python2.6/site-packages/PyQt4/QtXmlPatterns.so
usr/lib/klibc/include/
usr/lib/syslinux/
usr/qt/4/include/
usr/qt/4/mkspecs/
usr/qt/4/bin/
usr/qt/4/templates/
usr/share/aclocal/
usr/share/cups/
usr/share/doc/
usr/share/gfxtheme/
usr/share/info/
usr/share/sip/
usr/share/man/
usr/share/groff/
usr/share/dict/
var/db/pisi/
var/lib/pisi/
var/cache/pisi/packages/
var/cache/pisi/archives/
var/tmp/pisi/
var/pisi/
tmp/pisi-root/
var/log/comar.log
var/log/pisi.log
root/.bash_history
"""

default_install_glob_excludes = (
    ( "usr/lib/python2.6/", "*.pyc" ),
    ( "usr/lib/python2.6/", "*.pyo" ),
    ( "usr/lib/pardus/", "*.pyc" ),
    ( "usr/lib/pardus/", "*.pyo" ),
    ( "usr/lib/", "*.a" ),
    ( "usr/lib/", "*.la" ),
    ( "lib/", "*.a" ),
    ( "lib/", "*.la" ),
    ( "var/db/comar/", "__db*" ),
    ( "var/db/comar/", "log.*" ),
    ( "usr/qt/4/lib/", "libphononexperimental.so*" ),
    ( "usr/qt/4/lib/", "libphonon.so*" ),
    ( "usr/qt/4/lib/", "libqca.so*" ),
    ( "usr/qt/4/lib/", "libQt3Support.so*" ),
    ( "usr/qt/4/lib/", "libQtAssistantClient.so*" ),
    ( "usr/qt/4/lib/", "libQtCLucene.so*" ),
    ( "usr/qt/4/lib/", "libQtDBus.so*" ),
    ( "usr/qt/4/lib/", "libQtDesignerComponents.so*" ),
    ( "usr/qt/4/lib/", "libQtDesigner.so*" ),
    ( "usr/qt/4/lib/", "libQtHelp.so*" ),
    ( "usr/qt/4/lib/", "libQtNetwork.so*" ),
    ( "usr/qt/4/lib/", "libQtOpenGL.so*" ),
    ( "usr/qt/4/lib/", "libQtScript.so*" ),
    ( "usr/qt/4/lib/", "libQtScriptTools.so*" ),
    ( "usr/qt/4/lib/", "libQtSql.so*" ),
    ( "usr/qt/4/lib/", "libQtTapioca.so*" ),
    ( "usr/qt/4/lib/", "libQtTelepathyClient.so*" ),
    ( "usr/qt/4/lib/", "libQtTest.so*" ),
    ( "usr/qt/4/lib/", "libQtUiTools.so*" ),
    ( "usr/qt/4/lib/", "libQtWebKit.so*" ),
    ( "usr/qt/4/lib/", "libQtXmlPatterns.so*" ),
    ( "usr/qt/4/lib/", "libQtXml.so*" ),
)

default_live_glob_excludes = (
    ( "usr/lib/python2.6/", "*.pyc" ),
    ( "usr/lib/python2.6/", "*.pyo" ),
    ( "usr/lib/pardus/", "*.pyc" ),
    ( "usr/lib/pardus/", "*.pyo" ),
    ( "usr/lib/", "*.a" ),
    ( "usr/lib/", "*.la" ),
    ( "lib/", "*.a" ),
    ( "lib/", "*.la" ),
    ( "var/db/comar/", "__db*" ),
    ( "var/db/comar/", "log.*" ),
    ( "var/lib/pisi/index", "*" ),
    ( "var/lib/pisi/info", "*" ),
    ( "var/lib/pisi/package", "*" ),
)


class ExProject(Exception):
    pass

class ExProjectMissing(Exception):
    pass

class ExProjectBogus(Exception):
    pass


# Project class

class Project:
    def __init__(self):
        self.reset()

    def reset(self):
        self.filename = None
        self.title = ""
        self.work_dir = ""
        self.release_files = ""
        self.repo_uri = ""
        self.type = "install"
        self.squashfs_comp_type = "GZIP"
        self.media = "cd"
        self.extra_params = ""
        self.plugin_package = ""
        self.default_language = None
        self.selected_components = []
        self.selected_languages = []
        self.selected_packages = []
        self.all_packages = []
        self.missing_packages = []
        self.missing_components = []

    def open(self, filename):
        # Open and parse project file filename
        try:
            doc = piksemel.parse(filename)
        except OSError, e:
            if e.errno == 2:
                raise ExProjectMissing
            raise
        except piksemel.ParseError:
            raise ExProjectBogus
        if doc.name() != "PardusmanProject":
            raise ExProjectBogus

        self.reset()
        self.filename = filename

        # Fill in the properties from XML file
        self.title = doc.getTagData("Title")
        self.type = doc.getAttribute("type")
        self.media = doc.getAttribute("media")
        self.squashfs_comp_type = doc.getAttribute("compression")

        self.plugin_package = doc.getTagData("PluginPackage")
        if not self.plugin_package:
            self.plugin_package = ""
        self.release_files = doc.getTagData("ReleaseFiles")
        if not self.release_files:
            self.release_files = ""
        self.extra_params = doc.getTagData("ExtraParameters")
        if not self.extra_params:
            self.extra_params = ""
        self.work_dir = doc.getTagData("WorkDir")
        if not self.work_dir:
            self.work_dir = ""

        # Fill in the packages
        package_selection = doc.getTag("PackageSelection")
        if package_selection:
            self.repo_uri = package_selection.getAttribute("repo_uri")
            for tag in package_selection.tags("SelectedComponent"):
                self.selected_components.append(tag.firstChild().data())
            for tag in package_selection.tags("SelectedPackage"):
                self.selected_packages.append(tag.firstChild().data())
            for tag in package_selection.tags("Package"):
                self.all_packages.append(tag.firstChild().data())

        lang_selection = doc.getTag("LanguageSelection")
        if lang_selection:
            self.default_language = lang_selection.getAttribute("default_language")
            for tag in lang_selection.tags("Language"):
                self.selected_languages.append(tag.firstChild().data())

            if self.default_language not in self.selected_languages:
                self.selected_languages.append(self.default_language)

        # Sort the lists
        self.selected_components.sort()
        self.selected_languages.sort()
        self.selected_packages.sort()
        self.all_packages.sort()


    def save(self, filename=None):
        # Save the data into filename as pardusman project file
        doc = piksemel.newDocument("PardusmanProject")

        doc.setAttribute("type", self.type)
        doc.setAttribute("media", str(self.media))
        doc.setAttribute("compression", str(self.squashfs_comp_type))

        if self.title:
            doc.insertTag("Title").insertData(self.title)
        if self.work_dir:
            doc.insertTag("WorkDir").insertData(self.work_dir)
        if self.release_files:
            doc.insertTag("ReleaseFiles").insertData(self.release_files)
        if self.plugin_package:
            doc.insertTag("PluginPackage").insertData(self.plugin_package)
        if self.extra_params:
            doc.insertTag("ExtraParameters").insertData(self.extra_params)

        if self.repo_uri:
            package_selection = doc.insertTag("PackageSelection")
            package_selection.setAttribute("repo_uri", self.repo_uri)

            # Insert components if any
            for item in self.selected_components:
                package_selection.insertTag("SelectedComponent").insertData(item)

            for item in self.selected_packages:
                package_selection.insertTag("SelectedPackage").insertData(item)

            for item in self.all_packages:
                package_selection.insertTag("Package").insertData(item)

        if self.default_language:
            # Set the default language
            langs = doc.insertTag("LanguageSelection")
            langs.setAttribute("default_language", self.default_language)

            # Insert other supported languages if any
            for item in self.selected_languages:
                langs.insertTag("Language").insertData(item)

        # Write the file
        if not filename:
            filename = self.filename
        f = file(filename, "w")
        f.write(doc.toPrettyString())
        f.close()

    def exclude_list(self):
        import fnmatch

        def _glob_exclude(lst, excludes):
            image_dir = self.image_dir()
            for exc in excludes:
                path = os.path.join(image_dir, exc[0])
                for root, dirs, files in os.walk(path):
                    for name in files:
                        if fnmatch.fnmatch(name, exc[1]):
                            lst.append(os.path.join(root[len(image_dir)+1:], name))

        if self.type == "install":
            temp = default_install_exclude_list.split()
            _glob_exclude(temp, default_install_glob_excludes)
        else:
            temp = default_live_exclude_list.split()
            _glob_exclude(temp, default_live_glob_excludes)
        return temp

    def _get_dir(self, name, clean=False):
        dirname = os.path.join(self.work_dir, name)
        if os.path.exists(dirname):
            if clean:
                os.system('rm -rf "%s"' % dirname)
                os.makedirs(dirname)
        else:
            os.makedirs(dirname)
        return dirname

    def get_repo(self, console=None, update_repo=False):
        cache_dir = self._get_dir("repo_cache")
        repo = packages.Repository(self.repo_uri, cache_dir)
        repo.parse_index(console, update_repo)
        self.find_all_packages(repo)
        return repo

    def get_missing(self):
        return self.missing_components, self.missing_packages

    def find_all_packages(self, repo):
        self.missing_packages = []
        self.missing_components = []
        packages = []
        def collect(name):
            if name not in repo.packages:
                if name not in self.missing_packages:
                    self.missing_packages.append(name)
                return
            p = repo.packages[name]
            if name in packages:
                return
            packages.append(name)
            for dep in p.depends:
                collect(dep)
        for component in self.selected_components:
            if component not in repo.components:
                if component not in self.missing_components:
                    self.missing_components.append(component)
                return
            for package in repo.components[component]:
                collect(package)

        for package in self.selected_packages:
            collect(package)
        packages.sort()
        self.all_packages = packages

    def image_repo_dir(self, clean=False):
        return self._get_dir("image_repo", clean)

    def image_dir(self, clean=False):
        return self._get_dir("image", clean)

    def image_file(self):
        return os.path.join(self.work_dir, "pardus.img")

    def install_repo_dir(self, clean=False):
        return self._get_dir("install_repo", clean)

    def iso_dir(self, clean=False):
        return self._get_dir("iso", clean)

    def iso_file(self, clean=True):
        path = os.path.join(self.work_dir, "%s.iso" % self.title.replace(" ", "_"))
        if clean and os.path.exists(path):
            os.unlink(path)
        return path
