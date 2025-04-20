import json
import time
import logging
import requests


logging.basicConfig(
    level=logging.INFO,                       # DEBUG for more detail
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("MusicKG")

MB_HEADERS = {"User-Agent": "MusicKG/0.1 (you@example.com)"}
ABZ_HEADERS = {"User-Agent": "MusicKG/0.1 (you@example.com)"}


def search_recordings(artist: str, title: str, limit: int = 3):
    """Return up to `limit` recording MBIDs for artist + title."""
    q = f'recording:"{title}" AND artist:"{artist}"'
    url = "https://musicbrainz.org/ws/2/recording"
    try:
        r = requests.get(url, params={"query": q, "limit": limit, "fmt": "json"},
                         headers=MB_HEADERS, timeout=10)
        r.raise_for_status()
        mbids = [rec["id"] for rec in r.json().get("recordings", [])]
        log.debug("MB search «%s – %s»: %s", artist, title, mbids)
        return mbids
    except requests.RequestException as e:
        log.warning("MB search failed «%s – %s»: %s", artist, title, e)
        return []


def get_features(mbids):
    """Return (mbid, high‑level JSON) for the first MBID with ABZ data."""
    for mbid in mbids:
        url = f"https://acousticbrainz.org/api/v1/{mbid}/high-level"
        try:
            r = requests.get(url, headers=ABZ_HEADERS, timeout=10)
            if r.status_code == 404:
                log.debug("AB 404 %s", mbid)
                continue
            r.raise_for_status()
            return mbid, r.json()
        except requests.RequestException as e:
            log.warning("AB fetch failed %s: %s", mbid, e)

    return None, None


IN_FILE  = "../../data/processed/whosampled_tracks_2024.jsonl"
OUT_FILE = "../../data/raw/acousticbrainz_2024.jsonl"

counter, matched = 0, 0
with open(IN_FILE, "r", encoding="utf-8") as rf, \
     open(OUT_FILE, "w", encoding="utf-8") as wf:

    for line in rf:
        counter += 1
        rec = json.loads(line)
        if isinstance(rec['artist'], list):
            rec["artist"] = rec["artist"][0]
        mbids = search_recordings(rec["artist"], rec["title"], limit=5)

        if not mbids:
            log.info("No MBID: %s – %s", rec["artist"], rec["title"])
            continue

        mbid, features = get_features(mbids)
        if not features:
            log.info("No AB data: %s – %s", rec["artist"], rec["title"])
            continue

        wf.write(json.dumps({"whosampled_id": rec["whosampled_id"], "mbid": mbid,
                             "features": features}, ensure_ascii=True) + "\n")
        matched += 1
        log.info("✓ %s – %s (MBID %s)", rec["artist"], rec["title"], mbid)
        time.sleep(1)           # API politeness

log.info("Finished. %d tracks processed, %d matched with AB data.", counter, matched)
