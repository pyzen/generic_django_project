Setup for a new sever
=====================

# create group wheel
adduser --group wheel

# visudo:
Defaults targetpw # ask for root password - makes sense?
%wheel ALL=(ALL) ALL

# set root password for MySQL
mysqladmin -u root password 'ROOTPW'

# install packages
# add repo for RabbitMQ:
echo "
deb http://www.rabbitmq.com/debian/ testing main
" >> /etc/apt/sources.list
# see package.list

# install ConTeXt
# see http://wiki.contextgarden.net/ConTeXt_Minimals
mkdir /var/opt/context
cd /var/opt/context
rsync -av rsync://contextgarden.net/minimals/setup/first-setup.sh .
sh ./first-setup.sh

# .bashrc:
export PATH=$PATH:/var/opt/context/tex/texmf-linux-64/bin
. /var/opt/context/tex/setuptex

# TODO: SSH setup
# copy authenticated_hosts to /etc/skel/.ssh
