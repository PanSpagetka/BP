all: initApp cases pcap_filter initDB

apache_user = www-data

initApp:
	python init.py

cases:
	mkdir cases
	chown $(apache_user) -R cases
	chmod 774 cases

init:
	python init.py

pcap_filter:
	$(MAKE) -C PCAPtools


initDB:
	mkdir DB
	chmod 755 DB
	python initDB.py
	chmod 644 DB/test.sql
	chown -R $(apache_user) DB

clean:
	rm -r cases
	rm -r DB
	rm -f PCAPtools/pcap_filter
