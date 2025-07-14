#!/usr/bin/env python3
import os
import glob
import json
import re
from bs4 import BeautifulSoup, Tag, NavigableString

def extract_sections(soup):
    sections = {}
    # find all <strong><u>Heading:</u></strong> patterns
    headings = []
    for strong in soup.find_all('strong'):
        u = strong.find('u')
        if u:
            # use the text inside <u> as the section name, strip trailing colon
            name = u.get_text().strip().rstrip(':').strip()
            headings.append((strong, name))

    for idx, (strong_tag, heading) in enumerate(headings):
        next_strong = headings[idx + 1][0] if idx + 1 < len(headings) else None
        lines = []
        current = []

        for sib in strong_tag.next_siblings:
            # stop if we hit the next heading
            if sib == next_strong:
                break
            if isinstance(sib, Tag) and sib.name == 'strong' and sib.find('u'):
                break

            if isinstance(sib, Tag):
                if sib.name == 'br':
                    # end of this line
                    text = ''.join(current).strip()
                    if text:
                        lines.append(text)
                    current = []
                else:
                    # capture all text inside other tags (links, spans, etc)
                    current.append(sib.get_text(separator='', strip=False))
            elif isinstance(sib, NavigableString):
                txt = str(sib)
                if txt.strip():
                    current.append(txt)

        # flush last line
        if current:
            text = ''.join(current).strip()
            if text:
                lines.append(text)

        # clean up whitespace and dash-prefixed items
        clean = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line).strip()
            if line.startswith('- '):
                clean.append(line[2:].strip())
            else:
                clean.append(line)
        # decide whether to store string or list
        if len(clean) == 1:
            sections[heading] = clean[0]
        elif clean:
            sections[heading] = clean
        else:
            sections[heading] = ''

    return sections

def main():
    pages_dir = os.path.join(os.getcwd(), 'output', 'pages')
    html_files = sorted(glob.glob(os.path.join(pages_dir, '*.html')))
    data = {}

    for path in html_files:
        key = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
        data[key] = extract_sections(soup)

    out_path = os.path.join(os.getcwd(), 'neurons.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'✓ Extracted {len(html_files)} files → {out_path}')

if __name__ == '__main__':
    main()
