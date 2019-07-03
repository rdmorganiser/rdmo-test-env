# RDMO test environment

This repository contains documentation and config files to set up a test enviroment for RDMO. In particular services for LDAP and Shibboleth authentication.

*Important:* These instructions are not meant for a production system. We will use a weak passwords and a non save workflow for certificate signing.

Currently, the setup consists of virtual machines, with no automatic setup, but this might change (i.e. using ansible, docker, vagrant).


## Certificate authority

In a first step we setup a private CA to sign valid certificate (for our test setup). See `ssl/Makefile` and `ssl/ca.cnf` for the fun part.

```
cd ssl
make
```

Answer all questions correctly. This is the first test...

Import `ssl/ca/test.rdmo.org.crt` into your browser.


## bionic

This is the master VM from which all other VM are cloned.

HD: 20 Gb
Network: Bridged
Image: ubuntu-18.04.2-live-server-amd64.iso

Install with standard options.
After Install set `preserve_hostname: true` in `/etc/cloud/cloud.cfg`


## rdmo-ldap

This is the VM for the LDAP holding the user accounts.

Clone `bionic` VM.

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
ldapsearch -v -x -D "uid=rdmo,dc=ldap,dc=test,dc=rdmo,dc=org" -w rdmo -b "dc=ldap,dc=test,dc=rdmo,dc=org" -s sub 'uid=user'
ldapsearch -v -x -D "uid=rdmo,dc=ldap,dc=test,dc=rdmo,dc=org" -w rdmo -b "dc=ldap,dc=test,dc=rdmo,dc=org" -s sub 'objectClass=groupOfNames'
```

Check if ldap works:

```
apt install ldap-utils
ldapsearch -v -x -ZZ -H ldap://ldap.test.rdmo.org \
    -D "uid=idp,dc=ldap,dc=test,dc=rdmo,dc=org" -w idp \
    -b "dc=ldap,dc=test,dc=rdmo,dc=org" -s sub 'uid=user'
```

## rdmo-app

This is the VM to be user with the LDAP directly.

Clone `bionic` VM.

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
```

Copy `rdmo/app.local.py` to `/srv/rdmo/rdmo-app/config/settings` on `sp.test.rdmo.org`.

```bash
# as rdmo
./manage.py check
./manage.py migrate
./manage.py download_vendor_files
./manage.py collectstatic
```
```

### Deploy with Apache

```bash
# as root
apt install apache2 libapache2-mod-wsgi-py3
```

Copy `apache2/app.conf` to `/etc/apache2/sites-available/000-default.conf` on `app.test.rdmo.org`.

```bash
# as root
a2enmod ssl rewrite
systemctl restart apache2
```


## rdmo-idp

This is the VM acting as identity provider for Shibboleth.

Clone `bionic` VM.

Copy:

* `ssl/ca/test.rdmo.org.crt` to `/usr/local/share/ca-certificates/` on `idp.test.rdmo.org`
* `ssl/idp.test.rdmo.org.crt` to `/etc/ssl/certs/` on `idp.test.rdmo.org`
* `ssl/idp.test.rdmo.org.key` to `/etc/ssl/private/` on `idp.test.rdmo.org`

```bash
# as root
hostnamectl set-hostname idp.test.rdmo.org
update-ca-certificates
reboot
```

```bash
chgrp ssl-cert /etc/ssl/private
chgrp ssl-cert /etc/ssl/private/idp.test.rdmo.org.key
chmod 750 /etc/ssl/private/
chmod 640 /etc/ssl/private/idp.test.rdmo.org.key
```

Check if ldap works:

```
apt install ldap-utils
ldapsearch -v -x -ZZ -H ldap://ldap.test.rdmo.org \
    -D "uid=idp,dc=ldap,dc=test,dc=rdmo,dc=org" -w idp \
    -b "dc=ldap,dc=test,dc=rdmo,dc=org" -s sub 'uid=user'
```

### Install IdP

Install Java dependencies:

```
apt install openjdk-8-jdk
echo "JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> /etc/environment
```

Then log out and log in.

Get Shibboleth from https://shibboleth.net/downloads/identity-provider/latest/. We will use https://shibboleth.net/downloads/identity-provider/latest/shibboleth-identity-provider-3.4.4.tar.gz.

```
# as root
cd /opt
wget https://shibboleth.net/downloads/identity-provider/latest/shibboleth-identity-provider-3.4.4.tar.gz
tar xzvf shibboleth-identity-provider-3.4.4.tar.gz
cd shibboleth-identity-provider-3.4.4/bin
./install.sh
```

Accept default values and enter new passwords.

Update `validUntil` in `/opt/shibboleth-idp/metadata/idp-metadata.xml` to something in the future.


### Deploy IdP with tomcat

```bash
ap install apache2 tomcat8 tomcat8-admin
usermod -aG ssl-cert tomcat8
```

In /etc/tomcat7/server.xml uncomment:

```
    <Connector
           protocol="org.apache.coyote.http11.Http11AprProtocol"
           port="8443" maxThreads="200"
           scheme="https" secure="true" SSLEnabled="true"
           SSLCertificateFile="/etc/ssl/certs/idp.test.rdmo.org.crt"
           SSLCertificateKeyFile="/etc/ssl/private/idp.test.rdmo.org.key"
           SSLVerifyClient="optional" SSLProtocol="TLSv1+TLSv1.1+TLSv1.2"/>

    <Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />
```

Add a admin user for tomcat. In `/etc/tomcat8/tomcat-users.xml` add:

```
<user username="tomcat" password="tomcat" roles="manager-gui, admin-gui"/>
```

Download `jstl-1.2.jar` from https://mvnrepository.com/artifact/javax.servlet/jstl/1.2 and move it to `/var/lib/tomcat8/lib/` (this prevents a `NestedServletException` later).

Restart tomcat:

```bash
systemctl restart tomcat8
```

http://idp.test.rdmo.org:8080 and http://idp.test.rdmo.org:8443 should work now.

For debugging, you want to look at `/var/log/tomcat8/catalina.out`.

Change the permissions for `/opt/shibboleth-idp`:

```
chown -R tomcat8:tomcat8 /opt/shibboleth-idp
```

Go to http://idp.test.rdmo.org:8080/manager and add to "Deploy directory or WAR file located on server"::

```
Context Path (required): /idp
XML Configuration file URL:
WAR or Directory URL: /opt/shibboleth-idp/war/idp.war
```

Start the container. http://idp.test.rdmo.org:8080/idp/ should show a page now.


### Configure IdP

Copy:

* `idp/access-control.xml` (really insecure, *do not use in production*)
* `idp/attribute-resolver.xml`
* `idp/attribute-filter.xml`
* `idp/ldap.properties`

to `/opt/shibboleth-idp/conf/` on `idp.test.rdmo.org`.

Restart tomcat:

```
systemctl restart tomcat8
```

### Proxy IdP with apache

Copy `apache2/idp.conf` to `/etc/apache2/sites-available/000-default.conf` on `idp.test.rdmo.org`.

```
a2enmod ssl rewrite proxy_ajp
systemctl restart apache2
```

Go to:

* https://idp.test.rdmo.org/idp/shibboleth
* https://idp.test.rdmo.org/idp/profile/admin/resolvertest?requester=https%3A%2F%2Fsp.test.rdmo.org%2Fshibboleth&principal=test


## rdmo-sp

This is the VM with the service provider and the rdmo instance using Shibboleth.

Clone `bionic` VM.

```bash
hostnamectl set-hostname sp.test.rdmo.org
reboot
```

Copy:

* `ssl/ca/test.rdmo.org.crt` to `/usr/local/share/ca-certificates/` on `sp.test.rdmo.org`
* `ssl/sp.test.rdmo.org.crt` to `/etc/ssl/certs/` on `sp.test.rdmo.org`
* `ssl/sp.test.rdmo.org.key` to `/etc/ssl/private/` on `sp.test.rdmo.org`

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
pip install -r requirements/shibboleth.txt
```

Copy `rdmo/sp.local.py` to `/srv/rdmo/rdmo-app/config/settings` on `sp.test.rdmo.org`.

```bash
# as rdmo
./manage.py check
./manage.py migrate
./manage.py download_vendor_files
./manage.py collectstatic
```

### Install service provider

Get the package from https://www.switch.ch/aai/guides/sp/installation/?os=ubuntu (the Ubuntu package is broken).

```bash
cd /opt
curl --fail --remote-name https://pkg.switch.ch/switchaai/ubuntu/dists/bionic/main/binary-all/misc/switchaai-apt-source_1.0.0ubuntu1_all.deb
apt install /opt/switchaai-apt-source_1.0.0ubuntu1_all.deb
apt update
apt install --install-recommends shibboleth
apt autoremove
```

### Configure service provider

Copy:

* `sp/attribute-map.xml`
* `sp/shibboleth2.xml`

to `/etc/shibboleth` on `sp.test.rdmo.org`.

Fetch IdP Metadata:

```bash
wget https://idp.test.rdmo.org/idp/shibboleth -O /etc/shibboleth/idp-metadata.xml
```

Restart `shibd`:

```bash
systemctl restart shibd
```

### Deploy with Apache

```bash
# as root
apt install apache2 libapache2-mod-wsgi-py3
```

Copy `apache2/sp.conf` to `/etc/apache2/sites-available/000-default.conf` on `ap.test.rdmo.org`.

```bash
# as root
a2enmod ssl rewrite
systemctl restart apache2
```

### Configure metadata on IdP

Log in on `idp.test.rdmo.org`:

Copy `idp/metadata-provider.xml` to `/opt/shibboleth-idp/conf/` on `idp.test.rdmo.org`.

Fetch metadata and restart tomcat:

```bash
wget https://sp.test.rdmo.org/Shibboleth.sso/Metadata -O /opt/shibboleth-idp/metadata/sp-metadata.xml
systemctl restart tomcat8
```

Now it should work, but probably won't.
