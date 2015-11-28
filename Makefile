all: init

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
	rmdir cases
