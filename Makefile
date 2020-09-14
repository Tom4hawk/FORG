# Rudimentary Makefile for the FORG
#
# Copyright (C) 2001 David Allen <mda@idatar.com>
# Copyright (C) 2020 Tom4hawk
#
# Running ./forg.py hostname is sufficient to run the program, so don't 
# use make at all unless you know what this does.  :)
###############################################################################

srcdir  = $(shell pwd)
PYTHON  = /usr/bin/python3
RM      = /bin/rm -rf
CONFDIR = "$(HOME)/.config/forg"
CACHEDIR= "$(HOME)/.cache/forg"

all:
	$(PYTHON) forg.py gopher.quux.org

clean-cache:
	$(RM) -r $(CACHEDIR)/*

clean:	
	@echo Yeeeeeeeeeeeeeehaw\!\!\!\!\!
	find . -name \*.pyc -delete
	find . -name \*.~ -delete
	find . -type d -name \__pycache__ -delete

dist:
	tar zcvf ../forg-latest.tar.gz --exclude='.*' --exclude='__pycache__' --exclude='*.pyc' -C $(srcdir) *

install:
	mkdir -v -p $(CONFDIR)
	cp -i $(srcdir)/default_bookmarks.xml $(CONFDIR)/bookmarks
	cp -i $(srcdir)/default_options $(CONFDIR)/options

restore:	clean  clean-cache
	@echo "Done"
