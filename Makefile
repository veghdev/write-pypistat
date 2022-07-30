.PHONY: clean \
	clean-dev update-dev-req install-dev-req install touch-dev \
	check format check-format lint check-typing \
	clean-doc doc \
	clean-build build-release check-release release

VIRTUAL_ENV = .venv

DEV_BUILD_FLAG = $(VIRTUAL_ENV)/DEV_BUILD_FLAG



clean: clean-dev clean-doc clean-build



# init

clean-dev:
	rm -rf $(VIRTUAL_ENV)

update-dev-req: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/pip-compile --upgrade dev-requirements.in

install-dev-req:
	python3 -m venv $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python -m pip install --upgrade pip
	$(VIRTUAL_ENV)/bin/pip install -r dev-requirements.txt

install:
	$(VIRTUAL_ENV)/bin/python setup.py install

touch-dev:
	touch $(DEV_BUILD_FLAG)

dev: $(DEV_BUILD_FLAG)

$(DEV_BUILD_FLAG):
	$(MAKE) -f Makefile install-dev-req
	$(MAKE) -f Makefile install
	$(MAKE) -f Makefile touch-dev



# ci

check: check-format lint check-typing

format: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/black src setup.py

check-format: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/black --check src setup.py

lint: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/pylint src setup.py

check-typing: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/mypy src setup.py



# doc

clean-doc:
	rm -rf docs

doc: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/pdoc --docformat google src/writepypistat -o docs



# release

clean-build:
	rm -rf build
	rm -rf dist
	rm -rf `find . -name '*.egg-info'`
	rm -rf `find . -name '__pycache__'`

build-release: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/python -m build

check-release: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/python -m twine check dist/*.tar.gz dist/*.whl

release: clean-build build-release check-release