# BAT launcher behavior

`run_scanner.bat` now performs a full Python check before launch.

It does not overwrite an old Python installation.
If Python is missing or too old, it installs Python 3.12 side-by-side using winget, then launches the scanner.
