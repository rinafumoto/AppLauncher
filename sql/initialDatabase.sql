BEGIN TRANSACTION;

DROP TABLE IF EXISTS App_old;
DROP TABLE IF EXISTS Env_old;

ALTER TABLE App RENAME TO App_old;
ALTER TABLE Env RENAME TO Env_old;

CREATE TABLE 'App' (
    'Name' TEXT NOT NULL,
    'Path' TEXT NOT NULL,
    'Description' TEXT,
    'Icon' BLOB,
    'Command' TEXT,
    'Argument' TEXT,
    'AppID' INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE 'Env' (
    'Name' TEXT NOT NULL,
    'Value' TEXT NOT NULL,
    'ExeOrder' INTEGER NOT NULL,
    'EnvID' INTEGER PRIMARY KEY AUTOINCREMENT,
    'AppID' INTEGER NOT NULL
);

INSERT INTO App (Name, Path, Description, Icon, Command, Argument, AppID) VALUES
('Blender', '/public/devel/2021/fossdcc/blender-2.93.4-linux-x64/blender', 'Blender Description', '', '', '', 1),
('Visual Studio Code', '/opt/code/bin/code', 'Visual Studio Code Description', 'unset QT_PLUGIN_PATH', '', '', 2),
('DJV', '/public/devel/2021/fossdcc/DJV/bin/djv', 'DJV Description', '', '', '', 3),
('Gaffer', '/public/devel/2021/fossdcc/gafferpy3/bin/gaffer', 'Gaffer Description', '', '', '', 4),
('Gaffer Python2', '/public/devel/2021/fossdcc/gafferpy2/bin/gaffer', 'Gaffer Python2 Description', '', '', '', 5),
('Houdini 18', 'houdini', 'Houdini 18 Description', '', 'export HOUDINI_VERSION=hfs18.5.596
unset QT_PLUGIN_PATH
cd /opt/"$HOUDINI_VERSION"
source houdini_setup_bash', '', 6),
('Houdini 19', 'houdini', 'Houdini 19 Description', '', 'export HOUDINI_VERSION=hfs19.0.455
unset QT_PLUGIN_PATH
cd /opt/"$HOUDINI_VERSION"
source houdini_setup_bash', '', 7),
('Inkscape', '/public/devel/2021/fossdcc/Inkscape.AppImage', 'Inkscape Description', '', '', '', 8),
('Katana', '/opt/Katana4.0v4/katana', 'Katana Description', '', 'unset QT_PLUGIN_PATH', '', 9),
('Krita', '/public/devel/2021/fossdcc/krita.appimage', 'Krita Description', '', '', '', 10),
('Mari', '/opt/Mari4.7v3/mari', 'Mari Description', '', 'unset QT_PLUGIN_PATH
export DATE=`date +.%s`
mkdir -p /tmp/mari.cache."$USERNAME""$DATE"', '', 11),
('Maya', '"$MAYA_LOCATION"/bin/maya', 'Maya Description', '', 'unset QT_PLUGIN_PATH', '', 12),
('Meshroom', '/public/devel/2021/fossdcc/Meshroom/Meshroom', 'Meshroom Description', '', '', '', 13),
('Motion Builder 2020', '/opt/autodesk/MotionBuilder2020/bin/linux_64/motionbuilder', 'Motion Builder 2020 Description', '', 'unset QT_PLUGIN_PATH', '', 14),
('Mr Viewer', '/public/devel/2021/fossdcc/mrViewer/bin/mrViewer.sh', 'Mr Viewer Description', '', '', '', 15),
('Mudbox', '/opt/autodesk/mudbox/bin/mudbox', 'Mudbox Description', '', 'unset QT_PLUGIN_PATH', '', 16),
('Natron', '/public/devel/2021/fossdcc/Natron/Natron', 'Natron Description', '', 'unset PYTHONPATH', '', 17),
('Nuke', '/opt/Nuke13.0v2/Nuke13.0', 'Nuke Description', '', 'unset QT_PLUGIN_PATH', '--nukex', 18),
('Pensil 2D', '/public/devel/2021/fossdcc/pencil2d.AppImage', 'Pensil 2D Description', '', '', '', 19),
('Pftrack', '/usr/bin/pftrack', 'Pftrack Description', '', '', '', 20),
('PureRef', '/public/devel/2021/fossdcc/PureRef-1.11.1_x64.Appimage', 'PureRef Description', '', '', '', 21),
('Pycharm', '/public/devel/2021/pycharm-community/bin/pycharm.sh', 'Pycharm Description', '', '', '', 22),
('Qube', '/usr/bin/python', 'Qube Description', '', 'unset QT_PLUGIN_PATH', '/usr/local/pfx/qube/api/python/qb/gui/qube.py', 23),
('Quixel Bridge', '/public/devel/2021/fossdcc/Bridge.AppImage', 'Quixel Bridge Description', '', '', '', 24),
('Rawtherapee', '/opt/rawtherapee/RawTherapee_5.8.AppImage', 'Rawtherapee Description', '', '', '', 25),
('Storyboarder', '/public/devel/2021/fossdcc/Storyboarder.AppImage', 'Storyboarder Description', '', '', '-no-sandbox', 26),
('Synfig Studio', '/public/devel/2021/fossdcc/SynfigStudio.appimage', 'Synfig Studio Description', '', '', '', 27),
('Texture Lab', '/public/devel/2021/fossdcc/TextureLab/texturelab', 'Texture Lab Description', '', '', '--no-sandbox', 28),
('Toonz', '/public/devel/2021/fossdcc/OpenToonz.appimage', 'Toonz Description', '', '', '', 29),
('Ultimaker Cura', '/public/devel/2021/fossdcc/Ultimaker_Cura.AppImage', 'Ultimaker Cura Description', '', '', '', 30);

INSERT INTO Env (Name, Value, AppID, ExeOrder) VALUES
('LD_LIBRARY_PATH', '/public/devel/2021/fossdcc/DJV/lib', 3, 1),
('RENDERMAN_VERSION', 'RenderManProServer-24.1', 6, 1),
('PYTHONPATH', '', 6, 2),
('SESI_LMHOST', 'hamworthy.bournemouth.ac.uk', 6, 3),
('RMANTREE', '/opt/pixar/"$RENDERMAN_VERSION"', 6, 4),
('PATH', '/opt/pixar/"$RENDERMAN_VERSION"/bin:"$PATH":.', 6, 5),
('PYTHONPATH', '/opt/"$HOUDINI_VERSION"/python/lib/python2.7/site-packages:/opt/"$HOUDINI_VERSION"/python/lib/python2.7/site-packages/pxr:"$PYTHONPATH"', 6, 6),
('LD_LIBRARY_PATH', '"$LD_LIBRARY_PATH":/opt/rh/python27/root/usr/lib64', 6, 7),
('HOUDINI_TEMP_DIR', '/transfer/houdini_temp', 6, 8),
('RENDERMAN_VERSION', 'RenderManProServer-24.1', 7, 1),
('PYTHONPATH', '', 7, 2),
('SESI_LMHOST', 'hamworthy.bournemouth.ac.uk', 7, 3),
('RMANTREE', '/opt/pixar/"$RENDERMAN_VERSION"', 7, 4),
('PATH', '/opt/pixar/"$RENDERMAN_VERSION"/bin:"$PATH":.', 7, 5),
('PYTHONPATH', '/opt/"$HOUDINI_VERSION"/python/lib/python2.7/site-packages:/opt/"$HOUDINI_VERSION"/python/lib/python2.7/site-packages/pxr:"$PYTHONPATH"', 7, 6),
('LD_LIBRARY_PATH', '"$LD_LIBRARY_PATH":/opt/rh/python27/root/usr/lib64', 7, 7),
('HOUDINI_TEMP_DIR', '/transfer/houdini_temp', 7, 8),
('RMANTREE', '/opt/pixar/RenderManProServer-24.1/', 9, 1),
('foundry_LICENSE', '4101@beijing.bournemouth.ac.uk', 9, 2),
('DEFAULT_RENDERER', 'prman', 9, 3),
('KATANA_RESOURCES', '/opt/pixar/RenderManForKatana-24.1/plugins/katana4.0', 9, 4),
('MARI_CACHE', '/tmp/mari.cache."$USERNAME""$DATE"', 11, 1),
('PIXAR_LICENSE_FILE', '9010@talavera.bournemouth.ac.uk', 12, 1),
('AW_LOCATION', '/usr/autodesk', 12, 2),
('MAYA_LOCATION', '"$AW_LOCATION"/maya', 12, 3),
('HOUDINI_VERSION', 'hfs18.5.596', 12, 4),
('HOUDINI_MAYA_PLUGIN_VERSION', 'maya2020', 12, 5),
('GOLAEM_VERSION', 'Golaem-7.3.11-Maya2020', 12, 6),
('YETI_VERSION', 'Yeti-v4.0.1_Maya2020-linux', 12, 7),
('RENDERMAN_PROSERVER', 'RenderManProServer-24.1', 12, 8),
('RENDERMAN_FOR_MAYA', 'RenderManForMaya-24.1', 12, 9),
('RMANTREE', '/opt/pixar/"$RENDERMAN_PROSERVER"', 12, 10),
('RSTUDIOTREE', '/opt/pixar/"$RENDERMAN_FOR_MAYA"', 12, 11),
('RMSTREE', '/opt/pixar/"$RENDERMAN_FOR_MAYA"', 12, 12),
('MAYA_PLUG_IN_PATH', '"$RMSTREE"/plug-ins', 12, 13),
('MAYA_SCRIPT_PATH', '"$RMSTREE"/scripts:"$RSTUDIOTREE"/scripts', 12, 14),
('XBMLANGPATH', '"$RMSTREE"/icons/', 12, 15),
('RMANFB', 'it', 12, 16),
('MAYA_PLUG_IN_PATH', '"$RSTUDIOTREE"/plug-ins:~/plug-ins', 12, 17),
('XBMLANGPATH', '"$RSTUDIOTREE"/lib/mtor/resources/%B:"$XBMLANGPATH"', 12, 18),
('XBMLANGPATH', '"$XBMLANGPATH":"$RSTUDIOTREE"/icons/%B', 12, 19),
('XBMLANGPATH', '"$XBMLANGPATH":/opt/Golaem/"$GOLAEM_VERSION"/icons/%B', 12, 20),
('PATH', '"$PATH":"$RSTUDIOTREE"/bin:"$RMANTREE"/bin:/opt/Golaem/"$GOLAEM_VERSION"/icons/bin', 12, 21),
('MAYA_PLUG_IN_PATH', '"$MAYA_PLUG_IN_PATH":/usr/autodesk/maya/devkit-files/plug-ins', 12, 22),
('MAYA_SCRIPT_PATH', '"$MAYA_SCRIPT_PATH":/usr/autodesk/maya/devkit-files/scripts', 12, 23),
('XBMLANGPATH', '"$XBMLANGPATH":/usr/autodesk/maya/devkit-files/icons/%B', 12, 24),
('XBMLANGPATH', '"$XBMLANGPATH":/opt/yeti/"$YETI_VERSION"/icons/%B', 12, 25),
('MI_CUSTOM_SHADER_PATH', '"$HOME"/maya/mentalray/include', 12, 26),
('MI_LIBRARY_PATH', '"$HOME"/maya/mentalray/lib', 12, 27),
('LD_LIBRARY32_PATH', '"$MAYA_LOCATION"/lib:"$AW_LOCATION"/COM/lib:"$RSTUDIOTREE"/bin:"$RSTUDIOTREE"/lib', 12, 28),
('PYTHONPATH', '/usr/lib/python2.7/site-packages:"$PYTHONPATH"', 12, 29),
('VRAY_FOR_MAYA2020_MAIN', '/opt/VRAY2020/maya_vray', 12, 30),
('VRAY_FOR_MAYA2020_PLUGINS', '/opt/VRAY2020/maya_vray/vrayplugins', 12, 31),
('VRAY_OSL_PATH_MAYA2020', '/opt/VRAY2020/vray/opensl', 12, 32),
('LD_LIBRARY_PATH', '/opt/VRAY2020/maya_root/lib/:"$LD_LIBRARY_PATH"', 12, 33),
('MAYA_PLUG_IN_PATH', '/opt/VRAY2020/maya_vray/plug-ins:"$MAYA_PLUG_IN_PATH"', 12, 34),
('MAYA_SCRIPT_PATH', '/opt/VRAY2020/maya_vray/scripts:"$MAYA_SCRIPT_PATH"', 12, 35),
('MAYA_PRESET_PATH', '/opt/VRAY2020/maya_vray/presets:"$MAYA_PRESET_PATH"', 12, 36),
('PYTHONPATH', '/opt/VRAY2020/maya_vray/scripts:"$PYTHONPATH"', 12, 37),
('XBMLANGPATH', '/opt/VRAY2020/maya_vray/icons/%B:"$XBMLANGPATH"', 12, 38),
('VRAY_AUTH_CLIENT_FILE_PATH', '/opt', 12, 39),
('MAYA_CUSTOM_TEMPLATE_PATH', '/opt/VRAY2020/maya_vray/scripts:"$MAYA_CUSTOM_TEMPLATE_PATH"', 12, 40),
('MAYA_PLUG_IN_PATH', '"$MAYA_PLUG_IN_PATH":/opt/"$HOUDINI_VERSION"/engine/maya/"$HOUDINI_MAYA_PLUGIN_VERSION"/plug-ins', 12, 41),
('MAYA_SCRIPT_PATH', '"$MAYA_SCRIPT_PATH":/opt/"$HOUDINI_VERSION"/engine/maya/"$HOUDINI_MAYA_PLUGIN_VERSION"/scripts', 12, 42),
('MAYA_MODULE_PATH', '"$MAYA_MODULE_PATH":/opt/"$HOUDINI_VERSION"/engine/maya', 12, 43),
('MAYA_MMSET_DEFAULT_XCURSOR', '1', 12, 44),
('XBMLANGPATH', '"$XBMLANGPATH":/opt/yeti/"$YETI_VERSION"/icons/%B', 12, 45),
('MAYA_PLUG_IN_PATH', '"$MAYA_PLUG_IN_PATH":/opt/yeti/"$YETI_VERSION"/plug-ins', 12, 46),
('MAYA_MODULE_PATH', '"$MAYA_MODULE_PATH":/opt/yeti/"$YETI_VERSION"', 12, 47),
('VRAY_FOR_MAYA2019_PLUGINS', '"$VRAY_FOR_MAYA2019_PLUGINS":/opt/yeti/"$YETI_VERSION"/bin', 12, 48),
('VRAY_PLUGINS_x64', '"$VRAY_PLUGINS_x64":/opt/yeti/"$YETI_VERSION"/bin', 12, 49),
('MAYA_SCRIPT_PATH', '"$MAYA_SCRIPT_PATH":/opt/yeti/"$YETI_VERSION"/scripts', 12, 50),
('MTOA_EXTENSIONS_PATH', '/opt/yeti/"$YETI_VERSION"/plug-ins', 12, 51),
('ARNOLD_PLUGIN_PATH', '/opt/yeti/"$YETI_VERSION"/bin', 12, 52),
('TMPDIR', '/tmp', 12, 53),
('LD_LIBRARY_PATH', '/opt/yeti/"$YETI_VERSION"/plug-ins:"$LD_LIBRARY_PATH":/opt/VRAY2020/vray/lib', 12, 54),
('RLM_LICENSE', '5063@burton', 12, 55),
('golaem_LICENSE', '2375@handy', 12, 56),
('GOLAEM_CROWD_HOME', '/opt/Golaem/"$GOLAEM_VERSION"', 12, 57),
('MAYA_MODULE_PATH', '"$MAYA_MODULE_PATH":"$GOLAEM_CROWD_HOME"', 12, 58),
('XBMLANGPATH', '"$XBMLANGPATH":"/opt/Golaem/"$GOLAEM_VERSION"/icons/%B"', 12, 59),
('PATH', '"$PATH":"$RSTUDIOTREE"/bin:"$RMANTREE"/bin:/opt/Golaem/"$GOLAEM_VERSION"/icons/bin', 12, 60),
('MAYA_PLUG_IN_PATH', '"$GOLAEM_CROWD_HOME"/plug-ins:"$MAYA_PLUG_IN_PATH"', 12, 61),
('MAYA_SCRIPT_PATH', '"$GOLAEM_CROWD_HOME"/scripts:"$MAYA_SCRIPT_PATH"', 12, 62),
('PATH', '"$PATH":"$GOLAEM_CROWD_HOME"/bin', 12, 63),
('LD_LIBRARY_PATH', '"$LD_LIBRARY_PATH":"$GOLAEM_CROWD_HOME"/lib', 12, 64),
('RMS_SCRIPT_PATHS', '"$RMS_SCRIPT_PATHS":"$GOLAEM_CROWD_HOME"/procedurals', 12, 65),
('RMS_PROCEDURAL_PATH', '"$RMS_PROCEDURAL_PATH":"$GOLAEM_CROWD_HOME"/procedurals', 12, 66),
('RMS_SHADER_PATH', '"$RMS_SHADER_PATH":"$GOLAEM_CROWD_HOME"/shaders', 12, 67),
('VRAY_FOR_MAYA_SHADERS', '"$GOLAEM_CROWD_HOME"/shaders:"$VRAY_FOR_MAYA_SHADERS"', 12, 68),
('VRAY_FOR_MAYA2020_PLUGINS', '"$GOLAEM_CROWD_HOME"/procedurals:"$VRAY_FOR_MAYA2020_PLUGINS"', 12, 69),
('MI_CUSTOM_SHADER_PATH', '"$GOLAEM_CROWD_HOME"/procedurals:"$MI_CUSTOM_SHADER_PATH"', 12, 70),
('LD_LIBRARY_PATH', '/opt/yeti/"$YETI_VERSION"/plug-ins:"$LD_LIBRARY_PATH"', 12, 71),
('PYTHONPATH', '/opt/pixar/"$RENDERMAN_FOR_MAYA"/scripts/rfm2:/opt/pixar/"$RENDERMAN_FOR_MAYA"/scripts:/opt/autodesk/maya/lib/python2.7/site-packages:"$PYTHONPATH"', 12, 72),
('MAYA_MODULE_PATH', '"$MAYA_MODULE_PATH":"$RSTUDIOTREE"/etc', 12, 73),
('LD_LIBRARY_PATH', '"$LD_LIBRARY_PATH":/usr/autodesk/mudbox/lib', 16, 1),
('NUKE_TEMP_DIR', '/transfer/nuke."$USERNAME"', 18, 1),
('NUKE_DISK_CACHE', '/transfer/nuke-cache."$USERNAME"', 18, 2),
('OFX_PLUGIN_PATH', '/opt/OFX', 18, 3),
('NUKE_PATH', '/public/devel/2021/KeenTools', 18, 4),
('KEENTOOLS_LICENSE_SERVER', '7096@beijing.bournemouth.ac.uk', 18, 5),
('LD_LIBRARY_PATH', '/opt/thepixelfarm/pftrack/lib/', 20, 1),
('PFTRACK_APP_DIR', '/opt/thepixelfarm/pftrack/', 20, 2),
('QB_SUPERVISOR', 'tete.bournemouth.ac.uk', 23, 1),
('QB_DOMAIN', 'ncca', 23, 2),
('PYTHONPATH', '', 23, 3);

COMMIT;