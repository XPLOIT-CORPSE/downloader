import json
from flask import Flask, render_template, request, jsonify, send_file
from pytube import YouTube
import requests
import os
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, APIC, error
import tempfile
import atexit
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define a list to keep track of temporary files
temporary_files = []
def search_video_by_name(video_name):
    try:
        youtube = build('youtube', 'v3', developerKey="AIzaSyA1_A2NpHWr9IF21D5PV2v787KAufkw-r0")

        search_response = youtube.search().list(
            q=video_name,
            type="video",
            part="id",
            maxResults=1
        ).execute()

        if 'items' in search_response:
            video_id = search_response['items'][0]['id']['videoId']
            return f'https://www.youtube.com/watch?v={video_id}'

    except HttpError as e:
        print(f'An error occurred: {str(e)}')

    return None


# Function to delete temporary files on exit
def delete_temporary_files():
    for file_path in temporary_files:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {str(e)}")

# Register the delete_temporary_files function to be called at exit
atexit.register(delete_temporary_files)

pyt = False
current_dir = os.getcwd()
if pyt == True:
    current_dir = os.getcwd() + "/mysite/"
else:
    current_dir = os.getcwd() + "/Websites/MultiTool"
temp_dir = current_dir + "/backend/"
print(current_dir)
app = Flask(__name__, template_folder= current_dir +'/frontend/html', static_folder= current_dir + '/', static_url_path='/static')


@app.route('/delete_file', methods=['POST'])
def delete_file():
    file_path = request.form['file_path']
    try:
        os.remove(file_path)
        return "File deleted successfully"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tageditor', methods=['GET'])
def tag_editor():
    # Implement your tag editor functionality here
    return render_template('tageditor.html')
@app.route('/ytdown', methods=['GET'])
def yt_down():
    # Implement your tag editor functionality here
    return render_template('ytdown.html')

@app.route('/download', methods=['POST'])
def download():
    video_name_or_url = request.form['video_name_or_url']
    format = request.form['format']
    quality = request.form['quality']

    yt = None

    try:
        # Check if the provided input is a valid YouTube URL
        if "youtube.com" in video_name_or_url or "youtu.be" in video_name_or_url:
            yt = YouTube(video_name_or_url)
            video_name = yt.title  # Get the video title from the YouTube URL
        else:
            video_name = video_name_or_url
            # Search for the video by name using the YouTube Data API
            video_url = search_video_by_name(video_name)
            if video_url:
                yt = YouTube(video_url)
            else:
                return render_template("ytdown.html", error_message=f"Video not found.")

        if format == 'mp4':
            if quality == 'high':
                stream = yt.streams.get_highest_resolution()
            elif quality == 'low':
                stream = yt.streams.get_lowest_resolution()
            else:
                return "Invalid quality option."
        elif format == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
        else:
            return "Invalid format."

        if stream:
            video_url = stream.url
            response = {
                "download_url": video_url,
                "filename": f'{video_name}.{format}'
            }
            return render_template("ytdown.html", success_message="Download successful! Click below to download.", data=response)
        else:
            return render_template("ytdown.html", error_message=f"Video format not available for {format}.")

    except Exception as e:
        return render_template("ytdown.html", error_message=f"An error occurred: {str(e)}")



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3'}

@app.route('/download_zip')
def download_zip():
    zip_file_path = current_dir + '/backend/IntegratedTools.rar'  # Replace with the path to your ZIP file

    return send_file(zip_file_path, as_attachment=True)

@app.route('/edit_tags', methods=['POST'])
def edit_tags():
    title = request.form['title']
    artist = request.form['artist']
    album = request.form['album']
    year = request.form['year']

    audio_file = request.files['audio_file']
    album_cover = request.files['album_cover']

    if audio_file and allowed_file(audio_file.filename):
        try:
            # Save the uploaded audio file to a temporary location
            audio_path = os.path.join(temp_dir, 'audio.mp3')
            audio_file.save(audio_path)
            temporary_files.append(audio_path)  # Keep track of this file for deletion

            # Save the uploaded audio file and album cover
            album_cover_path = os.path.join(temp_dir + '/album_covers', album_cover.filename)
            album_cover.save(album_cover_path)
            temporary_files.append(album_cover_path)  # Keep track of this file for deletion

            # Edit ID3 tags
            audio = ID3(audio_path)

            if title:
                audio.add(TIT2(encoding=3, text=title))

            if artist:
                audio.add(TPE1(encoding=3, text=artist))

            if album:
                audio.add(TALB(encoding=3, text=album))

            if year:
                audio.add(TYER(encoding=3, text=year))
                
            audio.delall("APIC")

            with open(album_cover_path, 'rb') as album_cover_file:
                audio["APIC"] = APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,  # Set type to 3 (Front Cover)
                    desc=u'Front Cover',
                    data=album_cover_file.read()
                )
            audio.save(audio_path)

            print(f"audio_path: {audio_path}")
            return render_template("tageditor.html", success_message="Download successful! Click below to download.")

        except error:
            return render_template("tageditor.html", error_message="An error occurred while editing the tags.")
    else:
        return render_template("tageditor.html", error_message="Invalid file format. Only MP3 files are allowed.")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
