all: ca ldap app idp idp2 sp sp2

ldap: ldap.test.rdmo.org.key ldap.test.rdmo.org.crt

app: app.test.rdmo.org.key app.test.rdmo.org.crt

idp: idp.test.rdmo.org.key idp.test.rdmo.org.crt

idp2: idp2.test.rdmo.org.key idp2.test.rdmo.org.crt

sp: sp.test.rdmo.org.key sp.test.rdmo.org.crt

sp2: sp2.test.rdmo.org.key sp2.test.rdmo.org.crt

ca:
	mkdir ca && \
	touch ca/index.txt ca/index.txt.attr && \
	echo 01 > ca/serial.txt && \
	openssl req -config ca.cnf -newkey rsa:4096 -sha512 -x509 -extensions v3_ca \
	    -keyout ca/test.rdmo.org.key -out ca/test.rdmo.org.crt -days 1095

%.key:
	openssl genrsa -out $@ 4096

%.csr: %.key
	openssl req -config $*.cnf -new -key $< -out $@

%.crt: %.csr
	openssl ca -config ca.cnf -policy signing_policy -extensions signing_req -out $@ -infiles $<

clean:
	rm -rf ca *.key *.csr *.crt

.PHONY: clean
