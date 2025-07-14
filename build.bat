@echo off
pyinstaller -y ^
  --onefile ^
  --windowed ^
  --name FileSplitter ^
  --icon=icon.ico ^
  --add-data "icon.ico;." ^
  main.py
pause