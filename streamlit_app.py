"""

Streamlit application for YouTube Transcript scrapping

"""

import streamlit as st
from pytube import YouTube, Channel
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    YouTubeRequestFailed,
    VideoUnavailable,
    InvalidVideoId,
    TooManyRequests,
    TranscriptsDisabled,
    NoTranscriptAvailable,
    NotTranslatable,
    TranslationLanguageNotAvailable,
    CookiePathInvalid,
    CookiesInvalid,
    FailedToCreateConsentCookie,
    NoTranscriptFound,
)
import scrapetube
import os
import re


def get_transcript_text(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([item["text"] for item in transcript])


def remove_timestamps(srt_text):
    timestamp_pattern = re.compile(
        r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}"
    )
    lines = srt_text.split("\n")
    filtered_lines = [line for line in lines if not timestamp_pattern.match(line)]
    return "\n".join(filtered_lines)


def download_transcript(video_id, output_dir):
    try:
        transcript = get_transcript_text(video_id)
        if transcript:
            cleaned_text = remove_timestamps(transcript)

            with open(
                os.path.join(output_dir, f"{video_id}.txt"), "w", encoding="utf-8"
            ) as file:
                file.write(cleaned_text)
            return True
        else:
            print(f"No English transcript found for video ID {video_id}")
            return False
    except Exception as e:
        print(f"Failed to download transcript for video ID {video_id}: {e}")
        return False


def concatenate_transcripts(output_dir, final_file):
    with open(final_file, "w", encoding="utf-8") as f_out:
        for filename in os.listdir(output_dir):
            if filename.endswith(".txt"):
                with open(
                    os.path.join(output_dir, filename), "r", encoding="utf-8"
                ) as f_in:
                    f_out.write(f_in.read() + "\n\n")


def get_all_video_ids(channel_url):
    videos = scrapetube.get_channel(channel_url=channel_url)
    video_ids = [video["videoId"] for video in videos]
    return video_ids

def clear_transcript_folder(folder_path):
    """Delete all files in the specified folder."""
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                st.error(f"Error deleting {filename}: {e}")
        st.success("All transcript files cleared!")
    else:
        st.warning("Transcript folder does not exist")


st.set_page_config(
    page_title="YouTube Transcript Scrapping", 
    page_icon=":material/thumb_up:", 
    layout="wide"
)

st.title("YouTube Transcript Scrapping")

def main():

    st.subheader("YouTube Transcript Scrapping")

    st.write("Enter the channel URL to download the transcripts - example: https://www.youtube.com/@AdrianaGirdler")
    channel_url = st.text_input("Enter the channel URL")

    output_dir = "transcripts"  # Directory to save transcripts

    final_file = st.text_input("Enter the final file name")

    if st.button("Download Transcripts"):
        if not channel_url:
            st.error("Please enter a channel URL")
            return
    
        else:
            if not final_file:
                final_file = "combined_transcripts.txt"
            else:
                final_file = final_file + ".txt"

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            clear_transcript_folder(output_dir)
            video_ids = get_all_video_ids(channel_url)
            total_videos = len(video_ids)
            st.write(f"Total videos to process: {total_videos}")

            for i, video_id in enumerate(video_ids, 1):
                st.write(f"Processing video {i} of {total_videos} (ID: {video_id})")
                download_transcript(video_id, output_dir)

            st.write("Downloading transcripts completed. Starting concatenation...")
            concatenate_transcripts(output_dir, final_file)
            st.write(f"All transcripts concatenated into {final_file}")

if __name__ == "__main__":
    main()
