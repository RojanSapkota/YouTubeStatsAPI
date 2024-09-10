from flask import Flask, request, jsonify
import requests
from flask_caching import Cache

app = Flask(__name__)

cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})
cache.init_app(app)

@app.route('/channel', methods=['GET'])
@cache.cached(query_string=True)
def get_channel_info():
    try:
        channel_id = request.args.get('id')

        if not channel_id:
            return jsonify({'error': 'No channel ID provided'}), 400

        url = f"https://yt.lemnoslife.com/noKey/channels?part=snippet,statistics&id={channel_id}"

        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from YouTube API'}), response.status_code

        data = response.json()

        if 'items' not in data or len(data['items']) == 0:
            return jsonify({'error': 'No channel data found'}), 404

        channel_data = data['items'][0]

        snippet = channel_data.get('snippet', {})
        statistics = channel_data.get('statistics', {})

        result = {
            'title': snippet.get('localized', {}).get('title'),
            'description': snippet.get('localized', {}).get('description'),
            'subscribers': statistics.get('subscriberCount')
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    
@app.route('/recentvid', methods=['GET'])
@cache.cached(query_string=True)
def get_recent_video():
    try:
        channel_id = request.args.get('id')

        if not channel_id:
            return jsonify({'error': 'No channel ID provided'}), 400

        url = f"https://yt.lemnoslife.com/noKey/search?part=snippet&channelId={channel_id}&maxResults=1&order=date&type=video"

        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from YouTube API'}), response.status_code

        data = response.json()

        if 'items' not in data or len(data['items']) == 0:
            return jsonify({'error': 'No recent video found'}), 404

        video_id = data['items'][0]['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        return jsonify({'videoUrl': video_url})

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/stats', methods=['GET'])
@cache.cached(query_string=True)
def get_video_stats():
    try:
        video_id = request.args.get('id')

        if not video_id:
            return jsonify({'error': 'No video ID provided'}), 400

        url = f"https://yt.lemnoslife.com/noKey/videos?id={video_id}&part=snippet,contentDetails,statistics,status"

        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data from YouTube API'}), response.status_code

        data = response.json()

        if 'items' not in data or len(data['items']) == 0:
            return jsonify({'error': 'No video data found'}), 404

        video_item = data['items'][0]
        title = video_item['snippet']['title']
        view_count = video_item['statistics']['viewCount']

        return jsonify({'title': title, 'viewCount': view_count})

    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    
@app.route('/transcript', methods=['GET'])
@cache.cached(query_string=True)
def generate_transcript():
    vid_id = request.args.get('id')
    if not vid_id:
        return jsonify({'error': 'No video ID provided'}), 400

    json_data = {
        'video_id': vid_id,
        'format': True,
    }

    try:
        response = requests.post('https://api.kome.ai/api/tools/youtube-transcripts', json=json_data)

        if response.status_code == 200:
            transcript_data = response.json()
            transcript_text = transcript_data.get('transcript', 'No Transcript')
            return jsonify({'transcript': transcript_text})
        else:
            return jsonify({'transcript': 'No Transcript'})

    except requests.RequestException as e:
        return jsonify({'transcript': 'No Transcript'})
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    
def main():
    app.run(debug=True, port=5000)

if __name__ == '__main__':
    main()