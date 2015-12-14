all: initApp cases pcap_filter initDB

initApp:
	python init.py

cases:
	mkdir cases
	chmod 777 cases

init:
	python init.py

pcap_filter:
	$(MAKE) -C PCAPtools


initDB:
	mkdir DB
	chmod 777 DB
	python initDB.py
	chmod 666 DB/test.sql

clean:
	rm -r cases
	rm -r DB
	rm -f PCAPtools/pcap_filter
