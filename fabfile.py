#!/usr/bin/env python
# -*- coding: utf-8 -*-
# fabfile for Django:
# http://morethanseven.net/2009/07/27/fabric-django-git-apache-mod_wsgi-virtualenv-and-p/
# modified for fabric 0.9/1.0
from __future__ import with_statement # needed for python 2.5
from fabric.api import *

# globals
env.project_name = 'project_name' # no spaces!
env.use_photologue = False # django-photologue gallery module
env.use_medialibrary = False # feincms.medialibrary or similar
env.webserver = 'nginx' # nginx or apache2 (directory name below /etc!)

# environments

def localhost():
    "Use the local virtual server"
    env.hosts = ['localhost']
    env.user = 'hraban' # You must create and sudo-enable the user first!
    env.path = '/Users/%(user)s/workspace/%(project_name)s' % env # User home on OSX, TODO: check local OS
    env.virtualhost_path = env.path

def webserver():
    "Use the actual webserver"
    env.hosts = ['zipanu.fiee.net'] # Change to your server name!
    env.user = env.project_name
    env.path = '/var/www/%(project_name)s' % env
    env.virtualhost_path = env.path
    
# tasks

def test():
    "Run the test suite and bail out if it fails"
    local("cd %(path)s; python manage.py test" % env) #, fail="abort")
    
    
def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    """
    require('hosts', provided_by=[localhost,webserver])
    require('path')
    sudo('apt-get install build-essentials python-dev python-setuptools') # python-imaging?
    #sudo('apt-get install daemontools') # not available for hardy!
    sudo('easy_install pip')
    sudo('pip install -U virtualenv flup')
    if env.webserver=='nginx':
        sudo('apt-get install nginx')
    else:
        sudo('apt-get install apache2-threaded')
        #sudo('aptitude install -y libapache2-mod-wsgi') # outdated on hardy!
    # disable default site
    sudo('cd /etc/%(webserver)s/sites-enabled/; rm default;' % env, pty=True)
    sudo('mkdir -p %(path)s; chown %(user)s:%(user)s %(path)s;' % env, pty=True)
    run('ln -s %(path)s www;' % env, pty=True) # symlink web dir in home
    with cd(env.path):
        run('virtualenv .;' % env, pty=True)
        run('mkdir logs; chmod a+w logs; mkdir releases; mkdir shared; mkdir packages;' % env, pty=True)
        if env.use_photologue: run('mkdir photologue', pty=True);
        if env.use_medialibrary: run('mkdir medialibrary', pty=True);
        run('cd releases; ln -s . current; ln -s . previous;', pty=True)
    deploy()
    
def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """
    require('hosts', provided_by=[localhost,webserver])
    require('path')
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    upload_tar_from_git()
    install_requirements()
    install_site()
    symlink_current_release()
    migrate()
    restart_webserver()
    
def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', provided_by=[localhost,webserver])
    require('path')
    env.version = version
    with cd(env.path):
        run('rm -rf releases/previous; mv releases/current releases/previous;', pty=True)
        run('ln -s %(version)s releases/current' % env, pty=True)
    restart_webserver()
    
def rollback():
    """
    Limited rollback capability. Simply loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    require('hosts', provided_by=[localhost,webserver])
    require('path')
    with cd(env.path):
        run('mv releases/current releases/_previous;', pty=True)
        run('mv releases/previous releases/current;', pty=True)
        run('mv releases/_previous releases/previous;', pty=True)
    restart_webserver()    
    
# Helpers. These are called by other functions rather than directly

def upload_tar_from_git():
    "Create an archive from the current Git master branch and upload it"
    require('release', provided_by=[deploy, setup])
    local('git archive --format=tar master | gzip > %(release)s.tar.gz' % env)
    run('mkdir -p %(path)s/releases/%(release)s' % env, pty=True)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env, pty=True)
    local('rm %(release)s.tar.gz' % env)
    
def install_site():
    "Add the virtualhost file to the webserver's config"
    require('release', provided_by=[deploy, setup])
    sudo('cd %(path)s/releases/%(release)s; cp %(webserver)s.conf /etc/%(webserver)s/sites-available/%(project_name)s' % env, pty=True)
    sudo('cd /etc/%(webserver)s/sites-enabled/; ln -s ../sites-available/%(project_name)s %(project_name)s' % env, pty=True) 
    
def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    run('cd %(path)s; pip install -E . -r ./releases/%(release)s/requirements.txt' % env, pty=True)
    
def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, setup])
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous;', pty=True)
        run('ln -s %(release)s releases/current' % env, pty=True)
        if env.use_photologue:
            run('cd releases/current/%(project_name)s/static; rm -rf photologue; ln -s %(path)s/photologue;' % env, pty=True)
    
def migrate():
    "Update the database (doesn't really make sense - no migration)"
    require('project_name')
    run('cd %(path)s/releases/current/%(project_name)s; ../../../bin/python manage.py syncdb --noinput' % env, pty=True)
    
def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/%(webserver)s reload' % env, pty=True)
