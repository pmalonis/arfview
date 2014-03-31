Arfview
========

Arfview is a data visualization program for use with data in the [arf](https://github.com/dmeliza/arf/) format.

![](http://i60.tinypic.com/206xyqc.png)


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

    arfview

    
Plot Checked Mode:
------------------

To plot multiple datasets across entries or files, click the "plot checked mode" button in the toolbar. Then check the datasets you want to plot, and click "Refresh Data View."  To select data based on attributes, select "Check Multiple" in the Tree toolbar.  Later versions will include the capability for more complex queries. 

Labeling:
--------
To add a label to an existing label dataset, hold down a letter key and click on the plot.  A simple label with the name of the key pressed will be added to the plot at the point in time pressed.  To label an interval, hold down shift and the letter key, click on the plot at the start time of the label, and then click again at the stop time.  

To add a label dataset, select the entry in which you want the label to be added, add press the "Add label" button on the main toolbar. 

Exporting data:
--------------

The "Export Data" tool allows you to export a selected dataset as a .wav or .csv file.




