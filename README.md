# Spotify Downloader

Used for analyzing playlists from Spotify, where you can view the playlist, its YouTube link, and download all the songs in the playlist as a zip file.

## Project Overview

This project analyzes playlists from Spotify, providing insights such as the number of playlists, the number of songs, and YouTube links for each song. It also offers an option to download all songs.

## Motivation

The motivation behind this project is to provide users with an easy way to analyze their Spotify playlists and access their favorite songs in a convenient format.

## Contribution Guidelines

We welcome contributions! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch and create a pull request.

## Repository Structure

- `techstack/` - Contains tech stack specific README and setup instructions.


## Docker

```bash
docker build -t spotify-downloader:latest .
```

```bash
docker run -p 5000:5000 -p 3000:3000 spotify-downloader:latest
```
