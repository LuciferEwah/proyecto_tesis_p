# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
            ['LIACDD.py'],
             binaries=[],
             datas=[],
             hiddenimports=['bcrypt','mlxtend','matplotlib', 'matplotlib.backends', 'matplotlib.backends.backend_svg','matplotlib.backends.backend_pdf'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             noarchive=True)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LIACDD',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version.txt',
    icon=['assets\\images\\icon_machineLearning.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='LIACDD',
)