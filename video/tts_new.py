#!/usr/bin/env python3
"""Generate Bella VO for the two new scenes via ElevenLabs (with word timings for
captions). Key is read from the environment / .env and never printed.

  python3 video/tts_new.py
"""
import base64, json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = "hpp4J3VqNfWAUOO0d1Us"  # Bella
MODEL = "eleven_multilingual_v2"
SETTINGS = {"stability": 0.5, "similarity_boost": 0.8, "style": 0, "use_speaker_boost": True, "speed": 0.96}

NEW = [
    ("s03c_killer",
     "Watch. The new version passes every correctness test you have. Extraction, schema, "
     "accuracy, QA, all green. It would ship. CostGuard blocks it anyway: seven times the "
     "cost, for the exact same answers."),
]


def api_key() -> str:
    k = os.environ.get("ELEVENLABS_API_KEY")
    if k:
        return k.strip()
    env = os.path.join(HERE, "..", ".env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.strip().startswith("ELEVENLABS_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("ELEVENLABS_API_KEY not found in env or .env")


def words_from_alignment(al: dict):
    chars = al["characters"]
    st = al["character_start_times_seconds"]
    en = al["character_end_times_seconds"]
    words, cur, cs = [], "", None
    for c, a, b in zip(chars, st, en):
        if c == " ":
            if cur:
                words.append({"word": cur, "start": round(cs, 3), "end": round(prev_end, 3)})
                cur = ""
            continue
        if not cur:
            cs = a
        cur += c
        prev_end = b
    if cur:
        words.append({"word": cur, "start": round(cs, 3), "end": round(prev_end, 3)})
    return words


def main():
    key = api_key()
    manifest_path = os.path.join(HERE, "vo", "vo.manifest.json")
    manifest = json.load(open(manifest_path))
    existing = {s["id"] for s in manifest["scenes"]}

    for sid, text in NEW:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps"
        body = json.dumps({"text": text, "model_id": MODEL, "voice_settings": SETTINGS}).encode()
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"xi-api-key": key, "Content-Type": "application/json"})
        try:
            resp = json.load(urllib.request.urlopen(req, timeout=120))
        except urllib.error.HTTPError as e:
            sys.exit(f"{sid}: HTTP {e.code} — {e.read()[:300].decode(errors='replace')}")
        mp3 = os.path.join(HERE, "vo", f"{sid}.mp3")
        with open(mp3, "wb") as fh:
            fh.write(base64.b64decode(resp["audio_base64"]))
        words = words_from_alignment(resp["alignment"])
        dur = round(resp["alignment"]["character_end_times_seconds"][-1], 3)
        scene = {"id": sid, "mp3": f"{sid}.mp3", "duration": dur, "words": words}
        manifest["scenes"] = [s for s in manifest["scenes"] if s["id"] != sid] + [scene]
        print(f"  {sid}: {dur:.2f}s, {len(words)} words -> vo/{sid}.mp3")

    json.dump(manifest, open(manifest_path, "w"), indent=2)
    print("manifest updated")


if __name__ == "__main__":
    main()
