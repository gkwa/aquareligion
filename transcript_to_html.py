import argparse
import dataclasses
import json
import pathlib
import textwrap
import typing

import jinja2
import youtube_transcript_api


@dataclasses.dataclass
class TranscriptSentence:
    text: str
    starts: typing.List[float]

    def __str__(self):
        t1 = ",".join([str(x) for x in self.starts])
        t2 = self.text
        a = t1 + " " + t2
        return textwrap.fill(a, width=60)


@dataclasses.dataclass
class TranscriptSentences:
    sentences: typing.List[TranscriptSentence]
    video_id: typing.Optional[str] = None

    def as_HTML(self):
        s = []
        for sentence in self.sentences:
            obj = {}
            words = sentence.text.split()
            obj["first_word"] = "" if len(words) == 0 else words[0]
            obj["timestamp"] = 0 if len(sentence.starts) == 0 else sentence.starts[0]
            obj["remaining_text"] = " ".join(words[1:])
            s.append({"obj": obj})

        template_loader = jinja2.FileSystemLoader(searchpath="./")
        env = jinja2.Environment(loader=template_loader)
        template = env.get_template("html.tmpl")
        return template.render(sentences=s, video_id=self.video_id)


def aggregate_sentences(data):
    sentences = []
    current_sentence = ""
    current_starts = []
    for record in data["transcript"]:
        text = record.get("text")
        start = record.get("start")
        if text:
            current_sentence += " " + text
            current_starts.append(start)
            if text.endswith("."):
                sentences.append(
                    TranscriptSentence(
                        text=current_sentence.strip(), starts=current_starts.copy()
                    )
                )
                current_sentence = ""
                current_starts = []
    return sentences


def fetch_youtube_transcript(video_id, json_output_file):
    if pathlib.Path(json_output_file).exists():
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


def main():
    parser = argparse.ArgumentParser(
        description="Convert json ytb transcript into html"
    )
    parser.add_argument(
        "--video-id",
        default="RBYJTop1e-g",
        help="The video ID of the YouTube video",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="write output to a file",
    )

    args = parser.parse_args()

    transcript_json_path = f"{args.video_id}_transcript.json"
    transcript_html_output_path = (
        args.output if args.output else f"{args.video_id}_transcript.html"
    )
    data = fetch_youtube_transcript(args.video_id, transcript_json_path)

    with open(transcript_json_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    sentences = aggregate_sentences(data)
    sentences = TranscriptSentences(sentences)
    sentences.video_id = data["video_id"]

    pathlib.Path(transcript_html_output_path).write_text(sentences.as_HTML())


if __name__ == "__main__":
    main()
