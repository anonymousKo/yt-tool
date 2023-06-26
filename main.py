from flask import Flask, request, send_from_directory, send_file, Response
import subprocess
import os
import json

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
    command = f'yt-dlp -f {video_id} {url} -j'

    try:
        # Execute yt-dlp command and capture the output
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()

        # Print the output
        print(output)

        # Parse the JSON output containing video metadata
        video_data = json.loads(output)
        video_title = video_data['title']
        video_extension = video_data['ext']

        # Set the appropriate headers for the file download
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': f'attachment; filename="{video_title}.{video_extension}"'
        }

        # Create a Flask response with the output as the file content
        response = Response(video_data, headers=headers)
        return response

    except subprocess.CalledProcessError as e:
        return f'Error: {e.output}'
        
if __name__ == '__main__':
    app.run(port=8095,host='0.0.0.0')

