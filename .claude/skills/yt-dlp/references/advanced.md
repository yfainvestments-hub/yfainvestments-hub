# yt-dlp advanced reference

Detailed syntax for format selection, format sorting, output templates,
post-processing, and config files. Read the section you need — you rarely need
all of it.

## Table of contents

1. [Format selection (`-f`)](#format-selection--f)
2. [Format sorting (`-S` / `--format-sort`)](#format-sorting--s--format-sort)
3. [Inspecting formats (`-F`)](#inspecting-formats--f)
4. [Output templates (`-o`)](#output-templates--o)
5. [Selecting which items to download](#selecting-which-items-to-download)
6. [Post-processing](#post-processing)
7. [Network, throttling, and reliability](#network-throttling-and-reliability)
8. [Configuration files](#configuration-files)
9. [Extractor arguments](#extractor-arguments)

---

## Format selection (`-f`)

`-f`/`--format` asks for an **exact** selection and fails if it can't be met.
Use it when the user needs a precise stream; use `-S` (next section) when they
express a preference.

**Basic selectors**
- `best` / `worst` — best/worst combined (video+audio) file that is a single download
- `bestvideo` / `worstvideo` — best/worst video-only stream
- `bestaudio` / `worstaudio` — best/worst audio-only stream
- `bv*` / `ba*` — best video/audio that *may* also contain the other stream
- A literal `format_id` from `-F`, e.g. `137`
- `all` — every format; `mergeall` — merge everything into one file

**Merging** with `+` downloads separate streams and muxes them (needs ffmpeg):
```
-f "bestvideo+bestaudio"
```

**Fallback chain** with `/` tries left-to-right until one succeeds:
```
-f "bestvideo+bestaudio/best"
```
(Download best separate streams and merge; if that's impossible, take the best
single file.)

**Filters** in `[...]` narrow a selector. Combine freely:
```
-f "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"
```
- Numeric fields (comparisons `< <= = != >= >`): `height`, `width`, `tbr`,
  `abr`, `vbr`, `asr`, `fps`, `filesize`, `filesize_approx`
- String fields (`=`, `!=`, and `^=` starts / `$=` ends / `*=` contains, plus
  `~=` regex): `ext`, `acodec`, `vcodec`, `container`, `protocol`,
  `format_id`, `language`, `dynamic_range`
- Combine with `[a][b]` (AND). Example: `[height<=720][vcodec^=avc1]`

**Grouping** with parentheses (yt-dlp extension over youtube-dl):
```
-f "(mp4,webm)[height<480]"
```

## Format sorting (`-S` / `--format-sort`)

`-S` changes *which* format `best` resolves to, expressing preferences that
degrade gracefully instead of failing. Often the better tool for
resolution/codec/size asks.

Comma-separated keys, highest priority first. Common keys:
- `res` — resolution (use `res:1080` to target a value, closest-not-exceeding)
- `fps`, `hdr`, `vcodec`, `acodec`, `ext`, `filesize`, `br` (bitrate),
  `asr`, `channels`, `quality`
- `codec:h264` or `vcodec:h264` — prefer a specific codec
- `size`, `+size` — prefer larger; a leading `+` reverses to prefer smaller
- Append `~value` to target: `br~1000` prefers ~1000K bitrate

Examples:
```
-S "res:720"                     # closest to 720p, best available otherwise
-S "res:1080,vcodec:h264,acodec:aac"   # 1080p, H.264/AAC for compatibility
-S "+size,+br,+res"              # smallest file (reverse each dimension)
-S "hdr,res,fps"                 # prefer HDR, then higher res, then higher fps
```
`-S` pairs naturally with a permissive `-f` (or none), e.g.
`-f "bv*+ba/b" -S "res:720"`.

## Inspecting formats (`-F`)

```
yt-dlp -F "URL"
```
Lists every available format: `ID`, `EXT`, resolution, `FPS`, codecs, bitrate,
filesize, and notes (e.g. "video only", "audio only", storyboard). Run this
first when a `-f` selection fails or when you need a specific stream. Related:
- `--list-subs` — available subtitle languages/formats
- `--list-thumbnails` — available thumbnails

## Output templates (`-o`)

Syntax: `%(FIELD)s`, with optional Python string formatting like `%(FIELD)05d`.
Prefix with a type for per-file-type templates: `-o "thumbnail:thumbs/%(id)s.%(ext)s"`.

**Frequently used fields**
- `id`, `title`, `fulltitle`, `ext`, `url`, `webpage_url`
- `uploader`, `uploader_id`, `channel`, `channel_id`
- `upload_date` (YYYYMMDD), `timestamp`, `release_date`, `duration`
- `view_count`, `like_count`, `resolution`, `fps`, `vcodec`, `acodec`
- Playlist: `playlist`, `playlist_title`, `playlist_id`, `playlist_index`,
  `playlist_count`, `n_entries`
- `autonumber` — running counter across the whole run
- `chapter`, `chapter_number`, `section_title` (with `--split-chapters` / sections)

**Object traversal & slicing** (Python-like):
- `%(tags.0)s` — first tag; `%(formats.:2)j` — first two formats as JSON
- `%(id.3:7)s` — characters 3–7 of the id

**Arithmetic**: `%(playlist_index+10)03d`, `%(duration-60)d`

**Date/time reformatting** with `>`:
```
%(upload_date>%Y-%m-%d)s      -> 2023-11-04
%(timestamp>%Y/%m)s
```

**Alternatives / defaults** with `,` and `|`:
```
%(release_date>%Y,upload_date>%Y|Unknown)s   # first that exists, else Unknown
%(uploader|Unknown Uploader)s
```

**Type/format conversions** (the trailing letter):
`d/i/o/x/X` integers · `s` string · `j` JSON · `h` HTML-escaped ·
`q` shell-quoted · `S` sanitized-for-filename · `B` bytes w/ SI suffix ·
`l` comma-separated list · `#j` pretty JSON

**Useful flags alongside `-o`:**
- `--restrict-filenames` — ASCII only, no spaces/special chars (script-safe)
- `-P "home:~/Videos" -P "temp:/tmp/ytdl"` — separate final vs. temp dirs
- `--windows-filenames` — force Windows-safe names on any OS
- `--trim-filenames 200` — cap length
- `-o "-"` — stream to stdout (pipe to a player/processor)

Examples:
```
-o "%(title)s [%(id)s].%(ext)s"
-o "%(uploader)s/%(upload_date>%Y-%m-%d)s - %(title)s.%(ext)s"
-o "%(playlist_title)s/%(playlist_index)03d - %(title)s.%(ext)s"
-o "chapter:%(title)s/%(section_number)02d - %(section_title)s.%(ext)s"
```

## Selecting which items to download

- `--playlist-items 1:5,8,10:12,-1` — ranges, singletons, negatives, `::step`
- `--no-playlist` / `--yes-playlist` — force single vs. full playlist
- `--max-downloads N` — stop after N files
- `--break-on-existing` — stop when hitting an archived video (with `--download-archive`)
- `--dateafter 20240101 --datebefore 20241231` — date window
  (relative supported: `--dateafter "today-2weeks"`)
- `--match-filters "view_count>?1000 & duration<600"` — filter on metadata;
  `--match-filters "!is_live"` to skip livestreams
- `--download-sections "*10:00-12:30"` — time range (repeatable; regex on
  chapter names with `--download-sections "intro"`)

## Post-processing

All require ffmpeg unless noted.
- `-x --audio-format mp3 --audio-quality 0` — extract audio (VBR 0 = best)
- `--remux-video mkv` — change container without re-encoding (fast, lossless)
- `--recode-video mp4` — re-encode (slow, lossy) when remux can't produce the container
- `--embed-subs`, `--embed-thumbnail`, `--embed-metadata`, `--embed-chapters`
- `--split-chapters` — one file per internal chapter
- `--sponsorblock-remove sponsor,selfpromo,intro,outro`
  / `--sponsorblock-mark all`
- `--convert-subs srt` — normalize subtitle format
- `--exec "cmd {}"` — run a command per finished file (`{}` = filepath)
- `--keep-video` — keep the original when post-processing produces a new file

## Network, throttling, and reliability

- `--limit-rate 2M` — cap bandwidth
- `--sleep-requests 1 --min-sleep-interval 3 --max-sleep-interval 8` — be polite
- `--retries infinite --fragment-retries infinite` — survive flaky connections
- `--concurrent-fragments 4` (`-N 4`) — parallel fragment download (faster DASH/HLS)
- `--proxy socks5://127.0.0.1:1080`
- `--cookies-from-browser BROWSER[:PROFILE]` or `--cookies FILE` — auth/session
- `--user-agent`, `--add-headers "Header:Value"` — custom request headers
- `--force-ipv4` (`-4`) — work around some IPv6 blocks

## Configuration files

Put commonly used options in `yt-dlp.conf`, one option per line (comments with
`#`). yt-dlp reads (in order) a portable config beside the binary, `~/.config/
yt-dlp/config`, `~/yt-dlp.conf`, and system paths. Example:
```
# ~/.config/yt-dlp/config
-o ~/Videos/%(uploader)s/%(title)s [%(id)s].%(ext)s
-S res:1080,vcodec:h264
--embed-metadata
--embed-thumbnail
--sponsorblock-mark all
```
Use `--ignore-config` to run a one-off command without these defaults, or
`--config-locations PATH` to load a specific file.

## Extractor arguments

Some sites accept extra tuning via `--extractor-args "KEY:subkey=val"`. Most
useful for YouTube:
```
--extractor-args "youtube:player_client=default,web_safari"
--extractor-args "youtube:skip=dash,hls"          # try alternate manifests
--extractor-args "youtube:lang=en"                 # metadata language
```
Reach for these only when default extraction fails or the maintainers/issue
tracker recommend a specific workaround — they change over time.
