from flask import Flask, request, send_from_directory, send_file, Response
import subprocess
import os
import json
import requests
import urllib.parse

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
    video_id = request.args.get('id')
    command = f'yt-dlp -f {video_id} {url} -j'

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()
        video_data = json.loads(output)

        # Extract video title and sanitize it for the filename
        video_title = video_data['title']
        sanitized_title = urllib.parse.quote_plus(video_title)  # URL encode the title

        # Get the direct video URL
        video_url = video_data['url']

        # Send a request to get the video content
        response = requests.get(video_url, stream=True)

        # Set the appropriate headers for the file download
        headers = {
            'Content-Type': 'video/mp4',
            'Content-Disposition': f'attachment; filename="{sanitized_title}.mp4"'
        }

        # Create a Flask response with the video content as the file content
        file_response = Response(response.iter_content(chunk_size=1024), headers=headers)
        return file_response

    except subprocess.CalledProcessError as e:
        return f'Error: {e.output}'

if __name__ == '__main__':
    app.run(port=8095,host='0.0.0.0')

