from cx_Freeze import setup, Executable 
  
buildOptions = dict(includes =["idna.idnadata"], excludes = ["tkinter", "PyQt4.QtSql", "sqlite3", 
                                  "scipy.lib.lapack.flapack",
                                  "PyQt4.QtNetwork",
                                  "PyQt4.QtScript",
                                  "numpy.core._dotblas", 
                                  "PyQt5"], optimize=1)

setup(name = "CalculatedGG Uploader" , 
      version = "2.0" , 
      description = "" ,
      options = {"build_exe": buildOptions},
      executables = [Executable("CalculatedGGUploader.py")]) 