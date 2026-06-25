#!/usr/bin/env python3
"""Mix a subtle synthesized pad under the master and promote to canonical.

  python3 video/add_music.py            # out/costguard-demo-v2.mp4 -> out/costguard-demo.mp4 (+ yt + thumbnail)

The bed is a warm A-major pad (110/164.81/220/277.18 Hz), low-passed and at -25 dB
so it's felt, not heard — and royalty-free by construction (pure synthesis). Music
is a taste call; if you'd rather ship dry, the captionless/musicless master is
out/costguard-demo-v2.mp4.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SRC = os.path.join(OUT, "costguard-demo-v2.mp4")
MASTER = os.path.join(OUT, "costguard-demo.mp4")
YT = os.path.join(OUT, "costguard-demo-yt.mp4")
THUMB = os.path.join(OUT, "thumbnail.png")


def dur(path):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", path], text=True).strip())


def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("ffmpeg failed:\n" + p.stderr[-1200:])


def main():
    d = dur(SRC)
    outfade = round(d - 4.2, 2)
    bed = (
        "[1][2][3][4]amix=inputs=4:weights='1.0 0.7 0.55 0.4':normalize=0,"
        "lowpass=f=680,tremolo=f=0.1:d=0.5,aecho=0.8:0.6:50:0.2,volume=-25dB,"
        f"afade=t=in:d=3,afade=t=out:st={outfade}:d=4.2[bed];"
        "[0:a][bed]amix=inputs=2:weights='1.0 1.0':normalize=0:duration=first[a]")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", SRC,
         "-f", "lavfi", "-i", "sine=110", "-f", "lavfi", "-i", "sine=164.81",
         "-f", "lavfi", "-i", "sine=220", "-f", "lavfi", "-i", "sine=277.18",
         "-filter_complex", bed, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", MASTER])
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", MASTER, "-c", "copy",
         "-movflags", "+faststart", YT])
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "80", "-i", MASTER,
         "-frames:v", "1", THUMB])
    print(f"canonical: {MASTER}  ({int(d//60)}:{int(d%60):02d}, +pad)\n  + {YT}\n  + {THUMB}")


if __name__ == "__main__":
    main()
