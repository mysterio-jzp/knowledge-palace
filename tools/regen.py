#!/usr/bin/env python3
# 从 vault 真实目录结构重建博客索引 notes.json + 全部 notes/N.md
# 路径由脚本位置自动推导（脚本应放在 <vault>/blog-dist/tools/regen.py）：
#   tools/ -> blog-dist/ -> <vault>
import os, re, json, shutil
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.dirname(HERE)                       # blog-dist
VAULT = os.path.dirname(DIST)                      # 学习笔记（vault 根）
NOTES_DIR = os.path.join(DIST, 'notes')
os.makedirs(NOTES_DIR, exist_ok=True)

EXCLUDE = {'.workbuddy', 'blog-dist'}

# 一级目录 -> 展示用分类名（直接用真实目录名；不在下表里的目录会自动用原名）
CAT_DISPLAY = {
    'Agent': 'Agent',
    '人工智能基础': '人工智能基础',
    '线性代数': '线性代数',
    '网络工程': '网络工程',
}
DEFAULT_CAT = '其他'


def parse_frontmatter(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?', text, re.DOTALL)
    if not m:
        return {}, text
    fm, body = m.group(1), text[m.end():]
    meta = {}
    for line in fm.splitlines():
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        k, v = k.strip(), v.strip()
        if v.startswith('[') and v.endswith(']'):
            inner = v[1:-1].strip()
            meta[k] = [x.strip().strip('"').strip("'") for x in inner.split(',') if x.strip()]
        else:
            meta[k] = v.strip('"').strip("'")
    return meta, body


def make_summary(body, n=200):
    body = re.sub(r'```.*?```', ' ', body, flags=re.DOTALL)
    body = re.sub(r'(?m)^#{1,6}\s*', '', body)
    body = re.sub(r'(?m)^>\s?', '', body)
    body = re.sub(r'[*_`#>\-\[\]\(\)]', '', body)
    body = re.sub(r'\s+', ' ', body).strip()
    return body[:n]


def copy_note_images(full, notes_dir):
    """把笔记里引用的本地图片复制到 blog-dist/notes/。
    返回 [(原引用, 新引用 notes/xxx.png)]，供重写笔记副本里的图片路径。"""
    text = open(full, encoding='utf-8').read()
    note_dir = os.path.dirname(full)
    out = []
    for m in re.finditer(r'!\[[^\]]*\]\(([^)\s]+)\)', text):
        ref = m.group(1)
        if ref.startswith(('http://', 'https://', 'data:')):
            continue
        src = os.path.normpath(os.path.join(note_dir, ref))
        if not os.path.isfile(src):
            print(f'WARN  图片缺失: {full}: {ref}')
            continue
        new_ref = f'notes/{os.path.basename(ref)}'
        dst = os.path.join(notes_dir, os.path.basename(ref))
        if os.path.abspath(src) != os.path.abspath(dst):
            if os.path.exists(dst) and open(dst, 'rb').read() != open(src, 'rb').read():
                print(f'WARN  同名图片被覆盖: {os.path.basename(ref)}')
            shutil.copy2(src, dst)
        out.append((ref, new_ref))
    return out


# 收集 vault 内全部 .md（排除工作区与 blog-dist）
files = []
for dp, _, fs in os.walk(VAULT):
    if any(part in EXCLUDE for part in dp.split(os.sep)):
        continue
    for f in fs:
        if f.endswith('.md'):
            files.append(os.path.relpath(os.path.join(dp, f), VAULT))
files.sort()

items = []
for idx, rel in enumerate(files):
    full = os.path.join(VAULT, rel)
    text = open(full, encoding='utf-8').read()
    meta, body = parse_frontmatter(text)
    parts = rel.split('/')
    room = DEFAULT_CAT if len(parts) == 1 else CAT_DISPLAY.get(parts[0], parts[0])
    title = meta.get('title') or os.path.splitext(os.path.basename(rel))[0]
    date = meta.get('date', '')
    if isinstance(date, list):
        date = date[0] if date else ''
    tags = meta.get('tags', [])
    if isinstance(tags, str):
        tags = [tags]
    entry = {
        'id': idx,
        'room': room,                 # 一级真实目录名（= 博客顶部分类 tab）
        'path': rel,                  # 完整相对路径（文章页面包屑）
        'date': date,
        'title': title,
        'tags': tags,
        'from': os.path.splitext(os.path.basename(rel))[0],
        'summary': make_summary(body),
        'file': f'notes/{idx}.md',
    }
    items.append(entry)
    note_copy = text
    for ref, new_ref in copy_note_images(full, NOTES_DIR):
        note_copy = note_copy.replace(f']({ref})', f']({new_ref})')
        print(f'  图片  {new_ref} <- {ref}')
    open(os.path.join(NOTES_DIR, f'{idx}.md'), 'w', encoding='utf-8').write(note_copy)

json.dump(items, open(os.path.join(DIST, 'notes.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print('vault 根目录 :', VAULT)
print('总篇数      :', len(items))
print('分类统计:')
for k, v in Counter(i['room'] for i in items).most_common():
    print(f'  {k}: {v}')
print('\n样本(前3条 path):')
for i in items[:3]:
    print('  ', i['path'], '->', i['room'])
