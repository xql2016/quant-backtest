# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('多策略可视化回测_小红书20260117.py', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'streamlit',
        'pandas',
        'numpy',
        'matplotlib',
        'akshare',
        'yfinance',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.elements.image',
        'streamlit.elements.number_input',
        'streamlit.elements.selectbox',
        'streamlit.elements.text_input',
        'streamlit.elements.slider',
        'streamlit.elements.button',
        'streamlit.elements.write',
        'streamlit.elements.dataframe_utils',
        'streamlit.elements.exception',
        'streamlit.web.cli',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='量化回测工作台',
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
    icon=None,  # 可以添加 icon='icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='量化回测工作台',
)

