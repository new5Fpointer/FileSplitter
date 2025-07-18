python -m nuitka --standalone --onefile --windows-icon-from-ico=icon.ico ^
  --include-package=tkinterdnd2 ^
  --include-package=chardet ^
  --enable-plugin=tk-inter ^
  --msvc=latest ^
  --windows-console-mode=disable ^
  --include-data-files=icon.ico=icon.ico ^
  --output-dir=dist ^
  --output-filename=FileSplitter.exe ^
  main.py
pause