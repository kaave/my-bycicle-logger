from dropbox import Dropbox, files
from dotenv import load_dotenv
from glob import glob
from datetime import datetime
from os import path, environ, remove

load_dotenv()

token = environ['DROPBOX_TOKEN']

if __name__ == '__main__':
    dbx = Dropbox(token)
    dbx.users_get_current_account()
    now = datetime.now()
    csv_list = glob('csv/*.csv')

    for file_path in csv_list:
        with open(file_path, 'rb') as file:
            dbx.files_upload(
                file.read(),
                f'/{path.basename(file_path)}',
                mode=files.WriteMode.overwrite)
            delta = now - datetime.fromtimestamp(path.getmtime(file_path))

            if delta.days > 0:
                remove(file_path)
                print(f'uploaded and remove: {file_path}')
            else:
                print(f'uploaded: {file_path}')
