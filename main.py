from flask import Flask, request, send_from_directory, send_file
import subprocess
import os

app = Flask(__name__)

@app.route('/info', methods=['GET'])
def get_video_info():
    url = request.args.get('url')
    command = f'yt-dlp -F {url}'

    try:
        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        return result
    except subprocess.CalledProcessError as e:
        return f'Error: {e.output}'

DOWNLOAD_DIRECTORY = '/home/youtube-dl'

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    video_id = request.args.get('id')
    command = f'yt-dlp -f {video_id} {url} -o "{DOWNLOAD_DIRECTORY}/%(title)s.%(ext)s"'

    try:
        result = subprocess.check_output(command, shell=True, universal_newlines=True)
        return result
    except subprocess.CalledProcessError as e:
        return f'Error: {e.output}'

FILE_CACHE = []

@app.route('/list', methods=['GET'])
def list_files():
    refresh_file_cache()
    return '\n'.join(FILE_CACHE)


@app.route('/get', methods=['GET'])
def download_file():
    id = request.args.get('id')
    filename = get_filename_by_id(id)
    if filename:
        return send_from_directory(DOWNLOAD_DIRECTORY, filename, as_attachment=True)
    else:
        return 'File not found.'

def refresh_file_cache():
    global FILE_CACHE
    files = sorted(os.listdir(DOWNLOAD_DIRECTORY))
    FILE_CACHE = [f'ID: {i+1}, Filename: {filename}' for i, filename in enumerate(files)]

refresh_file_cache()

def get_filename_by_id(file_id):
    index = int(file_id) - 1
    if 0 <= index < len(FILE_CACHE):
        filename = FILE_CACHE[index].split(', Filename: ')[1]
        return filename.strip()
    return None

if __name__ == '__main__':
    app.run(port=8095,host='0.0.0.0')

