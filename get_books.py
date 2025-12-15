import json, requests, time, uuid

SUBJECTS = ["science_fiction", "fantasy", "mystery", "history", "romance", "biography"]
TARGET = 10000
BATCH = 200
out_path = "dataset/books-openlibrary.jsonl"
seen = set()
count = 0

def fetch_subject(subject, offset, limit):
    url = f"https://openlibrary.org/subjects/{subject}.json?limit={limit}&offset={offset}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json().get("works", [])

with open(out_path, "w", encoding="utf-8") as f:
    for subject in SUBJECTS:
        offset = 0
        while count < TARGET:
            works = fetch_subject(subject, offset, BATCH)
            if not works:
                break
            for w in works:
                key = w.get("key")
                if key in seen:
                    continue
                seen.add(key)
                doc_id = key.strip("/").replace("/", "-")
                title = w.get("title")
                authors = [a.get("name") for a in w.get("authors", []) if a.get("name")]
                langs = w.get("languages") or []
                lang = langs[0].get("key").split("/")[-1] if langs else "en"
                year = (w.get("first_publish_year") or w.get("created", {}).get("value", "")[:4]) or None
                subjects = [s for s in w.get("subjects", []) if isinstance(s, str)]
                synopsis = (w.get("description") or {}).get("value") if isinstance(w.get("description"), dict) else w.get("description")
                doc = {
                    "title": title,
                    "author": ", ".join(authors) if authors else None,
                    "language": lang,
                    "published_year": int(year) if isinstance(year, int) else None,
                    "genres": subjects[:8],
                    "synopsis": synopsis or "",
                    "tags": subjects[:12],
                    "file_url": f"https://openlibrary.org{key}"
                }
                f.write(json.dumps({ "index": { "_index": "ebooks", "_id": doc_id } }) + "\n")
                f.write(json.dumps(doc) + "\n")
                count += 1
                if count >= TARGET:
                    break
            offset += BATCH
            time.sleep(0.3)
print(f"wrote {count} docs to {out_path}")