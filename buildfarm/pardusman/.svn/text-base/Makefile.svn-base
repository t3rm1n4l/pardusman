all:
	pykde4uic -o gui/ui/main.py gui/ui/main.ui
	pykde4uic -o gui/ui/languages.py gui/ui/languages.ui
	pykde4uic -o gui/ui/packages.py gui/ui/packages.ui

clean:
	find -name *.pyc | xargs rm -rf
	rm -rf gui/ui/main.py
	rm -rf gui/ui/languages.py
	rm -rf gui/ui/packages.py
