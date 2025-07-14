#!/usr/bin/env python3
"""
selenium_wormatlas_dynamic.py

Fetch only the existing WormAtlas framesets by dynamically testing
for each grouping candidate—full name, strip 1 char, strip 2 chars,
strip trailing digits—then grabbing mainFrame. Skips pages already saved.

Dependencies:
    pip install selenium requests
    • Place chromedriver on your PATH.
"""

import urllib3
# disable warnings about unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
import re
import time
from collections import defaultdict

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_URL   = "https://www.wormatlas.org/neurons/Individual%20Neurons/"
INPUT_FILE = "neurons.txt"
OUT_DIR    = "output/pages"
HEADERS    = {"User-Agent": "dynamic-scraper/1.0"}
DELAY      = 1.0  # seconds between loads

os.makedirs(OUT_DIR, exist_ok=True)

# 1) Load your neuron list
with open(INPUT_FILE) as f:
    neurons = [l.strip() for l in f if l.strip()]

# 2) Helper: does this frameset exist?
def frameset_exists(base_name):
    url = f"{BASE_URL}{base_name}frameset.html"
    try:
        r = requests.head(url, headers=HEADERS, timeout=5, verify=False)
        ok = (r.status_code == 200)
    except requests.RequestException:
        ok = False
    print(f"[check] {base_name:6s}frameset.html → {'OK' if ok else '404/ERR'}")
    return ok

# 3) Decide grouping for each neuron dynamically
groups = {}
for nm in neurons:
    tried = set()
    # build candidate bases in order
    candidates = [
        nm,
        nm[:-1],
        nm[:-2],
        re.sub(r"\d+$", "", nm)
    ]
    for base in candidates:
        if base in tried or len(base) < 2:
            continue
        tried.add(base)
        print(f"[group-check] trying {base}frameset.html for {nm}")
        if frameset_exists(base):
            groups[nm] = base
            print(f"[group] {nm} → {base}")
            break
    else:
        # fallback: use the neuron itself
        groups[nm] = nm
        print(f"[group] {nm} → {nm} (fallback)")

# 4) Invert to get unique list of frameset bases
frameset_bases = sorted(set(groups.values()))
print("\n=== Will fetch framesets for these bases ===")
print(", ".join(frameset_bases))
print()

# 5) Selenium setup
opts = Options()
opts.add_argument("--headless")
opts.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=opts)

# 6) Fetch each base once, skipping existing files
for base in frameset_bases:
    out_path = os.path.join(OUT_DIR, f"{base}.html")
    if os.path.exists(out_path):
        print(f"→ Skipping {base}, already saved.")
        continue

    frameset_url = f"{BASE_URL}{base}frameset.html"
    print(f"→ Loading frameset: {frameset_url}")
    driver.get(frameset_url)
    time.sleep(0.5)

    # switch into mainFrame (or fallback to last <frame>)
    try:
        driver.switch_to.frame("mainFrame")
    except:
        frs = driver.find_elements(By.TAG_NAME, "frame")
        if not frs:
            print(f"⚠️  No frames for {base}, skipping.")
            driver.switch_to.default_content()
            continue
        driver.switch_to.frame(frs[-1])

    # save the content HTML
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print(f"✔️  Saved {base}.html")

    driver.switch_to.default_content()
    time.sleep(DELAY)

driver.quit()
print("✅ Done.")
