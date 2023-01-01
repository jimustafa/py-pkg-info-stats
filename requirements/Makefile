.PHONY: default
default: help

.PHONY: help
help:
	@echo
	@echo "Project Requirements"
	@echo "===================="
	@echo
	@echo "all"
	@echo "  compile all requirements files"
	@echo "install"
	@echo "  install all requirements"
	@echo

.PHONY: all
all: requirements.txt dev-requirements.txt ../binder/requirements.txt

.PHONY: install
install: requirements.txt dev-requirements.txt
	pip-sync $^

dev-requirements.txt: dev-requirements.in requirements.txt
	pip-compile $<

../binder/requirements.txt: requirements.in requirements.txt
	cat requirements.in | awk -F"[<=>~!]" '{print $$1}' | xargs -I{} sed -n '/^{}==/p' requirements.txt > $@

%.txt: %.in
	pip-compile $<
