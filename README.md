![splash](Source/splash.png)

This is the EPL-maintained version of the program originally written by Brad Buran.

[Help](https://EPL-Engineering.github.io/abr-peak-analysis/)

[Changelog](CHANGELOG.md)

Minimal Python environment:

```
conda create -n abr -c conda-forge python=3.9.12 nomkl scipy matplotlib wxPython numpy==2.0.2 spyder pyinstaller
conda activate abr

# then clone this repo
git clone https://github.com/tlambert03/abr-peak-analysis.git
cd abr-peak-analysis
python Source/notebook.py
```

Notes: numpy v2.0.1 has bugs that break bundled apps without a console, e.g.:
```
  File "numpy\f2py\cfuncs.py", line 19, in <module>
    errmess = sys.stderr.write
AttributeError: 'NoneType' object has no attribute 'write'
```

See [here](https://github.com/numpy/numpy/issues/26862)
