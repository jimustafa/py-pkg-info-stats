SOURCES := $(wildcard ./src/*.py)
NOTEBOOKS := $(patsubst ./src/%.py,./build/%.ipynb,$(SOURCES))


.PHONY: default
default: help

.PHONY: help
help:
	@echo
	@echo "Python PKG-INFO Stats"
	@echo "====================="
	@echo
	@echo "Build"
	@echo "-----"
	@echo "install-requirements"
	@echo "  install the requirements in the current Python environment"
	@echo "data"
	@echo "  generate PKG-INFO table"
	@echo "notebooks"
	@echo "  build the notebooks"
	@echo
	@echo "Development"
	@echo "-----------"
	@echo "start-dev"
	@echo "  watch Python source files and convert to IPython notebooks"
	@echo "  run Voila server"
	@echo "stop-dev"
	@echo "  terminate the background processes initiated by \`start-dev\`"
	@echo

.PHONY: install-requirements
install-requirements:
	$(MAKE) -C ./requirements/ install

.PHONY: all
all: notebooks data

.PHONY: notebooks
notebooks: $(NOTEBOOKS)

.PHONY: data
data: ./data/table.csv | ./build
	cp ./data/table.csv ./build/

./data/table.csv: generate-data.py
	mkdir -p ./data/json
	python generate-data.py

.PHONY: check
check: notebooks
	pytest --nbmake ./build/

.PHONY: start-dev
start-dev: stop-dev notebooks data
	watchmedo shell-command ./src/ --patterns="*.py" --command='make notebooks' \
	  & echo "$$!" >> watchmedo.pid
	voila --debug ./build/ \
	  & echo "$$!" >> voila.pid

.PHONY: stop-dev
stop-dev:
	- pkill -F watchmedo.pid
	- pkill -F voila.pid
	- rm watchmedo.pid
	- rm voila.pid

.PHONY: clean
clean:
	- rm -rf ./build/*

.PHONY: clean-all
clean-all: clean
	- rm -rf ./data/*

./build:
	mkdir -p ./build

./build/%.ipynb: ./src/%.py | ./build
	jupytext --from py:percent --to notebook --output $@ $<
