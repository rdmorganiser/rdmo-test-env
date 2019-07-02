RDMO test environment
=====================

This repository contains documentation and config files to set up a test enviroment for RDMO. In particular services for LDAP and Shibboleth authentication.

*Important:* These instructions are not meant for a production system. We will use a weak passwords and a non save workflow for certificate signing.

Currently, the setup consists of virtual machines, with no automatic setup, but this might change (i.e. using ansible, docker, vagrant).


Certificate authority
---------------------

In a first step we setup a private CA to sign valid certificate (for our test setup). See `ssl/Makefile` and `ssl/ca.cnf` for the fun part.

```
cd ssl
make
```

Answer all questions correctly. This is the first test...

Import `ssl/ca/test.rdmo.org.crt` into your browser.


xenial VM
----------

This is the master VM from which all other VM are cloned.

HD: 20 Gb
Network: Bridged
Image: ubuntu-18.04.2-live-server-amd64.iso

Install with standard options.
After Install set `preserve_hostname: true` in `/etc/cloud/cloud.cfg`


rdmo-ldap VM
------------

This is the machine for the LDAP holding the user accounts.

Clone `xenial-master`.

```bash
hostnamectl set-hostname ldap.test.rdmo.org
reboot
```

### LDAP

```
apt install slapd ldap-utils
dpkg-reconfigure slapd
```

with

```

    Omit OpenLDAP server configuration? No
    DNS domain name?
        This option will determine the base structure of your directory path. Read the message to understand exactly how this will be implemented. You can actually select whatever value you'd like, even if you don't own the actual domain. However, this tutorial assumes you have a proper domain name for the server, so you should use that. We'll use example.com throughout the tutorial.
    Organization name?
        For this guide, we will be using example as the name of our organization. You may choose anything you feel is appropriate.
    Administrator password? enter a secure password twice
    Database backend? MDB
    Remove the database when slapd is purged? No
    Move old database? Yes
    Allow LDAPv2 protocol? No

```

```bash
ufw allow ldap
```

```bash
ldapwhoami -H ldap:// -x
```

Returns `anonymous`.

### SSL

```bash
usermod -aG ssl-cert openldap
systemctl restart slapd
```

Copy:

* `ssl/ca/test.rdmo.org.crt` to `/usr/local/share/ca-certificates/` on `ldap.test.rdmo.org`
* `ssl/ldap.test.rdmo.org.crt` to `/etc/ssl/certs/` on `ldap.test.rdmo.org`
* `ssl/ldap.test.rdmo.org.key` to `/etc/ssl/private/` on `ldap.test.rdmo.org`

```
update-ca-certificates
```

```bash
chgrp ssl-cert /etc/ssl/private
chgrp ssl-cert /etc/ssl/private/ldap.test.rdmo.org.key
chmod 750 /etc/ssl/private/
chmod 640 /etc/ssl/private/ldap.test.rdmo.org.key
```

Copy `ldap` to `/root/ldap` on `ldap.test.rdmo.org`.

```bash
ldapmodify -H ldapi:// -Y EXTERNAL -f /root/ldap/ssl.ldif -v
```

### Users and Groups

```
ldapadd -x -D "cn=admin,dc=ldap,dc=test,dc=rdmo,dc=org" -w admin -f /root/ldap/users.ldif
ldapadd -x -D "cn=admin,dc=ldap,dc=test,dc=rdmo,dc=org" -w admin -f /root/ldap/groups.ldif
```

Check:

```
ldapsearch -v -x -D "uid=rdmo,dc=ldap,dc=test,dc=rdmo,dc=org" -w rdmo -b "dc=ldap,dc=test,dc=rdmo,dc=org" -s sub 'uid=ldap_user'
ldapsearch -v -x -D "uid=rdmo,dc=ldap,dc=test,dc=rdmo,dc=org" -w rdmo -b "dc=ldap,dc=test,dc=rdmo,dc=org" -s sub 'objectClass=groupOfNames'
```

rdmo-app VM
-----------

This is the `rdmo-app` to be user with the LDAP directly.

Clone `xenial-master`.

```bash
hostnamectl set-hostname app.test.rdmo.org
reboot
```

Copy:

* `ssl/ca/test.rdmo.org.crt` to `/usr/local/share/ca-certificates/` on `app.test.rdmo.org`
* `ssl/app.test.rdmo.org.crt` to `/etc/ssl/certs/` on `app.test.rdmo.org`
* `ssl/app.test.rdmo.org.key` to `/etc/ssl/private/` on `app.test.rdmo.org`

```bash
# as root
update-ca-certificates
```

### Install app

```bash
# as root
apt install build-essential libxml2-dev libxslt-dev zlib1g-dev \
    python3-dev python3-pip python3-venv \
    git pandoc texlive texlive-xetex \
    apache2 libapache2-mod-wsgi-py3

adduser rdmo --home /srv/rdmo

# as rdmo
git clone https://github.com/rdmorganiser/rdmo-app
cd rdmo-app
python3 -m venv env
echo "source ~/rdmo-app/env/bin/activate" >> ~/.bashrc
. ~/.bashrc

pip install --upgrade pip setuptools
pip install rdmo

cp config/settings/sample.local.py config/settings/local.py
# edit config/settings/local.py

./manage.py migrate
./manage.py download_vendor_files
./manage.py collectstatic
```

Copy `apache2/rdmo.conf` to `/etc/apache2/sites-available/000-default.conf` on `app.test.rdmo.org`.

```bash
# as root
a2enmod ssl
systemctl restart apache2
```
