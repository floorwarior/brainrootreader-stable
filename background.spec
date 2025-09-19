# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['background.py'],
    pathex=[],
    binaries=[],
    datas=[("templates","templates"),("LICENSE.txt","."),(MANUAL.md),("static","static"),("pipermodels","pipermodels"),("helpers","helpers"),("uploads","uploads"),("booklist.json","."),("pdftoplaylist.py","."),("readerconfigs","readerconfigs"),("plusreaders","plusreaders")],
    hiddenimports=['pypdf','helpers','readerconfigs','plusreaders','pypdf._reader', 'pypdf._writer', 'pypdf._crypt', 'pypdf._page', 'pypdf.generic', 'pypdf.constants','engineio.async_drivers.threading','engineio.async_drivers.eventlet',],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='brainrootreader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon = "brainrootreadericon.ico",
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
