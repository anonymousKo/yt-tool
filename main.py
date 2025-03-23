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
    url = request.args.get('url')
    video_id = request.args.get('video_id')
    command = f'yt-dlp -f {video_id} --get-filename -o "%(title)s.%(ext)s" {url}'

    try:
        # Execute yt-dlp command to get the original filename
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        # Check for errors
        if process.returncode != 0:
            return f'Error: {error}'

        # Get the original filename
        filename = output.decode().strip()

        # Download the video file
        download_command = f'yt-dlp -f {video_id} -o "{filename}" {url}'
        subprocess.run(download_command, shell=True, check=True)

        # Check if the file exists
        if os.path.exists(filename):
            # Send the file to the client
            return send_file(filename, as_attachment=True)

        else:
            return 'Error: File not found.'

    except subprocess.CalledProcessError as e:
        return f'Error: {str(e)}'

    except Exception as e:
        return f'Error: {str(e)}'

    finally:
        # Delete the downloaded file
        if os.path.exists(filename):
            os.remove(filename)
        
if __name__ == '__main__':
    app.run(port=8091,host='0.0.0.0')

