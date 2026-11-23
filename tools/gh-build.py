import io, json, os, sys, time, urllib.request, urllib.error, zipfile

raw = open("/root/.git-credentials").read().strip()
creds, _ = raw.split("://", 1)[1].rsplit("@", 1)
token = creds.split(":", 1)[1]
REPO = sys.argv[1]
OUT = sys.argv[2]
NAME = sys.argv[3] if len(sys.argv) > 3 else "super-mario-apk"


class NoAuth(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None:
            new.headers.pop("Authorization", None)
        return new


opener = urllib.request.build_opener(NoAuth)


def api(path):
    req = urllib.request.Request("https://api.github.com" + path,
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json", "User-Agent": "eta"})
    try:
        with urllib.request.urlopen(req) as r:
            p = r.read()
            return json.loads(p) if p else {}
    except urllib.error.HTTPError as e:
        return {"__error__": e.code, "body": e.read().decode()[:200]}


deadline = time.time() + 45 * 60
run = None
while time.time() < deadline:
    runs = api("/repos/%s/actions/runs?per_page=1" % REPO).get("workflow_runs", [])
    if not runs:
        print("no runs yet", time.strftime("%H:%M:%S"), flush=True)
        time.sleep(30)
        continue
    run = runs[0]
    print("run %s status=%s conclusion=%s %s" % (run["id"], run["status"], run["conclusion"], time.strftime("%H:%M:%S")), flush=True)
    if run["status"] == "completed":
        break
    time.sleep(30)

if run and run.get("conclusion") != "success":
    req = urllib.request.Request("https://api.github.com/repos/%s/actions/runs/%d/logs" % (REPO, run["id"]),
        headers={"Authorization": "Bearer " + token, "User-Agent": "eta"})
    with opener.open(req, timeout=180) as r:
        blob = r.read()
    zf = zipfile.ZipFile(io.BytesIO(blob))
    text = "\n".join("%s\n%s" % (n, zf.read(n).decode("utf-8", "ignore")) for n in zf.namelist())
    path = "/workspace/临时/%s-fail.log" % REPO.replace("/", "-")
    open(path, "w", encoding="utf-8").write(text)
    print("logs:", path)
    for ln in text.splitlines():
        if "error:" in ln.lower() or "FAILURE" in ln:
            print(ln[:200])
else:
    arts = api("/repos/%s/actions/runs/%d/artifacts" % (REPO, run["id"])).get("artifacts", [])
    print("artifacts:", [(a["name"], a["size_in_bytes"]) for a in arts])
    for a in arts:
        if a["name"] == NAME and not a["expired"]:
            req = urllib.request.Request("https://api.github.com/repos/%s/actions/artifacts/%d/zip" % (REPO, a["id"]),
                headers={"Authorization": "Bearer " + token, "User-Agent": "eta"})
            with opener.open(req, timeout=300) as r:
                blob = r.read()
            zf = zipfile.ZipFile(io.BytesIO(blob))
            os.makedirs(os.path.dirname(OUT), exist_ok=True)
            for n in zf.namelist():
                if n.endswith(".apk"):
                    open(OUT, "wb").write(zf.read(n))
                    print("saved:", OUT, os.path.getsize(OUT))
            break
