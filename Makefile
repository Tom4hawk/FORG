# Rudimentary Makefile for the FORG
#
# David Allen <mda@idatar.com>
#
# Running ./forg.py hostname is sufficient to run the program, so don't 
# use make at all unless you know what this does.  :)
#
# $Id: Makefile,v 1.12 2001/07/11 22:45:51 s2mdalle Exp $
###############################################################################

srcdir  = `pwd`
PYTHON  = /usr/bin/python
RM      = /bin/rm -f
CONFDIR = "$(HOME)/.forg"

all:
	$(PYTHON) forg.py gopher.quux.org

clean-cache:
	$(RM) -r $(CONFDIR)/cache/*

clean:	
	@echo Yeeeeeeeeeeeeeehaw\!\!\!\!\!
	$(RM) *.pyc *~

dist:
	cd .. && tar cvf forg-latest.tar $(srcdir) --exclude CVS && \
	gzip -9 forg-latest.tar

install:
	mkdir -v -p $(CONFDIR)
	cp -i $(srcdir)/default_bookmarks.xml $(CONFDIR)/bookmarks
	cp -i $(srcdir)/default_options $(CONFDIR)/options

restore:	clean  clean-cache
	@echo "Done"
