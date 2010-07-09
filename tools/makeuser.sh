#!/bin/bash
# Create a new user and database for a project

USER=$1
PASS=$2
WEBDIR=/var/www
USCRIPT=userscript.sql;

if [ "${PASS}" == "" ]; then
  echo "Missing parameter!"
  echo "Usage: $0 username password"
  exit 1
fi
exit

if [ ! -d "/home/${USER}" ]; then
  echo "User ${USER} is to be created"
  adduser "${USER}"
fi

echo "Adding ${USER} to group wheel"
adduser "${USER}" wheel

echo "Creating website directory ${WEBDIR}/${USER}"
mkdir "${WEBDIR}/${USER}"
chown -R "${USER}:${USER}" "${WEBDIR}/${USER}"
echo "Creating symlink in user's home"
ln -s "${WEBDIR}/${USER}" "/home/${USER}/www"
chown -R "${USER}:${USER}" "/home/${USER}"

echo "use mysql;
create user '${USER}'@'localhost' identified by '${PASS}';
create database ${USER} character set 'utf8';
grant all privileges on ${USER}.* to '${USER}'@'localhost';
flush privileges;
exit;
" > ${USCRIPT}
chmod a+r ${USCRIPT}

echo "Starting MySQL. For creating database and user ${USER}, please call:
\. ${USCRIPT}
"
mysql -u root -p
rm ${USCRIPT}
