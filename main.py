from flask import Flask, request, send_from_directory, send_file, Response, after_this_request
import subprocess
import os
import json
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('index.html')

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


@app.route('/getFile', methods=['GET'])
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


@app.route('/get', methods=['GET'])
def download_directly():
    @app.route('/get', methods=['GET'])
def download_directly():
    url = request.args.get('url')
    video_id = request.args.get('video_id')
    command = f'yt-dlp -f {video_id} {url} -o "%(title)s.%(ext)s"'

    try:
        # Execute yt-dlp command to download the video file
        subprocess.run(command, shell=True, check=True)

        # Get the title and extension of the downloaded video
        video_title = subprocess.check_output(f'yt-dlp --get-title {url}', shell=True).decode().strip()
        video_extension = subprocess.check_output(f'yt-dlp --get-filename {url} --format {video_id} --no-playlist', shell=True).decode().split('.')[-1]

        # Set the appropriate headers for the file download
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename="{video_title}.{video_extension}"'
        }

        # Read the file content
        file_path = f"{video_title}.{video_extension}"
        with open(file_path, 'rb') as file:
            file_content = file.read()

        # Create a Flask response with the file content as the response body
        response = Response(file_content, headers=headers)

        # Delete the file from the server
        os.remove(file_path)

        return response

    except subprocess.CalledProcessError as e:
        return f'Error: {str(e)}'

    except Exception as e:
        return f'Error: {str(e)}'
        
if __name__ == '__main__':
    app.run(port=8095,host='0.0.0.0')

