from cx_Freeze import setup, Executable
import glob
import shutil
import subprocess
import os
import sys
# Dependencies are automatically detected, but it might need
# fine tuning.

buildOptions = dict(packages = ['PySide','atexit','numpy','libtfr','arf','arfview',
                                'scipy','sys','os','pyqtgraph','h5py','tempfile', 'signal'],
                    excludes = ["Tkinter", "Tkconstants", "tcl"],
                    copy_dependent_files=True,
                    path=['/Library/Python/2.7/site-packages/h5py']
)

base = 'Win32GUI' if sys.platform=='win32' else None
        

executables = [
    Executable('../arfview/mainwin.py', base=base, targetName='arfview')
]

try:
    setup(name='arfview',
          version = '1.0',
          description = 't',
          options = dict(build_exe = buildOptions),
          executables = executables)

finally:
    pyside_dir = '/home/pmalonis/arfview/freeze/build/exe.linux-x86_64-2.7'
    pyside_so = glob.glob('%s/*.so'%(pyside_dir))
    depend_so = ' '.join([subprocess.check_output('ldd %s'%(so),
                                        shell=True) for so in pyside_so])

    for src in depend_so.split():
        if ('so' in src and src[0]=='/' and so.split('/')[-1]
            not in os.listdir('build/exe.linux-x86_64-2.7')):
            shutil.copy(src, 'build/exe.linux-x86_64-2.7/')
