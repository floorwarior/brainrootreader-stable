# -*- mode: python ; coding: utf-8 -*-


brainrootreader = Analysis(
    ['background.py'],
    pathex=[],
    binaries=[],
    datas=[("templates","templates"),("brainrootreadericon.ico","."),("loadingwindow.py","."),("README.md","."),("LICENSE.txt","."),("static","static"),("pipermodels","pipermodels"),("helpers","helpers"),("uploads","uploads"),("booklist.json","."),("readerconfigs","readerconfigs"),("plusreaders","plusreaders")],
    hiddenimports=['pypdf','helpers','readerconfigs','plusreaders','pypdf._reader', 'pypdf._writer', 'pypdf._crypt', 'pypdf._page', 'pypdf.generic', 'pypdf.constants','engineio.async_drivers.threading','engineio.async_drivers.eventlet',],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
brainrootreader_pyz = PYZ(brainrootreader.pure)

brainrootreader_exe = EXE(
    brainrootreader_pyz,
    brainrootreader.scripts,
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

readercore= Analysis(
    ['readercore.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
readercore_pyz = PYZ(readercore.pure)

readercore_exe = EXE(
    readercore_pyz,
    readercore.scripts,
    [],
    exclude_binaries=True,
    name='readercore',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    readercore_exe,
    brainrootreader_exe,
    readercore.binaries,
    brainrootreader.binaries,
    readercore.datas,
    brainrootreader.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='brainrootreader',
)
