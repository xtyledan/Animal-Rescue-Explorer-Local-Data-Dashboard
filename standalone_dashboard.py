"""Local animal rescue dashboard. Run: python standalone_dashboard.py

Uses synthetic sample data; optional MONGO_URI enables MongoDB.
"""
import argparse
import csv
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

DATA = Path(__file__).with_name("sample_animals.csv")
FIELDS = ("animal_id", "name", "animal_type", "breed", "outcome_type", "location_lat", "location_long")


def load_animals():
    if os.getenv("MONGO_URI"):
        from crud import AnimalShelter
        return [{key: (record.get(key) if record.get(key) is not None else "") for key in FIELDS} for record in AnimalShelter().read({})]
    with DATA.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def filter_animals(rows, animal_type="", breed="", outcome=""):
    """Filter by exact animal type/outcome and case-insensitive breed substring."""
    return [
        dict(row) for row in rows
        if (not animal_type or str(row.get("animal_type", "")).casefold() == animal_type.casefold())
        and (not breed or breed.casefold() in str(row.get("breed", "")).casefold())
        and (not outcome or str(row.get("outcome_type", "")).casefold() == outcome.casefold())
    ]


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Animal Rescue Explorer</title>
<style>
:root{font:16px system-ui;color:#17293d;background:#f3f6fa}*{box-sizing:border-box}body{margin:0}
header{background:#16324f;color:#fff;padding:36px max(22px,calc((100vw - 1100px)/2))}
h1{margin:0}header p{color:#d5e4f0}main{max-width:1100px;margin:24px auto;padding:0 18px}
section{background:white;border:1px solid #dee6ef;border-radius:12px;padding:22px;margin:0 0 18px}
.filters,.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px}
label{display:flex;flex-direction:column;gap:7px;font-weight:600}
input,select{font:inherit;padding:10px;border:1px solid #a7b8c7;border-radius:7px}
.stat strong{display:block;font-size:2rem}
table{width:100%;border-collapse:collapse;text-align:left}td,th{padding:10px;border-bottom:1px solid #e7edf2;font-size:14px}
.wrap{overflow:auto}.barrow{display:grid;grid-template-columns:minmax(110px,1fr) 2fr 35px;gap:10px;align-items:center;margin:10px 0}
.bar{height:12px;border-radius:6px;background:#2475ae;min-width:2px}
small{color:#536477}@media(max-width:680px){.filters,.stats{grid-template-columns:1fr}}
</style></head><body>
<header><h1>Animal Rescue Explorer</h1><p>Filter shelter data and explore outcomes and breeds.</p></header>
<main><section><h2>Filters</h2><div class="filters">
<label>Animal type<select id="type"><option value="">All</option><option>Dog</option><option>Cat</option></select></label>
<label>Breed contains<input id="breed" placeholder="e.g. Labrador"></label>
<label>Outcome<select id="outcome"><option value="">All</option><option>Adoption</option><option>Transfer</option><option>Return to Owner</option></select></label>
</div></section>
<div class="stats"><section class="stat">Animals<strong id="count">—</strong></section>
<section class="stat">Adoptions<strong id="adoptions">—</strong></section>
<section class="stat">Distinct breeds<strong id="breeds">—</strong></section></div>
<section><h2>Breed distribution</h2><div id="chart"></div></section>
<section><h2>Animal records</h2><p id="status" role="status"></p><div class="wrap"><table>
<thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Breed</th><th>Outcome</th><th>Location</th></tr></thead>
<tbody id="records"></tbody></table></div></section>
<small>Default dataset is synthetic demonstration data, not real shelter animals. Read-only local educational tool.</small>
</main><script>
const el=id=>document.getElementById(id), node=(tag,text)=>{const x=document.createElement(tag);x.textContent=String(text??'');return x};
async function refresh(){
 const params=new URLSearchParams({animal_type:el('type').value,breed:el('breed').value,outcome:el('outcome').value});
 el('status').textContent='Loading…';
 try{
 const res=await fetch('/api/animals?'+params);if(!res.ok)throw Error('HTTP '+res.status);
 const data=await res.json(), rows=data.animals;
 el('count').textContent=rows.length;
 el('adoptions').textContent=rows.filter(r=>r.outcome_type==='Adoption').length;
 const counts={};for(const r of rows){const b=r.breed||'Unknown';counts[b]=(counts[b]||0)+1}
 const ranked=Object.entries(counts).sort((a,b)=>b[1]-a[1]);el('breeds').textContent=ranked.length;
 const chart=el('chart');chart.replaceChildren();
 for(const [breed,count] of ranked.slice(0,12)){
 const item=node('div','');item.className='barrow';item.appendChild(node('span',breed));
 const track=node('div',''),bar=node('div','');bar.className='bar';bar.style.width=(100*count/ranked[0][1])+'%';
 track.appendChild(bar);item.appendChild(track);item.appendChild(node('span',count));chart.appendChild(item)}
 if(!ranked.length)chart.textContent='No matching breeds.';
 const body=el('records');body.replaceChildren();
 for(const r of rows){const tr=node('tr','');for(const k of ['animal_id','name','animal_type','breed','outcome_type'])tr.appendChild(node('td',r[k]));
 const td=node('td',''),lat=Number(r.location_lat),lon=Number(r.location_long);
 if(r.location_lat!==null&&r.location_lat!==undefined&&r.location_lat!==''&&r.location_long!==null&&r.location_long!==undefined&&r.location_long!==''&&Number.isFinite(lat)&&Number.isFinite(lon)&&Math.abs(lat)<=90&&Math.abs(lon)<=180){
 const a=node('a','Map');a.href='https://www.openstreetmap.org/?mlat='+encodeURIComponent(lat)+'&mlon='+encodeURIComponent(lon)+'#map=12/'+encodeURIComponent(lat)+'/'+encodeURIComponent(lon);a.target='_blank';a.rel='noopener noreferrer';td.appendChild(a)}
 else td.textContent='Unavailable';tr.appendChild(td);body.appendChild(tr)}
 el('status').textContent=rows.length+' matching records · '+(data.source==='sample'?'Synthetic sample':'MongoDB');
 }catch(e){el('status').textContent='Unable to load records: '+e.message}
}
el('type').addEventListener('change',refresh);el('outcome').addEventListener('change',refresh);el('breed').addEventListener('input',refresh);refresh();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/":
            self.send_content(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        elif url.path == "/health":
            self.send_json(200, {"status": "ok"})
        elif url.path == "/api/animals":
            query = parse_qs(url.query)
            try:
                animals = filter_animals(
                    load_animals(),
                    query.get("animal_type", [""])[0],
                    query.get("breed", [""])[0],
                    query.get("outcome", [""])[0],
                )
                self.send_json(200, {
                    "animals": animals,
                    "source": "mongo" if os.getenv("MONGO_URI") else "sample",
                })
            except Exception:
                # Never expose connection strings or database exception details.
                self.send_json(503, {"error": "Data source unavailable"})
        else:
            self.send_json(404, {"error": "Not found"})

    def send_json(self, status, body):
        self.send_content(status, json.dumps(body, default=str).encode("utf-8"),
                          "application/json; charset=utf-8")

    def send_content(self, status, content, media_type):
        self.send_response(status)
        self.send_header("Content-Type", media_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)


def main():
    parser = argparse.ArgumentParser(description="Run the local shelter data dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Open http://{args.host}:{server.server_port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
