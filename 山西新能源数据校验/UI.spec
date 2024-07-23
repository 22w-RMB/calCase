# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['UI.py','common.py','excel_handler.py','test.py'],
    pathex=["D:\\code\\python\\calCase\\山西新能源数据校验"],
    binaries=[],
    datas=[(".\\config\\*.yaml","山西新能源数据校验\\config"),(".\\导出\\导出模板.xlsx","山西新能源数据校验\\导出")],
    hiddenimports=[],
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
    name='执行程序',
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
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='执行程序',
)
