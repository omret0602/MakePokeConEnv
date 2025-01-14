import tkinter as tk
import tkinter.ttk as ttk
from loguru import logger as _logger

from tkinter import messagebox, filedialog

import json
from pathlib import Path
import os

CWD = Path.cwd()
PYTHON_VERSION_JSON_FILE_NAME = 'python_ver.json'
POKECON_VER_JSON_FILE_NAME = 'pokecon_ver.json'

class MakePokeConEnvironment:
	def __init__(self, master=None):
		# logger setting
		log_folder_path = CWD.joinpath('log')
		log_file_path = log_folder_path.joinpath('install_log.log')
		_logger.add(log_file_path, rotation='1 day', level='INFO')
		self.logger = _logger

		# Load Setting
		self.get_setting_path()

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
		self.install_folder_path = tk.StringVar()
		self.combobox_select_path.configure(
			justify='center', state='readonly', textvariable=self.install_folder_path, values=['参照(Cドライブ直下推奨)'])
		self.combobox_select_path.place(anchor='nw', relheight=0.1, relwidth=0.5, relx=0.4, rely=0.2, x=0, y=0)

		pokecon_ver_list = self.get_pokecon_ver()
		self.combobox_select_pokecon_ver = ttk.Combobox(frame_1)
		self.select_pokecon_ver = tk.StringVar()
		self.combobox_select_pokecon_ver.configure(
			justify='center', state='readonly', textvariable=self.select_pokecon_ver, values=pokecon_ver_list)
		self.combobox_select_pokecon_ver.place(anchor='nw', relheight=0.1, relwidth=0.5, relx=0.4, rely=0.35, x=0, y=0)

		python_ver_list = self.get_python_ver()
		self.combobox_install_python_ver = ttk.Combobox(frame_1)
		self.install_python_ver = tk.StringVar()
		self.combobox_install_python_ver.configure(
			justify='center', state='readonly', textvariable=self.install_python_ver, values=python_ver_list)
		self.combobox_install_python_ver.option_add('*TCombobox*Listbox.Font', ('{游ゴシック} 12 {}'))
		self.combobox_install_python_ver.place(anchor='nw', relheight=0.1, relwidth=0.5, relx=0.4, rely=0.5, x=0, y=0)

		self.button_install = ttk.Button(frame_1)
		self.button_install.configure(text='インストール開始',state='disabled')
		self.button_install.place(anchor='nw', relheight=0.1, relwidth=0.8, relx=0.1, rely=0.85, x=0, y=0)
		frame_1.grid(column=0, padx=6, pady=6, row=0, sticky='nsew')

		self.mainwindow = frame_1
		self.bind()

	def bind(self):
		self.root.protocol('WM_DELETE_WINDOW', self.closing)
		self.combobox_select_path.bind('<<ComboboxSelected>>', self.select_folder)
		self.combobox_select_pokecon_ver.bind('<<ComboboxSelected>>', self.input_check)
		self.combobox_install_python_ver.bind('<<ComboboxSelected>>', self.input_check)

	def input_check(self, event=None):
		self.logger.info("Input Check")
		if not all([self.install_folder_path.get(), self.select_pokecon_ver.get(), self.install_python_ver.get()]):
			self.button_install['state'] = 'disabled'
		else:
			self.button_install['state'] = 'enabled'
			self.logger.info("Input Check OK")

	def select_folder(self, event=None):
		self.button_install['state'] = 'disabled'
		if self.install_folder_path.get() == '参照(Cドライブ直下推奨)':
			self.install_folder_path.set('')
			install_folder_path = Path(is_ask := filedialog.askdirectory(title='PokeConをインストールする空のフォルダーを選択してください。(日本語が含まれているフォルダー名非推奨)'))
			# フォルダーがそもそも選択されていない場合にエラー表示
			if not is_ask:
				self.logger.error('Folder Not Selection Error.')
				return messagebox.showerror('フォルダー選択エラー', 'インストール先のフォルダーが選択されませんでした。')

			# 空のフォルダーが選択されていないときにエラー表示
			if os.listdir(install_folder_path):
				self.logger.error('Folder Selection Error.')
				self.install_folder_path.set('')
				return messagebox.showerror('フォルダー選択エラー', '選択されたフォルダーにはインストールできません。\nインストール先は空のフォルダーを選択してください。')
			self.install_folder_path.set(install_folder_path)
			self.input_check()

	def get_setting_path(self):
		setting_folder_path = CWD.joinpath('settings')
		self.pokecon_ver_json_file_path = setting_folder_path.joinpath(POKECON_VER_JSON_FILE_NAME)
		self.python_ver_json_file_path = setting_folder_path.joinpath(PYTHON_VERSION_JSON_FILE_NAME)

	def get_pokecon_ver(self):
		self.logger.info('Get Pokecon Ver')
		return [key for key in json.load(open(self.pokecon_ver_json_file_path)).keys()]

	def get_python_ver(self):
		self.logger.info('Get Python Ver')
		return [key for key in json.load(open(self.python_ver_json_file_path)).keys()]

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