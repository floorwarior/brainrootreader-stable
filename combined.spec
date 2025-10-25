# -*- mode: python ; coding: utf-8 -*-


brainrootreader = Analysis(
    ['background.py'],
    pathex=[],
    binaries=[],
    datas=[("templates","templates"),(".venv/Lib/site-packages/language_data/data","language_data/data"),
    (".venv/Lib/site-packages/language_tags/data","language_tags/data"),
    (".venv/Lib/site-packages/misaki","misaki"),("brainrootreadericon.ico","."),
    (".venv/Lib/site-packages/kokoro","kokoro"),
    (".venv/Lib/site-packages/spacy","spacy"),
    (".venv/Lib/site-packages/spacy_curated_transformers","spacy_curated_transformers"),
    (".venv/Lib/site-packages/spacy_legacy","spacy_legacy"),
    (".venv/Lib/site-packages/spacy_loggers","spacy_loggers"),
    (".venv/Lib/site-packages/espeakng_loader","espeakng_loader"),
    ("loadingwindow.py","."),("README.md","."),("LICENSE.txt","."),
    ("static","static"),("pipermodels","pipermodels"),
    ("helpers","helpers"),
    ("uploads","uploads"),
    ("booklist.json","."),("readerconfigs","readerconfigs"),
    ("plusreaders","plusreaders"),("appconfig.json","."),
    (".venv/Lib/site-packages/en_core_web_sm","en_core_web_sm"),
    ("kokoromodels","kokoromodels"),("__version__.py","__version__.py")],
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
    console=False,
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


loadingwindow = Analysis(
    ['loadingwindow.py'],
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

loadingwindow_pyz = PYZ(loadingwindow.pure)

loadingwindow_exe = EXE(
    loadingwindow_pyz,
    loadingwindow.scripts,
    [],
    exclude_binaries=True,
    name='loadingwindow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)



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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    readercore_exe,
    loadingwindow_exe,
    brainrootreader_exe,
    loadingwindow.binaries,
    readercore.binaries,
    brainrootreader.binaries,
    readercore.datas,
    brainrootreader.datas,
    loadingwindow.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='brainrootreader',
)
