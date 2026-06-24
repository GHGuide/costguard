#!/usr/bin/env python3
"""Assemble the CostGuard master: 14 scenes (de-AI'd graphics + real captures),
each timed to Bella's VO. No shared pipeline needed — pure ffmpeg.

  python3 video/assemble.py            # -> video/out/costguard-demo-v2.mp4

Each scene = its source clip (a rendered graphic, a captured terminal/UI clip, or
the architecture still) fitted to (VO duration + 0.6s pad): held on the last frame
when shorter, trimmed when longer. Audio = that scene's VO, padded to the segment.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SEG = os.path.join(OUT, "_seg")
PAD = 0.6  # tail breath after each VO line

# scene id -> (source path relative to video/, kind)
SRC = {
    "s01_hook":        ("out/scenes/s01-hook.mp4",            "video"),
    "s02_gap":         ("out/scenes/s02-gap.mp4",             "video"),
    "s03_name":        ("out/scenes/s03-name.mp4",            "video"),
    "s04_architecture":("captures/architecture/frame_00001.png", "still"),
    "s05_under_test":  ("captures/architecture/frame_00001.png", "still"),
    "s06_contrast":    ("out/scenes/s06-contrast.mp4",        "video"),
    "s07_verdict":     ("out/scenes/s07-chart.mp4",           "video"),
    "s08_on_uipath":   ("out/scenes/s08-uipath.mp4",          "video"),
    "s09_ledger":      ("captures/dashboard/base.mp4",        "video"),
    "s10_human":       ("out/scenes/s10-human.mp4",           "video"),
    "s11_robust":      ("captures/robust/base.mp4",           "video"),
    "s12_coding_agent":("captures/coding-agent/base.mp4",     "video"),
    "s13_impact":      ("out/scenes/s13-impact.mp4",          "video"),
    "s14_logo":        ("out/scenes/s14-logo.mp4",            "video"),
}
VF = ("scale=1920:1080:force_original_aspect_ratio=decrease,"
      "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#0d1219,setsar=1,fps=30,format=yuv420p")


def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit("ffmpeg failed:\n" + " ".join(args) + "\n" + p.stderr[-1500:])


def main():
    os.makedirs(SEG, exist_ok=True)
    script = json.load(open(os.path.join(HERE, "script", "script.json")))
    durs = {s["id"]: s["duration"] for s in json.load(open(os.path.join(HERE, "vo", "vo.manifest.json")))["scenes"]}

    seg_files, total = [], 0.0
    for i, sc in enumerate(script["scenes"]):
        sid = sc["id"]
        src, kind = SRC[sid]
        src = os.path.join(HERE, src)
        vo = os.path.join(HERE, "vo", sid + ".mp3")
        seg_len = round(durs[sid] + PAD, 3)
        total += seg_len
        out = os.path.join(SEG, f"{i:02d}_{sid}.mp4")
        va = (f"[0:v]{VF},tpad=stop_mode=clone:stop_duration={seg_len}[v];"
              f"[1:a]apad,atrim=0:{seg_len},asetpts=N/SR/TB[a]")
        if kind == "still":
            inp = ["-loop", "1", "-t", str(seg_len), "-i", src, "-i", vo]
            va = (f"[0:v]{VF}[v];[1:a]apad,atrim=0:{seg_len},asetpts=N/SR/TB[a]")
        else:
            inp = ["-i", src, "-i", vo]
        run(["ffmpeg", "-y", "-loglevel", "error", *inp,
             "-filter_complex", va, "-map", "[v]", "-map", "[a]",
             "-t", str(seg_len), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
             "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-ar", "48000", "-ac", "2", out])
        seg_files.append(out)
        print(f"  {sid:18} {seg_len:5.1f}s  <- {os.path.basename(src)}")

    lst = os.path.join(SEG, "concat.txt")
    with open(lst, "w") as fh:
        for s in seg_files:
            fh.write(f"file '{s}'\n")
    master = os.path.join(OUT, "costguard-demo-v2.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", "-movflags", "+faststart", master])
    print(f"\nmaster: {master}  ({total:.1f}s ≈ {int(total//60)}:{int(total%60):02d})")


if __name__ == "__main__":
    main()
