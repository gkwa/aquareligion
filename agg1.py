import json
import textwrap

def main():
    with open("RBYJTop1e-g_transcript.json") as f:
        records = json.load(f)

    sentences = aggregate_records_into_sentences(records)
    formatted_text = reformat_sentences(sentences)
    print(formatted_text)

def aggregate_records_into_sentences(records):
    sentences = [record["text"] for record in records]
    return split_long_sentences(sentences)

def split_long_sentences(sentences):
    result = []
    current_sentence = ""

    for sentence in sentences:
        current_sentence += " " + sentence
        if "." in sentence:
            result.append(current_sentence.strip())
            current_sentence = ""

    return result

def reformat_sentences(sentences):
    wrapped_sentences = [textwrap.fill(sentence, width=60) for sentence in sentences]
    formatted_text = "\n\n".join(wrapped_sentences)
    return formatted_text

if __name__ == "__main__":
    main()
