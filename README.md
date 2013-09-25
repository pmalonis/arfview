Arfview
========

Arfview is a data visualization program for use with data in the [arf](https://github.com/dmeliza/arf/) format.

Installation (Linux and OS X)
------------
  * Install [Anaconda](https://store.continuum.io/cshop/anaconda/).
  * In a new terminal window, install arfview:

        git clone https://github.com/kylerbrown/arfview.git
        cd arfview
        python setup.py install

To have audio playback, install [sox](http://sox.sourceforge.net/)

You may also need build dependencies for PySide and HDF5. In Ubuntu/Debian:

    sudo apt-get build-dep python-pyside python-h5py

Starting arfview:
-----------------

    arfview.py

