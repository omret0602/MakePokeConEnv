import json
import os
import shutil
import subprocess
import tarfile
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from tkinter import filedialog, messagebox

import requests
from loguru import logger as _logger

from consts import (
	DEFAULT_TYPE_REQUIREMENTS_TXT_PATH,
	DOWNLOAD_FOLDER_NAME,
	EXTENSION_UPDATECHECKER_PY_NAME,
	GIT_FILE_NAME,
	GIT_JSON_FILE_PATH,
	INSTALL_PYTHON_FOLDER_NAME,
	LIBRARY_INSTALL_BAT,
	LOG_FILE_PATH,
	POKECON_TYPE_LIST,
	POKECON_TYPE_MODIFIED,
	POKECON_TYPE_MODIFIED_EXTENSION,
	POKECON_TYPE_NAME_LIST,
	POKECON_TYPE_NAME_MODIFIED,
	POKECON_TYPE_NAME_MODIFIED_EXTENSION,
	POKECON_TYPE_NAME_NORMAL,
	POKECON_TYPE_NORMAL,
	POKECON_VER_JSON_FILE_PATH,
	PYTHON_EXE_NAME,
	PYTHON_TAR_FILE_NAME,
	PYTHON_VERSION_JSON_PATH,
	SERIALCONTROLLER_FOLDER_NAME,
	START_BAT_NAME,
)
from utils import library_install_bat_txt, start_bat_default_txt, start_bat_ext_txt


class MakePokeConEnvironment:
	def __init__(self, master=None):
		# logger setting
		_logger.add(LOG_FILE_PATH, rotation='1 day', level='INFO')
		self.logger = _logger

		# window setting
		self.root = master
		self.root.title('Make-PokeCon-Enviroment')

		frame_1 = ttk.Frame(self.root)
		frame_1.configure(height=588, width=488)
		label_2 = ttk.Label(frame_1)
		label_2.configure(anchor='center', background='#3993c7', font='{游ゴシック} 12 {}', justify='center', relief='ridge', text='Poke-Controller 環境構築')
		label_2.place(anchor='nw', relheight=0.1, relwidth=0.8, relx=0.1, rely=0.05, x=0, y=0)
		label_3 = ttk.Label(frame_1)
		label_3.configure(anchor='center', background='#3993c7', font='{游ゴシック} 12 {}', justify='center', relief='ridge', text='path')
		label_3.place(anchor='nw', relheight=0.1, relwidth=0.3, relx=0.1, rely=0.2, x=0, y=0)
		label_4 = ttk.Label(frame_1)
		label_4.configure(anchor='center', background='#3993c7', font='{游ゴシック} 12 {}', justify='center', relief='ridge', text='PokeCon')
		label_4.place(anchor='nw', relheight=0.1, relwidth=0.3, relx=0.1, rely=0.35, x=0, y=0)
		label_5 = ttk.Label(frame_1)
		label_5.configure(anchor='center', background='#3993c7', font='{游ゴシック} 12 {}', justify='center', relief='ridge', text='Python Ver')
		label_5.place(anchor='nw', relheight=0.1, relwidth=0.3, relx=0.1, rely=0.5, x=0, y=0)

		self.combobox_select_path = ttk.Combobox(frame_1)
		self.install_folder_path_var = tk.StringVar()
		self.combobox_select_path.configure(
			justify='center', state='readonly', textvariable=self.install_folder_path_var, values=['参照(Cドライブ直下推奨)'])
		self.combobox_select_path.place(anchor='nw', relheight=0.1, relwidth=0.5, relx=0.4, rely=0.2, x=0, y=0)

		# pokecon_ver_list = 
		self.combobox_select_pokecon_ver = ttk.Combobox(frame_1)
		self.select_pokecon_ver = tk.StringVar()
		self.combobox_select_pokecon_ver.configure(
			justify='center', state='readonly', textvariable=self.select_pokecon_ver, values=self.get_pokecon_ver())
		self.combobox_select_pokecon_ver.place(anchor='nw', relheight=0.1, relwidth=0.5, relx=0.4, rely=0.35, x=0, y=0)

		self.combobox_install_python_ver = ttk.Combobox(frame_1)
		self.install_python_ver = tk.StringVar()
		self.combobox_install_python_ver.configure(
			justify='center', state='readonly', textvariable=self.install_python_ver, values=self.get_python_ver())
		self.combobox_install_python_ver.option_add('*TCombobox*Listbox.Font', ('{游ゴシック} 12 {}'))
		self.combobox_install_python_ver.place(anchor='nw', relheight=0.1, relwidth=0.5, relx=0.4, rely=0.5, x=0, y=0)

		self.button_install = ttk.Button(frame_1)
		self.button_install.configure(text='開始', state='disabled', command=self.main)
		self.button_install.place(anchor='nw', relheight=0.1, relwidth=0.8, relx=0.1, rely=0.85, x=0, y=0)
		frame_1.grid(column=0, padx=6, pady=6, row=0, sticky='nsew')

		self.mainwindow = frame_1
		self.bind()

	def bind(self):
		self.root.protocol('WM_DELETE_WINDOW', self.closing)
		self.combobox_select_path.bind('<<ComboboxSelected>>', self.select_folder)
		self.combobox_select_pokecon_ver.bind('<<ComboboxSelected>>', self.input_check)
		self.combobox_install_python_ver.bind('<<ComboboxSelected>>', self.input_check)

	def main(self):
		self.button_install['state'] = 'disabled'

		if not messagebox.askokcancel('インストール確認', f'{self.install_folder_path_var.get()}\n{self.select_pokecon_ver.get()}\n{self.install_python_ver.get()}\n上記内容でインストールを開始します。よろしいですか? \nまた、インストール中は応答なしになります。'):
			self.button_install['state'] = 'enable'
			return 

		self.load_path_settings()
		if not self.get_python():
			self.logger.error('Python download ERROR')
			self.button_install['state'] = 'enable'
			return messagebox.showerror('error', 'PythonのDL中にエラーが発生しました。')

		# Git download install
		if not self.get_git():
			self.logger.error('Exception Git.')
			self.button_install['state'] = 'enable'
			return messagebox.showerror('error', 'GitのDL.Install中にエラーが発生しました。')

		# Clone poke-con
		if not self.get_pokecon():
			self.logger.error('Clone ERROR.')
			self.button_install['state'] = 'enable'
			return messagebox.showerror('error', 'Poke-ConのClone中にエラーが発生しました。')

		# Install Python library.
		if not self.install_library():
			self.logger.error('Install library ERROR.')
			self.button_install['state'] = 'enable'
			return messagebox.showerror('error', 'ライブラリをインストール中にエラーが発生しました。')

		# Create Start bat.
		if not self.create_start_bat():
			self.logger.error('Does not create start.bat.')
			self.button_install['state'] = 'enable'
			return messagebox.showerror('error', 'start.batの作成中にエラーが発生しました。')
		
		if not self.create_library_install_bat():
			self.logger.error('Does not create library_install.bat.')
			self.button_install['state'] = 'enable'
			return messagebox.showerror('error', 'library_install.batの作成中にエラーが発生しました。')

		self.logger.success('Sucessfully make Poke-Con environment.')
		self.button_install['state'] = 'enable'
		messagebox.showinfo('環境構築完了', '環境構築が完了しました。')

	def load_path_settings(self):
		# install先フォルダーpath
		self.install_folder_path = Path(self.install_folder_path_var.get())
		if self.install_folder_path.exists():
			self.install_folder_path.mkdir(parents=True, exist_ok=True)

		# downloadフォルダーpath
		self.download_folder_path = self.install_folder_path.joinpath(DOWNLOAD_FOLDER_NAME)
		self.download_folder_path.mkdir(parents=True)

	def get_python(self):
		self.logger.info('Start download Python.')
		try:
			response = requests.get(json.load(open(PYTHON_VERSION_JSON_PATH, mode='r'))[self.install_python_ver.get()]['url'])
			if response.status_code == 200:
				python_builds_path = self.download_folder_path.joinpath(PYTHON_TAR_FILE_NAME)
				with open(python_builds_path, mode='wb') as file:
					for chunk in response.iter_content(chunk_size=4096):
						if chunk:
							file.write(chunk)
				with tarfile.open(python_builds_path, 'r:gz') as tar:
					tar.extractall(path=self.install_folder_path)
				self.logger.info('Python download sucessfully.')
			return response.status_code == 200
		except Exception as e:
			self.logger.exception(e)
			return False

	def get_git(self):
		try:
			if self.is_install_check_git():
				self.logger.info('Skip this step because Git is already installed.')
				return True
			self.logger.info('Start download Git.')
			response = requests.get(json.load(open(GIT_JSON_FILE_PATH, mode='r'))['url'])
			git_file_path = self.download_folder_path.joinpath(GIT_FILE_NAME)
			if response.status_code == 200:
				with open(git_file_path, 'wb') as file:
					for chunk in response.iter_content(chunk_size=4096):
						if chunk:
							file.write(chunk)
				self.logger.info('Finish download Git.')
				self.logger.info('Start install Git.')
				install_git_args = [
					str(git_file_path),
					"/VERYSILENT",
					"/NORESTART",
					"/NOCANCEL", "/SP-",
					"/CLOSEAPPLICATIONS",
					"/RESTARTAPPLICATIONS",
					'/COMPONENTS="icons,ext\\reg\shellhere,assoc,assoc_sh"',
				]
				subprocess.run(install_git_args, shell=True)
				self.logger.info('Finish install Git.')
			return response.status_code == 200
		except Exception as e:
			self.logger.exception(e)
			return False

	def get_pokecon(self):
		self.logger.info('Start clone PokeCon.')
		try:
			if not self.is_install_check_git():
				self.logger.warning('WARNING: Git is not installed. or PATH does not through. Please restart computer.')
				messagebox.showwarning('Gitインストール警告', 'Gitがインストールされていない \nもしくは\nPATHが通っていないため、PCを再起動して最初から実行してください。')
				return False
			json_data = json.load(open(POKECON_VER_JSON_FILE_PATH, mode='r'))[self.select_pokecon_ver.get()]
			git_url = json_data['url']
			git_branch_name = json_data['branch_name']
			git_clone_args = ['git', 'clone', '--recursive', '-b', git_branch_name, git_url]
			subprocess.run(git_clone_args, cwd=self.install_folder_path, shell=True)
			self.logger.info('Finish clone PokeCon')
			return True
		except Exception as e:
			self.logger.exception(e)
			return False

	def install_library(self):
		self.logger.info('Start install Python library.')
		try:
			python_folder_path = self.install_folder_path.joinpath(INSTALL_PYTHON_FOLDER_NAME)
			pokecon_type = self.get_pokecon_type()
			pokecon_type_name = self.get_pokecon_type_name()
			requirements_txt_path = self.install_folder_path.joinpath(pokecon_type_name, 'requirements.txt')

			# pip upgrade
			pip_upgrade_args = ['python.exe', '-m', 'pip', 'install', '--upgrade', 'pip']
			subprocess.run(pip_upgrade_args, cwd=python_folder_path, shell=True)

			# setuptools upgrade
			setuptools_upgrade_args = ['python.exe', '-m', 'pip', 'install', '--upgrade', 'setuptools']
			subprocess.run(setuptools_upgrade_args, cwd=python_folder_path, shell=True)

			# 本家Poke-conをインストールする場合
			if pokecon_type == POKECON_TYPE_NORMAL and pokecon_type_name == POKECON_TYPE_NAME_NORMAL:
				normal_args = ['python.exe', '-m', 'pip', 'install', '-r', f'{DEFAULT_TYPE_REQUIREMENTS_TXT_PATH}']
				subprocess.run(normal_args, cwd=python_folder_path, shell=True)

			# Poke-con-modifiedをインストールする場合
			elif pokecon_type == POKECON_TYPE_MODIFIED and pokecon_type_name == POKECON_TYPE_NAME_MODIFIED:
				modified_args = ['python.exe', '-m', 'pip', 'install', '-r', f'{requirements_txt_path}']
				subprocess.run(modified_args, cwd=python_folder_path, shell=True)

			# Poke-con-modified-extensionをインストールする場合
			elif pokecon_type == POKECON_TYPE_MODIFIED_EXTENSION and pokecon_type_name == POKECON_TYPE_NAME_MODIFIED_EXTENSION:
				extension_args = ['python.exe', '-m', 'pip', 'install', '-r', f'{requirements_txt_path}']
				subprocess.run(extension_args, cwd=python_folder_path, shell=True)

			# JSONの項目が正しく入力されていない場合はエラーを表示。
			else:
				self.logger.error('Invalid Poke-Con type.')
				messagebox.showerror('Poke-Conの種類指定が無効なため、ライブラリのインストールに失敗しました。')
				return False

			self.logger.info('Finish install Python library.')
			return True

		except Exception as e:
			self.logger.exception(e)
			return False

	def create_start_bat(self):
		try:
			pokecon_type = self.get_pokecon_type()
			pokecon_type_name = self.get_pokecon_type_name()
			serialcontroller_path = self.install_folder_path.joinpath(pokecon_type_name, SERIALCONTROLLER_FOLDER_NAME)
			python_exe_path = self.install_folder_path.joinpath(INSTALL_PYTHON_FOLDER_NAME, PYTHON_EXE_NAME)

			# 本家Poke-conをインストールする場合
			if pokecon_type == POKECON_TYPE_NORMAL and pokecon_type_name == POKECON_TYPE_NAME_NORMAL:
				txt = start_bat_default_txt(python_exe_path, serialcontroller_path)

			# Poke-con-modifiedをインストールする場合
			elif pokecon_type == POKECON_TYPE_MODIFIED and pokecon_type_name == POKECON_TYPE_NAME_MODIFIED:
				txt = start_bat_default_txt(python_exe_path, serialcontroller_path)

			# Poke-con-modified-extensionをインストールする場合
			elif pokecon_type == POKECON_TYPE_MODIFIED_EXTENSION and pokecon_type_name == POKECON_TYPE_NAME_MODIFIED_EXTENSION:
				extension_folder_path = self.install_folder_path.joinpath(pokecon_type_name)
				updatechecker_path = serialcontroller_path.joinpath(EXTENSION_UPDATECHECKER_PY_NAME)
				txt = start_bat_ext_txt(
					python_exe_path,
					serialcontroller_path,
					extension_folder_path,
					updatechecker_path,
				)

			else:
				self.logger.error('Invalid Poke-Con type. Does not create start.bat.')
				messagebox.showerror('Poke-Conの種類指定が無効なため、batファイルの作成に失敗しました。')
				return False

			with open(self.install_folder_path.joinpath(START_BAT_NAME), 'w', encoding='utf-8') as file:
				file.write(txt)
			return True

		except Exception as e:
			self.logger.exception(e)
			return False

	def create_library_install_bat(self):
		try:
			python_exe_path = self.install_folder_path.joinpath(INSTALL_PYTHON_FOLDER_NAME, PYTHON_EXE_NAME)
			library_install_bat_path = self.install_folder_path.joinpath(LIBRARY_INSTALL_BAT)
			txt = library_install_bat_txt(python_exe_path)

			with open(library_install_bat_path, 'w', encoding='cp932') as file:
				file.write(txt)

		except Exception as e:
			self.logger.exception(e)
			return False
		return True

	def is_install_check_git(self):
		if shutil.which("git"):
			try:
				subprocess.run(["git", "--version"])
				return True
			except subprocess.CalledProcessError:
				pass
		return False

	def input_check(self, event=None):
		self.logger.info("Input Check")
		if not all([self.install_folder_path_var.get(), self.select_pokecon_ver.get(), self.install_python_ver.get()]):
			self.button_install['state'] = 'disabled'
		else:
			self.button_install['state'] = 'enabled'
			self.logger.info("Input Check OK")

	def select_folder(self, event=None):
		self.button_install['state'] = 'disabled'
		if self.install_folder_path_var.get() == '参照(Cドライブ直下推奨)':
			self.install_folder_path_var.set('')
			install_folder_path = Path(is_ask := filedialog.askdirectory(title='PokeConをインストールする空のフォルダーを選択してください。(日本語が含まれているフォルダー名非推奨)'))
			# フォルダーがそもそも選択されていない場合にエラー表示
			if not is_ask:
				self.logger.error('Folder Not Selection Error.')
				return messagebox.showerror('フォルダー選択エラー', 'インストール先のフォルダーが選択されませんでした。')

			# 空のフォルダーが選択されていないときにエラー表示
			if os.listdir(install_folder_path):
				self.logger.error('Folder Selection Error.')
				self.install_folder_path_var.set('')
				return messagebox.showerror('フォルダー選択エラー', '選択されたフォルダーにはインストールできません。\nインストール先は空のフォルダーを選択してください。')
			self.install_folder_path_var.set(install_folder_path)
			self.input_check()

	def get_pokecon_type(self):
		pokecon_type = json.load(open(POKECON_VER_JSON_FILE_PATH, mode='r'))[self.select_pokecon_ver.get()]['type']
		if pokecon_type not in POKECON_TYPE_LIST:
			return 'invalid_type'
		return pokecon_type

	def get_pokecon_type_name(self):
		pokecon_type = json.load(open(POKECON_VER_JSON_FILE_PATH, mode='r'))[self.select_pokecon_ver.get()]['name']
		if pokecon_type not in POKECON_TYPE_NAME_LIST:
			return 'invalid_type_name'
		return pokecon_type

	def get_pokecon_ver(self):
		self.logger.info('Get Pokecon Ver')
		return [key for key in json.load(open(POKECON_VER_JSON_FILE_PATH, mode='r')).keys()]

	def get_python_ver(self):
		self.logger.info('Get Python Ver')
		return [key for key in json.load(open(PYTHON_VERSION_JSON_PATH, mode='r')).keys()]

	def closing(self):
		self.logger.info('Confirmation at finish.')
		if messagebox.askyesno('終了確認', '終了しますか?'):
			self.mainwindow.quit()

	def run(self):
		self.mainwindow.mainloop()

if __name__ == '__main__':
	root = tk.Tk()
	app = MakePokeConEnvironment(master=root)
	app.run()