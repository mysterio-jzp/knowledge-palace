#!/usr/bin/env python3
# 把 blog-dist/ 部署到 GitHub Pages 仓库（Contents API 推送 + 触发 Pages 重建）
# Token 从环境变量读取，切勿硬编码进本文件（本仓库为公开仓库）。
# 用法:  GH_TOKEN=ghp_xxx python3 tools/deploy.py
import os, base64, json, subprocess, time, sys

TOKEN = os.environ.get('GH_TOKEN')
if not TOKEN:
    print('ERROR: 请先设置环境变量 GH_TOKEN=你的GitHubPersonalAccessToken')
    sys.exit(1)

REPO_ID = 1322435195                              # mysterio-jzp/knowledge-palace
HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.dirname(HERE)                      # blog-dist


def curl(method, url, data=None):
    cmd = ["curl", "-s", "--max-time", "40", "-X", method,
           "-H", f"Authorization: Bearer {TOKEN}",
           "-H", "Content-Type: application/json"]
    if data is not None:
        cmd += ["-d", json.dumps(data)]
    p = subprocess.run(cmd + [url], capture_output=True, text=True)
    return p.stdout


def deploy(local_rel):
    local = os.path.join(DIST, local_rel)
    if not os.path.exists(local):
        print(f"SKIP {local_rel} (missing)")
        return
    b64 = base64.b64encode(open(local, "rb").read()).decode()
    url = f"https://api.github.com/repositories/{REPO_ID}/contents/{local_rel}"
    sha = ""
    for _ in range(1, 7):                          # GET sha 带重试（sandbox TLS 偶抖）
        try:
            cur = json.loads(curl("GET", url))
            if "sha" in cur:
                sha = cur["sha"]
                break
            if str(cur.get("message", "")).startswith("Not Found"):
                sha = ""
                break
        except Exception:
            pass
        time.sleep(2)
    payload = {"message": f"update {local_rel}", "content": b64}
    if sha:
        payload["sha"] = sha
    for attempt in range(1, 5):
        try:
            resp = json.loads(curl("PUT", url, payload))
            if "commit" in resp:
                print(f"OK   {local_rel} ({len(b64)}b)")
                return
            print(f"FAIL {local_rel} try{attempt}: {resp.get('message')}")
        except Exception as e:
            print(f"ERR  {local_rel} try{attempt}: {e}")
        time.sleep(2)
    print(f"GAVEUP {local_rel}")


# 要推送的文件
targets = ["index.html", "notes.json", ".nojekyll", "README.md"]
for f in sorted(os.listdir(os.path.join(DIST, "notes"))):
    if f.endswith(".md"):
        targets.append(f"notes/{f}")
for f in sorted(os.listdir(HERE)):
    if f.endswith(".py"):
        targets.append(f"tools/{f}")

print(f"=== 推送 {len(targets)} 个文件 ===")
for t in targets:
    deploy(t)

# 触发 Pages 重建
print("=== 触发 Pages 重建 ===")
for _ in range(1, 6):
    r = curl("POST", f"https://api.github.com/repositories/{REPO_ID}/pages/builds",
             {"ref": "main"})
    try:
        d = json.loads(r)
        if "status" in d:
            print("rebuild:", d.get("status"), d.get("created_at"))
            break
    except Exception:
        pass
    time.sleep(3)
print("=== DONE ===")
