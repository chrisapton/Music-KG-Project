import json
import time
import logging
import tempfile
import subprocess
import os
import requests
from dotenv import load_dotenv
load_dotenv()

# ── logging ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("MusicKG")

# ── API headers ─────────────────────────────────────
MB_HEADERS    = {"User-Agent": "MusicKG/0.1 (you@example.com)"}
DEEZER_HEADERS = {"User-Agent": "MusicKG/0.1 (you@example.com)"}


# ── Deezer helpers ──────────────────────────────────
def search_deezer_preview(artist, title):
    """Return (track_id, preview_url) or (None, None)."""
    q = f'artist:"{artist}" track:"{title}"'
    try:
        r = requests.get("https://api.deezer.com/search",
                         params={"q": q, "limit": 5},
                         headers=DEEZER_HEADERS, timeout=10)
        r.raise_for_status()
        for item in r.json().get("data", []):
            if item.get("preview"):               # 30‑sec MP3 link
                return item["id"], item["preview"]
    except requests.RequestException as e:
        log.warning("Deezer search failed: %s – %s | %s", artist, title, e)
    return None, None


def download_preview(url):
    """Download MP3 preview to a temp file; return path."""
    r = requests.get(url, stream=True, timeout=15)
    r.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    for chunk in r.iter_content(8192):
        tmp.write(chunk)
    tmp.close()
    return tmp.name


# ── Essentia extractor ──────────────────────────────
def run_essentia(audio_path):
    """Run essentia_streaming_extractor_music; return JSON dict."""
    out_json = audio_path + ".json"
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    profile = os.path.join(SCRIPT_DIR, "profile_highlevel.yaml")
    cmd = [
        "essentia_streaming_extractor_music",
        audio_path,
        out_json,
        profile
    ]

    subprocess.run(cmd, check=True)

    with open(out_json, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    # clean up temp files
    os.remove(audio_path)
    os.remove(out_json)
    return data

# ── Main ETL loop ───────────────────────────────────
CHECK_FILE = "../../data/raw/acousticbrainz_2024.jsonl"
IN_FILE  = "../../data/processed/whosampled_tracks_2024.jsonl"
OUT_FILE = "../../data/raw/acousticbrainz_fallback_2024.jsonl"

with open(CHECK_FILE, "r", encoding="utf-8") as f:
    existing_wsids = set()
    for line in f:
        rec = json.loads(line)
        existing_wsids.add(rec["whosampled_id"])

with open(IN_FILE, "r", encoding="utf-8") as rf, \
     open(OUT_FILE, "w", encoding="utf-8") as wf:

    for line in rf:
        rec = json.loads(line)
        if rec["whosampled_id"] in existing_wsids:
            log.info("Already exists: %s", rec["whosampled_id"])
            continue

        artist_names = rec["artist"] if isinstance(rec["artist"], list) else [rec["artist"]]
        title = rec["title"]

        track_id, preview_url = None, None
        for name in artist_names:
            track_id, preview_url = search_deezer_preview(name, title)
            time.sleep(0.3)
            if track_id:
                break

        if not track_id:
            log.info("No Deezer preview: %s – %s", artist_names, title)
            continue

        try:
            mp3_path = download_preview(preview_url)
            features = run_essentia(mp3_path)
        except Exception as e:
            log.warning("Essentia failed: %s – %s | %s", artist_names, title, e)
            continue

        out = {
            "whosampled_id":   rec["whosampled_id"],
            "deezer_track_id": track_id,
            "features": features
        }
        wf.write(json.dumps(out, ensure_ascii=False) + "\n")
        log.info("✓ Deezer/Essentia features saved for %s – %s", artist_names[0], title)
        time.sleep(1)                          # avoid MB & Deezer throttling
