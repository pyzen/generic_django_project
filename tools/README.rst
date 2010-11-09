Tools for Django/Nginx
======================

Server management helpers for my setup:

* setup

  - server-setup.rst_: some hints what to do with a new (virtual) server
  - makeuser.sh: create user, database and web directory for a new project
  - package.list: my selection of installed packages on a new virtual server with Debian 5.0 (Lenny)
  - copysite.sh: copy a complete site from another server (use for server migrations)

* process management with fcgi (obsolete with gunicorn)

  - nginxsite.sh: start/stop one Django site running on fcgi behind Nginx
  - websites-init.sh: start/stop/restart all Django sites (use e.g. as startup script)

Some of these functions will migrate to the fabfile sometime...

.. _server-setup.rst: _server-setup.rst
