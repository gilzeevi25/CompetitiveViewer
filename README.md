# CompetitiveViewer


## Packing to EXE

```bash
pip install pyinstaller
python make_exe.py
dist/NervioViz/NervioViz.exe
```
The build script collects all required pandas and numpy binaries to avoid
``ImportError: DLL load failed`` errors when launching the packaged
application.

## Development

### Tests
```bash
pytest
```

CI

GitHub Actions badge shows lint + test status on every push.
