all: install

install:
	source env/bin/activate; pip install --editable .
