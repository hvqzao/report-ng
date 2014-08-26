@rem --clean --strip --onedir
pyinstaller --noconfirm --onefile --windowed --icon src/resources/icon.ico --distpath build --specpath build --workpath build/tmp wasar.py
