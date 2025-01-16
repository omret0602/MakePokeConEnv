from consts import WINDOW_PY_NAME


def start_bat_default_txt(python_exe_path, serialcontroller_path):
    txt = f"""
cd {str(serialcontroller_path)}
{str(python_exe_path)} {WINDOW_PY_NAME}
pause
"""
    return txt

def start_bat_ext_txt(python_exe_path, serialcontroller_path, extension_folder_path, updatechecker_path):
    txt = f"""
cd {str(extension_folder_path)}
{str(python_exe_path)} {str(updatechecker_path)}
cd {str(serialcontroller_path)}
rem python Window.py --profile dragonite
{str(python_exe_path)} Window.py
pause
"""
    return txt

def library_install_bat_txt(python_exe_path):
    txt = f'''
@echo off
echo =====================================
echo Pythonライブラリ インストール
echo =====================================
echo.
set /p libname=インストールしたいライブラリ名を入力してください（複数の場合はスペースで区切って入力）: 

if "%libname%"=="" (
    echo ライブラリ名が入力されませんでした。
    pause
    exit /b
)

echo %libname% をインストールしています...
{python_exe_path} -m pip install %libname%

echo ライブラリのインストールが完了しました。
pause
'''
    return txt
