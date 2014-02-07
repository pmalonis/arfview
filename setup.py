from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import io
import os
import sys

import arfview

# here = os.path.abspath(os.path.dirname(__file__))


# def read(*filenames, **kwargs):
#     encoding = kwargs.get('encoding', 'utf-8')
#     sep = kwargs.get('sep', '\n')
#     buf = []
#     for filename in filenames:
#         with io.open(filename, encoding=encoding) as f:
#             buf.append(f.read())
#     return sep.join(buf)

# long_description = read('README.md', 'CHANGES.md')


# class PyTest(TestCommand):
#     def finalize_options(self):
#         TestCommand.finalize_options(self)
#         self.test_args = []
#         self.test_suite = True

#     def run_tests(self):
#         import pytest
#         errcode = pytest.main(self.test_args)
#         sys.exit(errcode)

setup(
    name='arfview',
    scripts=['arfview.py'],
    #url='http://github.com/kylerbrown/arfview/',
    license='MIT License',
    author='Kyler Brown',
    #tests_require=['pytest'],
    # install_requires=['pyqtgraph>=0.9.7',
    #                   'lbl>=0.1.1',
    #                   'PySide',
    #                   'matplotlib',
    #                   'h5py',
    #                   'scipy',
    #                   'numpy'
    #                   ],
    #cmdclass={'test': PyTest},
    author_email='kylerjbrown@gmail.com',
    description='a data visualization program for arf files',
    # long_description=long_description,
    packages=['arfview'],
    # include_package_data=True,
    platforms='any',
    #test_suite='arfview.test.test_arfview',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        ],
    #extras_require={
    #    'testing': ['pytest'],
    #}
)
