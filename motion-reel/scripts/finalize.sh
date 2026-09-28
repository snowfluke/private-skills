#!/bin/sh
# Mux the rendered picture with the loop-exact score, and make a 3x file for players that stutter on restart.
#   sh tools/finalize.sh out/render.mp4 public/score.wav out/reel
# Writes out/reel.mp4 and out/reel-x3.mp4. The audio is cut to the video length, so both wrap together.
set -e
VID="$1"; WAV="$2"; OUT="$3"
DUR=$(ffprobe -v error -select_streams v -show_entries stream=duration -of default=nw=1:nk=1 "$VID" | head -1)
ffmpeg -y -loglevel error -i "$VID" -i "$WAV" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -t "$DUR" -movflags +faststart "$OUT.mp4"
printf "file '%s'\n" "$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT").mp4" "$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT").mp4" "$(cd "$(dirname "$OUT")" && pwd)/$(basename "$OUT").mp4" > "$OUT.x3.txt"
DUR3=$(python3 -c "print(round(3 * $DUR, 6))")
ffmpeg -y -loglevel error -f concat -safe 0 -i "$OUT.x3.txt" -stream_loop 2 -i "$WAV" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -t "$DUR3" -movflags +faststart "$OUT-x3.mp4"
rm "$OUT.x3.txt"
for f in "$OUT.mp4" "$OUT-x3.mp4"; do printf "%s  " "$f"; ffprobe -v error -show_entries stream=codec_type,duration -of compact "$f" | tr "\n" " "; echo; done
