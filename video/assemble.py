#!/usr/bin/env python3
"""Assemble the CostGuard master (de-AI pass): scenes timed to Bella's VO, with
continuous motion (graphics breathe; the architecture still gets Ken Burns), soft
dip transitions, and burned word-timed captions.

  python3 video/assemble.py        # -> video/out/costguard-demo-v2.mp4
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SEG = os.path.join(OUT, "_seg")
PAD = 0.25
FADE = 0.12
DIP = "#0d1219"

SRC = {
    "s01_hook":        ("out/scenes/s01-hook.mp4",            "video"),
    "s02_gap":         ("out/scenes/s02-gap.mp4",             "video"),
    "s03_name":        ("out/scenes/s03-name.mp4",            "video"),
    "s03b_explain":    ("out/scenes/s03b-explain.mp4",        "video"),
    "s04_architecture":("out/scenes/s04-architecture.mp4",       "video"),
    "s05_under_test":  ("out/scenes/s04-architecture.mp4",       "video"),
    "s06_contrast":    ("out/scenes/s06-contrast.mp4",        "video"),
    "s07_verdict":     ("out/scenes/s07-chart.mp4",           "video"),
    "s08_on_uipath":   ("out/scenes/s08-uipath.mp4",          "video"),
    "s09_ledger":      ("captures/dashboard/base.mp4",        "video"),
    "s10_human":       ("out/scenes/s10-human.mp4",           "video"),
    "s11_robust":      ("captures/robust/base.mp4",           "video"),
    "s12_coding_agent":("captures/coding-agent/base.mp4",     "video"),
    "s13_impact":      ("out/scenes/s13-impact.mp4",          "video"),
    "s13b_install":    ("out/scenes/s13b-install.mp4",        "video"),
    "s14_logo":        ("out/scenes/s14-logo.mp4",            "video"),
}
FIT = ("scale=1920:1080:force_original_aspect_ratio=decrease,"
       "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=" + DIP + ",setsar=1,fps=30")


def run(args, cwd=None, soft=False):
    p = subprocess.run(args, capture_output=True, text=True, cwd=cwd)
    if p.returncode != 0:
        if soft:
            return False
        sys.exit("ffmpeg failed:\n" + " ".join(args[:9]) + " ...\n" + p.stderr[-1600:])
    return True


def fades(seg_len):
    return f"fade=t=in:st=0:d={FADE}:color={DIP},fade=t=out:st={seg_len-FADE:.3f}:d={FADE}:color={DIP}"


def vfilter(kind, seg_len):
    nf = int(round(seg_len * 30)) + 2
    if kind.startswith("still"):
        # Ken Burns: fit on the diagram's own light mat, then slow zoom (vary dir)
        base = "scale=-1:980,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#eef0f2,setsar=1"
        z = (f"zoompan=z='min(1.0+0.00060*on,1.10)'" if kind == "still_in"
             else f"zoompan=z='max(1.10-0.00060*on,1.0)'")
        zp = f"{z}:d={nf}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
        return f"[0:v]{base},{zp},format=yuv420p,{fades(seg_len)}[v]"
    return f"[0:v]{FIT},tpad=stop_mode=clone:stop_duration={seg_len},format=yuv420p,{fades(seg_len)}[v]"


def phrases(words, max_w=6, max_c=42):
    out, cur = [], []
    for w in words:
        cur.append(w)
        txt = " ".join(x["word"] for x in cur)
        end_punct = w["word"][-1:] in ".!?—:" or w["word"][-1:] == ","
        if len(cur) >= max_w or len(txt) >= max_c or (end_punct and len(cur) >= 3):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def main():
    os.makedirs(SEG, exist_ok=True)
    script = json.load(open(os.path.join(HERE, "script", "script.json")))
    man = {s["id"]: s for s in json.load(open(os.path.join(HERE, "vo", "vo.manifest.json")))["scenes"]}

    seg_files, caps, clock = [], [], 0.0
    for i, sc in enumerate(script["scenes"]):
        sid = sc["id"]
        src, kind = SRC[sid]
        src = os.path.join(HERE, src)
        vo = os.path.join(HERE, "vo", sid + ".mp3")
        seg_len = round(man[sid]["duration"] + PAD, 3)
        out = os.path.join(SEG, f"{i:02d}_{sid}.mp4")
        vf = vfilter(kind, seg_len)
        af = f"[1:a]apad,atrim=0:{seg_len},asetpts=N/SR/TB[a]"
        inp = (["-loop", "1", "-t", str(seg_len), "-i", src, "-i", vo]
               if kind.startswith("still") else ["-i", src, "-i", vo])
        if not (os.path.exists(out) and "--force" not in sys.argv):
            run(["ffmpeg", "-y", "-loglevel", "error", *inp, "-filter_complex", f"{vf};{af}",
                 "-map", "[v]", "-map", "[a]", "-t", str(seg_len), "-c:v", "libx264", "-preset",
                 "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac",
                 "-ar", "48000", "-ac", "2", out])
        # captions for this scene, offset to absolute time
        for ph in phrases(man[sid].get("words", [])):
            s = clock + ph[0]["start"]
            e = clock + ph[-1]["end"]
            txt = " ".join(w["word"] for w in ph).replace("\n", " ")
            caps.append((s, min(e, clock + seg_len), txt))
        seg_files.append(out)
        clock += seg_len
        print(f"  {sid:18} {seg_len:5.1f}s  ({kind})")

    lst = os.path.join(SEG, "concat.txt")
    open(lst, "w").write("".join(f"file '{s}'\n" for s in seg_files))
    nocap = os.path.join(SEG, "_master_nocap.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", nocap])

    # Caption track: render an alpha ProRes mov from the events and overlay it.
    # (This ffmpeg has no text/libass filters, but it does have prores + overlay.)
    total_frames = int(round(clock * 30))
    capjson = os.path.join(SEG, "captions.json")
    json.dump({"events": [{"start": round(s, 3), "end": round(e, 3), "text": t} for s, e, t in caps],
               "durationInFrames": total_frames}, open(capjson, "w"))
    caps_mov = os.path.join(SEG, "caps.mov")
    master = os.path.join(OUT, "costguard-demo-v2.mp4")
    # alpha ProRes needs PNG intermediate frames + an alpha pixel format
    rendered = run(["npx", "remotion", "render", "Captions", caps_mov,
                    "--codec=prores", "--prores-profile=4444",
                    "--pixel-format=yuva444p10le", "--image-format=png",
                    f"--props={capjson}"],
                   cwd=os.path.join(HERE, "chart"), soft=True)
    if rendered and os.path.exists(caps_mov):
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", nocap, "-i", caps_mov,
             "-filter_complex", "[0:v][1:v]overlay=format=auto[v]", "-map", "[v]", "-map", "0:a",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
             "-c:a", "copy", "-movflags", "+faststart", master])
        tag = "+ captions"
    else:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", nocap, "-c", "copy",
             "-movflags", "+faststart", master])
        tag = "no captions (caption render failed)"
    print(f"\nmaster: {master}  ({clock:.1f}s ≈ {int(clock//60)}:{int(clock%60):02d})  {tag}")


if __name__ == "__main__":
    main()
