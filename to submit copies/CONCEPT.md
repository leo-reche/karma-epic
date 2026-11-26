# The Karma-LLMifier

## The problem

We have many videos, for example talks and interviews. They contain useful information, but it is hard to find. You must watch the whole video, and most AI tools work better with text.

## The idea

A simple website that turns a video into a text file. You can give this file to your favourite AI and ask questions about the video.

## How it works

1. **Upload** your video (usually MP4).
2. **Wait** while the app processes it.
3. **Download** the result. The button is grey until the file is ready.
4. **Ask** your AI about it.

## What you get

A Markdown (`.md`) file with:

- the full transcript (everything people say)
- times, so you can find each part in the video
- a few screenshots of important moments

## Plan

1. Build a Python script that processes one video.
2. Put it on Google Cloud.
3. Connect it to our website, so users can use it online.
