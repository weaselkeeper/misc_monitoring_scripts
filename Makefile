# Makefile is a confused mess.  Needs significant cleanup
NAME = check_unmonitored
VERSION=0.1
RELEASE=0
SHELL := /bin/bash
SPECFILE = $(firstword $(wildcard *.spec))
WORKDIR := $(shell pwd)/work
SRCRPMDIR ?= $(shell pwd)
SPECFILE = packaging/rpm/${NAME}.spec

DEBFULLNAME=Jim Richardson
DEBEMAIL=weaselkeeper@gmail.com
SOURCE_URL=https://github.com/weaselkeeper/$(NAME).git
BASEDIR := $(shell git rev-parse --show-toplevel)

BUILDDIR ?= $(WORKDIR)
RPMDIR ?= $(shell pwd)
SOURCEDIR := $(shell pwd)
TAR := /bin/tar
RPM_DEFINES := --define "_sourcedir $(SOURCEDIR)" \
		--define "_builddir $(BUILDDIR)" \
		--define "_srcrpmdir $(SRCRPMDIR)" \
		--define "_rpmdir $(RPMDIR)" \

VER_REL := $(shell rpm $(RPM_DEFINES) -q --qf "%{VERSION} %{RELEASE}\n" --specfile $(SPECFILE)| head -1)

ifndef VERSION
	VERSION := $(word 1, $(VER_REL))
endif
ifndef RELEASE
	RELEASE := $(word 2, $(VER_REL))
endif
ifndef RPM
	RPM := rpmbuild
endif
ifndef RPM_WITH_DIRS
	RPM_WITH_DIRS = $(RPM) $(RPM_DEFINES)
endif

TARSRC = $(NAME)-$(VERSION)

#TODO: this should probably be a tag rather than just the latest commit.
TAG             := $(shell git log ./ | head -1 | sed 's/commit //')

###########
## Some setup

authors:
	sh packaging/authors.sh

common: authors



# Build targets

# Debian related.
deb: common
	cd $(BASEDIR) && mkdir -p BUILD_TEMP/debian && echo 'setting up temp build env'
	cd BUILD_TEMP/debian

# Redhat related
build-srpm:
	$(RPM) -bs $(RPM_DEFINES) $(SPECFILE)

build-rpm:
	$(RPM) -bb $(RPM_DEFINES) $(SPECFILE)

all: srpm

sources:
	mkdir $(NAME)
	cp -r src/* $(NAME)
	cp -r conf/* $(NAME)
	mkdir -p $(SOURCEDIR)
	mkdir -p $(WORKDIR)
	/bin/tar -jcf $(SOURCEDIR)/$(TARSRC).tar.bz2 $(NAME)

srpm: sources build-srpm

rpm: sources build-rpm


# Cleanup
clean:
	@echo "cleaning up "
	@/bin/rm -rf $(WORKDIR) building $(NAME)
	@cd $(BASEDIR) && rm -rf BUILD_TEMP && rm -f AUTHORS.TXT $(NAME)-$(VERSION)*.tar.bz2
	@find $(BASEDIR) -iname *.py[co] | xargs -i rm -f {}
	@rm -rf noarch
	@rm -f $(NAME)*rpm

bleach: clean
	@/bin/rm -f $(NAME)-$(VERSION)*rpm*

# Usage
help:
	@echo 'Makefile for $(NAME), currently supports deb and rpm '
	@echo ' builds from current source tree.'
	@echo "Usage: make <target>"
	@echo "Available targets are:"
	@echo "	sources			Create tarball"
	@echo "	srpm			Create srpm"
	@echo "	rpm			Create rpm"
	@echo "	clean			Remove work dir"

