all: install

install:
	. env/bin/activate; pip install --editable .
