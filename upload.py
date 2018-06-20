from dropbox import Dropbox
from dotenv import load_dotenv
from glob import glob
from os import path, environ

load_dotenv()

token = environ['DROPBOX_TOKEN']

if __name__ == '__main__':
    dbx = Dropbox(token)
    dbx.users_get_current_account()

    csv_list = glob('csv/*.csv')
    for file_path in csv_list:
        with open(file_path, 'rb') as file:
            dbx.files_upload(file.read(), f'/{path.basename(file_path)}')
            print(f'uploaded: {file_path}')
