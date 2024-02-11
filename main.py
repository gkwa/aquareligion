import json
import os

import jinja2
import youtube_transcript_api


def fetch_youtube_transcript(video_id, json_output_file):
    if os.path.exists(json_output_file):
        with open(json_output_file, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
    else:
        try:
            transcript = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(
                video_id, languages=["en"]
            )
            data = {
                "video_id": video_id,
                "transcript": transcript,
            }
            with open(json_output_file, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=2)
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return None
    
    return data


def convert_to_txt(transcript, output_file):
    with open(output_file, "w", encoding="utf-8") as txt_file:
        for line in transcript:
            txt_file.write(f"{line['text']}\n")


def wrap_first_word_with_anchor(text, start_time, video_id):
    first_word, *remaining_words = text.split(" ", 1)
    anchor_tag = f'<a target="_blank" href="https://www.youtube.com/watch?v={video_id}&t={start_time}s">{first_word}</a>'
    if remaining_words:
        return f"{anchor_tag} {''.join(remaining_words)}"
    else:
        return anchor_tag


def convert_to_html(transcript, output_file, video_id):
    template_str = """
    <html>
    <head>
        <title>Transcript</title>
        <script>
            function openVideoAtTimestamp(timestamp) {
                var url = "https://www.youtube.com/watch?v={{ video_id }}&t=" + timestamp + "s";
                window.open(url, '_blank');
            }
        </script>
    </head>
    <body>
        {% for line in transcript %}
            <span onclick="openVideoAtTimestamp({{ line['start'] }})">{{ line['text'] }}</span><br>
        {%- endfor %}
    </body>
    </html>
    """
    template = jinja2.Template(template_str)
    html_content = template.render(transcript=transcript, video_id=video_id)

    with open(output_file, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)


def main():
    video_id = "RBYJTop1e-g"
    json_output_file = f"{video_id}_transcript.json"
    data = fetch_youtube_transcript(video_id, json_output_file)
    transcript = data.get("transcript")
    if transcript:
        txt_output_file = f"{video_id}_transcript.txt"
        html_output_file = f"{video_id}_transcript.html"

        convert_to_txt(transcript, txt_output_file)
        convert_to_html(transcript, html_output_file, video_id=video_id)
        print("Transcript fetched successfully and saved to files.")


if __name__ == "__main__":
    main()
