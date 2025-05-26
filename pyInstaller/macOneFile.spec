# -*- mode: python -*-

# Run with `pyinstaller --windowed --onedir`

block_cipher = None

a = Analysis(['../main.py'],
             pathex=['../'],
             binaries=[],
             datas=[( '../resources/*', './resources' )], # Move these to the `MacOS` directory, or the app can't find them
             hiddenimports=['pywt._extensions._cwt'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False,
             target_arch=['x86_64', 'arm64'])
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='RMTS',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False)
coll = COLLECT(exe,
              a.binaries,
              a.zipfiles,
              a.datas,
              strip=False,
              upx=True,
              name='RMTS')
app = BUNDLE(coll,
             name='RMTS.app',
             icon='../resources/icon.icns',
             version='0.4.0',
             info_plist={
              'NSHighResolutionCapable': True,
             },
             bundle_identifier=None)
