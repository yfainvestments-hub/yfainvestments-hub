---
name: yt-dlp
description: >-
  Download video or audio from YouTube and 1000+ other sites using the yt-dlp
  command-line tool. Use this skill whenever the user wants to download,
  save, rip, grab, or archive a video, a playlist, a channel, a livestream,
  or the audio/subtitles/thumbnail from any online video URL — including
  "download this YouTube video", "get the mp3 from this", "save this playlist",
  "extract audio", "download subtitles", "rip this podcast", or when a
  video URL (YouTube, Vimeo, Twitch, SoundCloud, TikTok, Twitter/X, etc.)
  appears alongside a request to fetch its media. Covers format/quality
  selection, audio extraction, subtitles, playlists, cookies for private or
  age-restricted content, SponsorBlock, download archives, and troubleshooting.
---

# yt-dlp

yt-dlp is a feature-rich command-line downloader for YouTube and 1000+ other
sites. It is the actively maintained successor to youtube-dl, with the same
core syntax plus many extra features.

## Before you start: two dependencies

1. **yt-dlp itself.** Check it exists with `yt-dlp --version`. yt-dlp changes
   fast because sites change fast — if a download fails with an extractor
   error, updating is the first fix (see Troubleshooting). Install/update:
   - `pip install -U yt-dlp` (or `python3 -m pip install -U "yt-dlp[default]"`)
   - Standalone binary users: `yt-dlp -U`
2. **ffmpeg + ffprobe.** Required for merging separate video+audio streams
   (the norm for high-quality YouTube), for `-x` audio extraction, and for any
   remux/recode/embed post-processing. Check with `ffmpeg -version`. Without
   it, yt-dlp is limited to whatever single pre-merged file a site offers,
   usually capped at 720p on YouTube. Install via the system package manager
   (`apt install ffmpeg`, `brew install ffmpeg`, etc.). Note: the PyPI
   package named `ffmpeg` is **not** the binary — install the real ffmpeg.

## Core command shape

```
yt-dlp [OPTIONS] URL [URL...]
```

Multiple URLs are allowed. Wrap URLs in quotes — YouTube URLs frequently
contain `&`, `?`, and other shell-significant characters.

## Recipes for the common asks

Reach for the recipe that matches the user's intent, then adjust. Prefer
showing the user the exact command you ran.

**Best-quality video (the sensible default).**
```
yt-dlp "URL"
```
yt-dlp's default already picks the best video+audio and merges them. Only
add an explicit `-f` when the user wants something specific.

**Audio only, as MP3.** The most common non-default request.
```
yt-dlp -x --audio-format mp3 --audio-quality 0 "URL"
```
`-x` extracts audio, `--audio-quality 0` is best VBR. For a lossless/native
grab that avoids re-encoding, use `-f bestaudio` and let the container be
whatever the site served (often `.m4a`/`.opus`). Preset shortcut: `-t mp3`.

**A specific resolution, e.g. 1080p.**
```
yt-dlp -S "res:1080" "URL"
```
`-S` (format-sort) is more robust than a rigid `-f` filter: it asks for
"as close to 1080p as possible, best available otherwise" instead of failing
when an exact match is absent. Use `-S "res:1080,vcodec:h264"` to also prefer
an H.264 codec for maximum compatibility.

**A whole playlist or channel.**
```
yt-dlp -o "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s" "PLAYLIST_URL"
```
Passing a channel/playlist URL downloads every entry by default. Use
`--playlist-items 1:10` to take a subset, or `--no-playlist` to grab only the
single video when the URL points at one item inside a playlist.

**Subtitles.**
```
yt-dlp --write-subs --write-auto-subs --sub-langs "en.*" --embed-subs "URL"
```
`--write-subs` gets human subs, `--write-auto-subs` adds YouTube's
auto-generated captions, `--embed-subs` bakes them into the video container
(mp4/mkv/webm). Drop `--embed-subs` to keep them as separate `.srt`/`.vtt`
files; add `--convert-subs srt` to normalize the format.

**Just the thumbnail / metadata, no video.**
```
yt-dlp --skip-download --write-thumbnail --write-info-json "URL"
```

**Skip sponsor segments (SponsorBlock).**
```
yt-dlp --sponsorblock-remove sponsor,selfpromo "URL"
```
Use `--sponsorblock-mark all` to keep segments but add chapter markers.

**Re-runnable archive (don't re-download what you already have).**
```
yt-dlp --download-archive archive.txt "CHANNEL_URL"
```
Records each downloaded video's ID; on the next run those are skipped. Ideal
for keeping a channel or playlist mirrored over time.

**A clip / time range of a long video.**
```
yt-dlp --download-sections "*00:10:00-00:12:30" "URL"
```

**Private, members-only, or age-restricted content.** These need your login.
Prefer browser cookies:
```
yt-dlp --cookies-from-browser chrome "URL"
```
or an exported Netscape-format cookie file with `--cookies cookies.txt`. Only
do this for the user's own authenticated access — never to bypass paywalls or
access-control on accounts that aren't theirs.

## Format selection, briefly

- Let the default win when the user just wants "the video." It already does
  `bestvideo*+bestaudio/best`.
- Prefer **`-S`/`--format-sort`** ("prefer this, fall back gracefully") over
  **`-f`** exact filters ("this exact thing or fail") whenever the user's ask
  is about a *preference* like resolution, codec, or filesize.
- `-F "URL"` (`--list-formats`) lists every available stream with its
  `format_id`, resolution, codec, and size. Run it first whenever you're
  unsure what a site offers or a specific `-f` selection failed.

The full format-selection grammar (filters like `[height<=720]`, operators,
merging with `+`, sort keys) and the complete output-template field/conversion
reference live in **`references/advanced.md`**. Read it before constructing
anything beyond the recipes above — the syntax has sharp edges (e.g. the
difference between `-f` and `-S`, and template arithmetic/date formatting).

## Output filenames

Control naming with `-o` and template fields like `%(title)s`, `%(id)s`,
`%(ext)s`, `%(uploader)s`, `%(upload_date)s`, `%(playlist_index)s`. Example:
```
yt-dlp -o "%(uploader)s/%(upload_date>%Y-%m-%d)s - %(title)s [%(id)s].%(ext)s" "URL"
```
Add `--restrict-filenames` for ASCII-only, shell-safe names when the output
feeds another script. See `references/advanced.md` for every field.

## Troubleshooting

- **`ERROR: unable to extract ...` / `Unsupported URL` / signature errors on
  a site that used to work** → the extractor is stale. Update first:
  `pip install -U yt-dlp` (or `yt-dlp -U`). This resolves the large majority
  of sudden failures, since sites break extractors regularly.
- **HTTP 403 / "Sign in to confirm you're not a bot" / rate limiting** → the
  site wants a session. Add `--cookies-from-browser <browser>`. To be gentle
  on the server, add `--sleep-requests 1 --limit-rate 2M` and consider
  `--retries infinite`.
- **Only 720p available / video and audio came as separate files** → ffmpeg
  is missing or not on PATH. Install it; yt-dlp merges automatically once it's
  present.
- **YouTube needs a JS runtime** → recent yt-dlp may require deno/node/bun for
  full YouTube support; install one if prompted.
- **Diagnosing anything** → re-run with `-v` (verbose) and read the traceback;
  it usually names the exact cause. `--simulate` (or `-j` for JSON) inspects
  what *would* be downloaded without fetching.

## A note on responsible use

Download content the user is entitled to: their own uploads, openly available
media, or content they have rights/permission to save. Don't use this skill to
circumvent paywalls, DRM, or access controls, or to redistribute others' work
in violation of its license or terms. When a request is clearly for personal
access to public or owned content, just help.
