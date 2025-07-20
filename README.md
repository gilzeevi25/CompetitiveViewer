# CompetitiveViewer


## Packing to EXE

```bash
pip install pyinstaller
python make_exe.py
dist/NervioViz/NervioViz.exe
```
The build script collects all required pandas and numpy binaries and
uses a runtime hook that appends their ``*.libs`` directories to ``PATH``.
This ensures that libraries bundled with these packages can be located,
preventing ``ImportError: DLL load failed`` when launching the packaged
application.
Existing ``dist/NervioViz`` contents are removed automatically so repeated
builds do not require manual cleanup.

## Development

### Tests
```bash
pytest
```

CI

GitHub Actions badge shows lint + test status on every push.
