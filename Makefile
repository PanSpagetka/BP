all: init, cases, pcap_filter, initDB

cases:
	mkdir cases

pcap_filter:
	$(MAKE) -C PCAPtools
init:
	python init.py

initDB:
	mkdir DB
	python initDB.py

clean:
	rm -r cases
	rm -r DB
	rm -f pcap_filter
