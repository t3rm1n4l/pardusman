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
import re
import sys
import stat
import time
import dbus
import glob
import hashlib
import tempfile

from repotools.utility import xterm_title, wait_bus

#
# Utilities
#

def run(cmd, ignore_error=False):
    print cmd
    ret = os.system(cmd)
    if ret and not ignore_error:
        print "%s returned %s" % (cmd, ret)
        sys.exit(1)

def connectToDBus(path):
    global bus
    bus = None
    for i in range(20):
        try:
            print("trying to start dbus..")
            bus = dbus.bus.BusConnection(address_or_type="unix:path=%s/var/run/dbus/system_bus_socket" % path)
            break
        except dbus.DBusException:
            time.sleep(1)
            print("wait dbus for 1 second...")
    if bus:
        return True
    return False

def chroot_comar(image_dir):
    if os.fork() == 0:
        # Workaround for creating ISO's on 2007 with PiSi 2.*
        # Create non-existing /var/db directory before running COMAR
        try:
            os.makedirs(os.path.join(image_dir, "var/db"), 0700)
        except OSError:
            pass
        os.chroot(image_dir)
        if not os.path.exists("/var/lib/dbus/machine-id"):
            run("/usr/bin/dbus-uuidgen --ensure")

        run("/sbin/start-stop-daemon -b --start --pidfile /var/run/dbus/pid --exec /usr/bin/dbus-daemon -- --system")
        sys.exit(0)
    wait_bus("%s/var/run/dbus/system_bus_socket" % image_dir)

def get_exclude_list(project):
    exc = project.exclude_list()[:]
    image_dir = project.image_dir()
    path = image_dir + "/boot"
    for name in os.listdir(path):
        if name.startswith("kernel") or name.startswith("initramfs"):
            exc.append("boot/" + name)
    return exc

#
# Grub related stuff
#

def generate_grub_conf(project, kernel, initramfs):
    print "Generating grub.conf files..."
    xterm_title("Generating grub.conf files")

    image_dir = project.image_dir()
    iso_dir = project.iso_dir()

    dict = {}
    dict["kernel"] = kernel
    dict["initramfs"] = initramfs
    dict["title"] = project.title
    dict["exparams"] = project.extra_params or ''

    path = os.path.join(image_dir, "usr/share/grub/templates")
    dest = os.path.join(iso_dir, "boot/grub")
    for name in os.listdir(path):
        if name.startswith("menu"):
            data = file(os.path.join(path, name)).read()
            f = file(os.path.join(dest, name), "w")
            f.write(data % dict)
            f.close()

def setup_grub(project):
    image_dir = project.image_dir()
    iso_dir = project.iso_dir()
    kernel = ""
    initramfs = ""

    # Setup dir
    path = os.path.join(iso_dir, "boot/grub")
    if not os.path.exists(path):
        os.makedirs(path)

    def copy(src, dest):
        run('cp -P "%s" "%s"' % (src, os.path.join(iso_dir, dest)))

    # Copy the kernel and initramfs
    path = os.path.join(image_dir, "boot")
    for name in os.listdir(path):
        if name.startswith("kernel") or name.startswith("initramfs") or name.endswith(".bin"):
            if name.startswith("kernel"):
                kernel = name
            elif name.startswith("initramfs"):
                initramfs = name
            copy(os.path.join(path, name), "boot/" + name)

    # and the other files
    path = os.path.join(image_dir, "boot/grub")
    for name in os.listdir(path):
        copy(os.path.join(path, name), "boot/grub/" + name)

    # Generate the config file
    generate_grub_conf(project, kernel, initramfs)

def generate_isolinux_conf(project):
    print "Generating isolinux config files..."
    xterm_title("Generating isolinux config files")

    dict = {}
    dict["title"] = project.title
    dict["exparams"] = project.extra_params or ''

    image_dir = project.image_dir()
    iso_dir = project.iso_dir()

    lang_default = project.default_language
    lang_all = project.selected_languages

    isolinux_tmpl = """
prompt 1
timeout 200

ui gfxboot.com /boot/isolinux/init

label pardus
    kernel /boot/kernel
    append initrd=/boot/initrd root=/dev/ram0 splash=silent quiet %(exparams)s

label rescue
    kernel /boot/kernel
    append initrd=/boot/initrd root=/dev/ram0 yali4=rescue splash=silent quiet %(exparams)s

label harddisk
    localboot 0x80

label memtest
    kernel /boot/memtest

label hardware
    kernel hdt.c32
"""

    # write isolinux.cfg
    dest = os.path.join(iso_dir, "boot/isolinux/isolinux.cfg")
    data = isolinux_tmpl % dict

    f = file(dest, "w")
    f.write(data % dict)
    f.close()

    # write gfxboot config for title
    data = file(os.path.join(image_dir, "usr/share/gfxtheme/pardus/install/gfxboot.cfg")).read()
    f = file(os.path.join(iso_dir, "boot/isolinux/gfxboot.cfg"), "w")
    f.write(data % dict)
    f.close()

    if len(lang_all) and lang_default != "":
        langdata = ""

        if not lang_default in lang_all:
            lang_all.append(lang_default)

        lang_all.sort()

        for i in lang_all:
            langdata += "%s\n" % i


        # write default language
        f = file(os.path.join(iso_dir, "boot/isolinux/lang"), "w")
        f.write("%s\n" % lang_default)
        f.close()

        # write available languages
        f = file(os.path.join(iso_dir, "boot/isolinux/languages"), "w")
        f.write(langdata)
        f.close()


def setup_isolinux(project):
    print "Generating isolinux files..."
    xterm_title("Generating isolinux files")

    image_dir = project.image_dir()
    iso_dir = project.iso_dir()
    repo = project.get_repo()
    kernel = ""
    initramfs = ""

    # Setup dir
    path = os.path.join(iso_dir, "boot/isolinux")
    if not os.path.exists(path):
        os.makedirs(path)

    def copy(src, dest):
        run('cp -P "%s" "%s"' % (src, os.path.join(iso_dir, dest)))

    # Copy the kernel and initramfs
    path = os.path.join(image_dir, "boot")
    for name in os.listdir(path):
        if name.startswith("kernel") or name.startswith("initramfs") or name.endswith(".bin"):
            if name.startswith("kernel"):
                copy(os.path.join(path, name), "boot/kernel")
            elif name.startswith("initramfs"):
                copy(os.path.join(path, name), "boot/initrd")

    tmplpath = os.path.join(image_dir, "usr/share/gfxtheme/pardus/install")
    dest = os.path.join(iso_dir, "boot/isolinux")
    for name in os.listdir(tmplpath):
        if name != "gfxboot.cfg":
            copy(os.path.join(tmplpath, name), dest)

    # copy config and gfxboot stuff
    generate_isolinux_conf(project)

    copy(os.path.join(image_dir, "usr/lib/syslinux/isolinux-debug.bin"), "%s/isolinux.bin" % dest)
    copy(os.path.join(image_dir, "usr/lib/syslinux/hdt.c32"), dest)
    copy(os.path.join(image_dir, "usr/lib/syslinux/gfxboot.com"), dest)
    copy(os.path.join(image_dir, "usr/share/misc/pci.ids"), dest)
    copy(os.path.join(image_dir, "lib/modules/%s-%s/modules.pcimap" % (repo.packages["kernel"].version, repo.packages["kernel"].release)), dest)
    copy(os.path.join(image_dir, "boot/memtest"), os.path.join(iso_dir, "boot"))



#
# Setup default wallpaper, hostname, home folder contents
#

def setup_userfiles_uploads(project):
    import shutil, tarfile

    plasmarc = """
[Containments][1]
activity=
desktop=0
formfactor=0
geometry=0,0,1280,800
immutability=1
location=0
plugin=desktop
screen=0
wallpaperplugin=image
wallpaperpluginmode=SingleImage
zvalue=0

[Containments][1][Applets][2]
activity=
desktop=-1
formfactor=0
geometry=6,6,600,400
immutability=1
location=0
plugin=folderview
screen=-1
zvalue=-2

[Containments][1][Applets][2][Configuration]
activity=
desktop=-1
formfactor=0
geometry=6,6,600,400
immutability=1
location=0
plugin=folderview
screen=-1
url=desktop:/
zvalue=0

[Containments][1][Wallpaper][image]
fadeEffect=true
slideTimer=600
slidepaths=/usr/kde/4/share/wallpapers/
userswallpapers=
wallpaper=/usr/kde/4/share/wallpapers/default.png
wallpapercolor=56,111,150
wallpaperposition=0

[Containments][3]
activity=
desktop=-1
formfactor=2
geometry=0,-56,1260,50
immutability=1
location=4
plugin=panel
screen=0
zvalue=150

[Containments][3][Applets][10]
geometry=1048,6,44,44
immutability=1
plugin=battery
zvalue=0

[Containments][3][Applets][11]
geometry=1096,6,44,44
immutability=1
plugin=nm-applet
zvalue=0

[Containments][3][Applets][12]
geometry=1144,6,88,44
immutability=1
plugin=digital-clock
zvalue=0

[Containments][3][Applets][12][Configuration][PopupApplet]
DialogHeight=270
DialogWidth=250

[Containments][3][Applets][4]
geometry=6,6,44,44
immutability=1
plugin=launcher
zvalue=0

[Containments][3][Applets][4][Shortcuts]
global=Alt+F1

[Containments][3][Applets][5]
geometry=54,6,44,44
immutability=1
plugin=showdesktop
zvalue=0

[Containments][3][Applets][6]
geometry=102,6,44,44
immutability=1
plugin=notifier
zvalue=0

[Containments][3][Applets][7]
geometry=150,6,58,44
immutability=1
plugin=pager
zvalue=0

[Containments][3][Applets][8]
geometry=212,6,746,44
immutability=1
plugin=tasks
zvalue=0

[Containments][3][Applets][9]
geometry=962,6,82,44
immutability=1
plugin=systemtray
zvalue=0

[Containments][3][Applets][9][Configuration][PopupApplet]
DialogHeight=8
DialogWidth=0

[Containments][3][Configuration]
maximumSize=1260,50
minimumSize=1260,50
"""

    image_dir = project.image_dir()

    if project.wallpaper:
        shutil.copyfile(os.path.join(project.project_dir,project.wallpaper),os.path.join(image_dir,'usr/kde/4/share/wallpapers/default.png'))
        run('mkdir -p %s/etc/skel/.kde4/share/config/' %image_dir)
        handle = file(os.path.join(image_dir,'etc/skel/.kde4/share/config/plasma-appletsrc'),'w+')
        handle.write(plasmarc)
        handle.close()

    if project.user_contents:
        path = os.path.join(project.project_dir,project.user_contents)

        tar = tarfile.open(path,'r:gz')
        tar.extractall(os.path.join(image_dir,'etc/skel/'))
        tar.close()

    if project.hostname:
        handle = file(os.path.join(image_dir,"etc/env.d/01hostname"),'w+')
        handle.write('HOSTNAME="%s"\n' % project.hostname)
        handle.close()




    

def setup_live_kdm(project):
    image_dir = project.image_dir()
    if "kdebase" in project.all_packages :
        path = os.path.join(image_dir, "etc/X11/kdm/kdmrc")
    elif "kdebase4" in project.all_packages :
        # FIXME : find a generic way to do this
        # Heyaa, there's no kdebase4 in 2009, this should be fixed!
        path = os.path.join(image_dir, "etc/X11/kdm/kdmrc4")
    lines = []
    for line in file(path):
        if line.startswith("#AutoLoginEnable"):
            lines.append("AutoLoginEnable=true\n")
        elif line.startswith("#AutoLoginUser"):
            lines.append("AutoLoginUser=%s\n" %project.username)
        else:
            lines.append(line)
    file(path, "w").write("".join(lines))

def setup_live_policykit_conf(project):
    policykit_conf_tmpl = """<?xml version="1.0" encoding="UTF-8"?> <!-- -*- XML -*- -->

<!DOCTYPE pkconfig PUBLIC "-//freedesktop//DTD PolicyKit Configuration 1.0//EN"
"http://hal.freedesktop.org/releases/PolicyKit/1.0/config.dtd">

<!-- See the manual page PolicyKit.conf(5) for file format -->

<config version="0.1">
    <define_admin_auth group="wheel"/>
    <match user="%s">
        <return result="yes"/>
    </match>
</config>
""" %project.username

    # Write PolicyKit.conf
    image_dir = project.image_dir()
    dest = os.path.join(image_dir, "etc/PolicyKit/PolicyKit.conf")

    f = file(dest, "w")
    f.write(policykit_conf_tmpl)
    f.close()

def copyPisiIndex(project):
    image_dir = project.image_dir()
    path = os.path.join(image_dir, "usr/share/yali4/data/pisi-index.xml.bz2")
    repo = os.path.join(project.work_dir, "repo_cache/pisi-index.xml.bz2")

    run('cp -PR "%s" "%s"' % (repo, path))
    run('sha1sum "%s" > "%s"' % (repo, "%s.sha1sum" % path))
    print('cp -PR "%s" "%s"' % (repo, path))
    print('sha1sum "%s" > "%s"' % (repo, "%s.sha1sum" % path))

def install_packages(project):
    image_dir = project.image_dir()
    path = os.path.join(image_dir, "var/lib/pisi/package")
    for name in project.all_packages:
        flag = True
        if os.path.exists(path):
            for avail in os.listdir(path):
                if avail.startswith(name) and avail[len(name)] == "-":
                    flag = False
        if flag:
            run('pisi --yes-all --ignore-comar --ignore-file-conflicts -D"%s" it %s' % (image_dir, name))

def squash_image(project):
    image_dir = project.image_dir()
    image_file = project.image_file()

    if not image_dir.endswith("/"):
        image_dir += "/"
    temp = tempfile.NamedTemporaryFile()
    f = file(temp.name, "w")
    f.write("\n".join(get_exclude_list(project)))
    f.close()

    run('mksquashfs "%s" "%s" -noappend -ef "%s"' % (image_dir, image_file, temp.name))
    # FIXME
    #if project.squashfs_comp_type == 'LZMA':
    #    run('mksquashfs "%s" "%s" -noappend -ef "%s"' % (image_dir, image_file, temp.name))
    #else:
    #    run('mksquashfs "%s" "%s" -nolzma -noappend -ef "%s"' % (image_dir, image_file, temp.name))

#
# Operations
#

def make_repos(project):
    print "Preparing image repo..."
    xterm_title("Preparing image repo")

    try:
        repo = project.get_repo()
        repo_dir = project.image_repo_dir(clean=True)
        if project.type == "install":
            imagedeps = repo.full_deps("yali4")
        else:
            imagedeps = project.all_packages
        repo.make_local_repo(repo_dir, imagedeps)

        if project.type == "install":
            xterm_title("Preparing installination repo")
            print "Preparing installation repository..."

            repo_dir = project.install_repo_dir(clean=True)
            repo.make_local_repo(repo_dir, project.all_packages)
    except KeyboardInterrupt:
        print "Keyboard Interrupt: make_repo() cancelled."
        sys.exit(1)

def check_file(repo_dir, name, hash):
    path = os.path.join(repo_dir, name)
    if not os.path.exists(path):
        print "\nPackage missing: %s" % path
        return
    data = file(path).read()
    cur_hash = hashlib.sha1(data).hexdigest()
    if cur_hash != hash:
        print "\nWrong hash: %s" % path

def check_repo_files(project):
    print "Checking image repo..."
    xterm_title("Checking image repo")

    try:
        repo = project.get_repo()
        repo_dir = project.image_repo_dir()
        if project.type == "install":
            imagedeps = repo.full_deps("yali4")
        else:
            imagedeps = project.all_packages
        i = 0
        for name in imagedeps:
            i += 1
            sys.stdout.write("\r%-70.70s" % "Checking %d of %s packages" % (i, len(imagedeps)))
            sys.stdout.flush()
            pak = repo.packages[name]
            check_file(repo_dir, pak.uri, pak.sha1sum)
        sys.stdout.write("\n")

        if project.type == "install":
            repo_dir = project.install_repo_dir()
            i = 0
            for name in project.all_packages:
                i += 1
                sys.stdout.write("\r%-70.70s" % "Checking %d of %s packages" % (i, len(project.all_packages)))
                sys.stdout.flush()
                pak = repo.packages[name]
                check_file(repo_dir, pak.uri, pak.sha1sum)
        sys.stdout.write("\n")
    except KeyboardInterrupt:
        print "Keyboard Interrupt: check_repo() cancelled."
        sys.exit(1)

def make_image(project):
    global bus

    print "Preparing install image..."
    xterm_title("Preparing install image")


    try:
        repo = project.get_repo()
        repo_dir = project.image_repo_dir()
        image_file = project.image_file()

        image_dir = project.image_dir()
        run('umount %s/proc' % image_dir, ignore_error=True)
        run('umount %s/sys' % image_dir, ignore_error=True)
        image_dir = project.image_dir(clean=True)

        run('pisi --yes-all -D"%s" ar pardus-install %s' % (image_dir, repo_dir + "/pisi-index.xml.bz2"))
        if project.type == "install":
            run('pisi --yes-all --ignore-comar -D"%s" it yali4' % image_dir)
            if project.plugin_package:
                plugin_package = project.plugin_package
                run('pisi --yes-all --ignore-comar -D"%s" it %s' % (image_dir, plugin_package))
        else:
            install_packages(project)

            setup_userfiles_uploads(project)


        def chrun(cmd):
            run('chroot "%s" %s' % (image_dir, cmd))

        os.mknod("%s/dev/null" % image_dir, 0666 | stat.S_IFCHR, os.makedev(1, 3))
        os.mknod("%s/dev/console" % image_dir, 0666 | stat.S_IFCHR, os.makedev(5, 1))
        os.mknod("%s/dev/random" % image_dir, 0666 | stat.S_IFCHR, os.makedev(1, 8))
        os.mknod("%s/dev/urandom" % image_dir, 0666 | stat.S_IFCHR, os.makedev(1, 9))

        path = "%s/usr/share/baselayout/" % image_dir
        path2 = "%s/etc" % image_dir
        for name in os.listdir(path):
            run('cp -p "%s" "%s"' % (os.path.join(path, name), os.path.join(path2, name)))
        run('/bin/mount --bind /proc %s/proc' % image_dir)
        run('/bin/mount --bind /sys %s/sys' % image_dir)

        chrun("/sbin/ldconfig")
        chrun("/sbin/update-environment")
        chroot_comar(image_dir)
        chrun("/usr/bin/pisi configure-pending baselayout")
        chrun("/usr/bin/pisi configure-pending")

        # FIXME : find a generic way to do this
        if "kdebase4" in project.all_packages:
            # Disable Nepomuk in live CDs
            if project.type == "live":
                os.unlink("%s/usr/kde/4/share/autostart/nepomukserver.desktop" % image_dir)

        if project.type == "install":
            # FIXME: Do not hard code installer name
            dm_config = "DISPLAY_MANAGER=yali4"

            # Write default display manager config
            image_dir = project.image_dir()
            dest = os.path.join(image_dir, "etc/default/xdm")

            f = file(dest, "w")
            f.write(dm_config)
            f.close()

        connectToDBus(image_dir)

        obj = bus.get_object("tr.org.pardus.comar", "/package/baselayout")

        obj.setUser(0, "", "", "", project.password, "", dbus_interface="tr.org.pardus.comar.User.Manager")
        if project.type != "install":
            obj.addUser(1000, project.username, project.username, os.path.join('/home',project.username), "/bin/bash", project.password, ["wheel", "users", "pnp", "pnpadmin", "removable", "disk", "audio", "video", "power", "dialout"], [], [], dbus_interface="tr.org.pardus.comar.User.Manager")

        chrun("/sbin/depmod -a %s-%s" % (repo.packages["kernel"].version, repo.packages["kernel"].release))

        path1 = os.path.join(image_dir, "usr/share/baselayout/inittab.live")
        path2 = os.path.join(image_dir, "etc/inittab")
        os.unlink(path2)
        run('mv "%s" "%s"' % (path1, path2))

        file(os.path.join(image_dir, "etc/pardus-release"), "w").write("%s\n" % project.title)

        if project.type != "install" and ("kdebase" in project.all_packages or "kdebase4" in project.all_packages):
            setup_live_kdm(project)
            setup_live_policykit_conf(project)

        if project.type == "install":
            copyPisiIndex(project)

        # Make sure environment is updated regardless of the booting system, by setting comparison
        # files' atime and mtime to UNIX time 1

        os.utime(os.path.join(image_dir, "etc/profile.env"), (1, 1))

        run('umount %s/proc' % image_dir)
        run('umount %s/sys' % image_dir)
    except KeyboardInterrupt:
        print "Keyboard Interrupt: make_image() cancelled."
        sys.exit(1)

def generate_sort_list(iso_dir):
    # Sorts the packages in repo_dir according to their size
    # mkisofs sort_file format:
    # filename   weight
    # where filename is the whole name of a file/directory and the weight is a whole
    # number between +/- 2147483647. Files will be sorted with the highest weights first
    # and lowest last. The CDs are written from the middle outwards.
    # High weighted files will be nearer to the inside of the CD.
    # Highest weight -> nearer to the inside,
    # lowest weight -> outwards
    packages = glob.glob("%s/repo/*.pisi" % iso_dir)
    package_list = dict([(k, os.stat(k).st_size) for k in packages]).items()
    package_list.sort(key=lambda x: x[1], reverse=True)

    for i in xrange(len(packages)):
        package_list.insert(i, (package_list.pop(i)[0], 100+10*i))

    # Move baselayout to the top
    for p in package_list:
        if "baselayout" in p[0]:
            package_list.insert(0, package_list.pop(package_list.index(p)))

    return package_list


def make_iso(project):
    print "Preparing ISO..."
    xterm_title("Preparing ISO")

    sort_cd_layout = False

    try:
        iso_dir = project.iso_dir(clean=True)
        iso_file = project.iso_file(clean=True)
        image_dir = project.image_dir()
        image_file = project.image_file()

        os.link(image_file, os.path.join(iso_dir, "pardus.img"))

        def copy(src, dest):
            run('cp -PR "%s" "%s"' % (src, os.path.join(iso_dir, dest)))


        if project.release_files:
            path = os.path.join(project.project_dir, project.release_files)

            copy(path,"RELEASE.txt")
            os.chmod(os.path.join(iso_dir,"RELEASE.txt"),655)


        # setup_grub(project)
        setup_isolinux(project)

        if project.type == "install":
            run('ln -s "%s" "%s"' % (project.install_repo_dir(), os.path.join(iso_dir, "repo")))

        # Generate sort_list for mkisofs and YALI
        # Disabled for now
        if sort_cd_layout:
            sorted_list = generate_sort_list(iso_dir)
            if sorted_list:
                open("%s/repo/install.order" % iso_dir, "w").write("\n".join(["%s %d" % (k,v) for (k,v) in sorted_list]))
                run('mkisofs -f -sort %s/repo/install.order -J -joliet-long -R -l -V "Pardus" -o "%s" -b boot/isolinux/isolinux.bin -c boot/isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table "%s"' % (iso_dir, iso_file, iso_dir,))

        else:
            run('mkisofs -f -J -joliet-long -R -l -V "Pardus" -o "%s" -b boot/isolinux/isolinux.bin -c boot/isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table "%s"' % (iso_file, iso_dir,))

    except KeyboardInterrupt:
        print "Keyboard Interrupt: make_iso() cancelled."
        sys.exit(1)


def make(project):

    make_image(project)
    if project.type == "install":
        make_install_repo(project)
    make_iso(project)
    print "ISO is ready!"
    xterm_title("ISO is ready")
