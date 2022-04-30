.PHONY: install dev clean check format check-format lint docs

VIRTUAL_ENV = .venv
DEV_BUILD_FLAG = $(VIRTUAL_ENV)/DEV_BUILD_FLAG

install:
	$(VIRTUAL_ENV)/bin/python setup.py install

dev: $(DEV_BUILD_FLAG)

$(DEV_BUILD_FLAG):
	python3 -m venv $(VIRTUAL_ENV)
	$(VIRTUAL_ENV)/bin/python setup.py install
	$(VIRTUAL_ENV)/bin/pip install -r dev-requirements.txt
	touch $(DEV_BUILD_FLAG)

clean:
	-rm -rf $(VIRTUAL_ENV)

requirements:
	pip-compile --upgrade dev-requirements.in

check: check-format lint

format: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/black src

check-format: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/black --check src

lint: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/pylint \
		--disable missing-function-docstring \
		--disable missing-class-docstring \
		--disable missing-module-docstring \
		--disable too-few-public-methods \
		src

docs: $(DEV_BUILD_FLAG)
	$(VIRTUAL_ENV)/bin/pdoc --docformat numpy src/write-pypistat -o docs
