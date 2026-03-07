#!/usr/bin/env python3
"""Parse the old index.html and generate individual publication markdown files."""

import re
import os
import unicodedata

HTML_FILE = os.path.join(os.path.dirname(__file__), '..', '_old_index.html')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', '_publications')


def slugify(text, max_len=60):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_]+', '-', text).strip('-')
    return text[:max_len].rstrip('-')


def extract_section(html, h3_title):
    pattern = rf'<h3>{re.escape(h3_title)}</h3>\s*<ol>(.*?)</ol>'
    m = re.search(pattern, html, re.DOTALL)
    return m.group(1) if m else ''


def parse_items(ol_html):
    items = re.findall(r'<li>\s*<p>(.*?)</p>\s*</li>', ol_html, re.DOTALL)
    return items


def clean(text):
    text = re.sub(r'</?[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&nbsp', ' ').replace('&amp;', '&')
    text = text.replace('&ldquo;', '"').replace('&rdquo;', '"')
    text = text.replace('&lsquo;', "'").replace('&rsquo;', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_pub(raw_html):
    abbr_m = re.search(r'\[(\w[\w\s]*?)\]', raw_html)
    abbr = abbr_m.group(1).strip() if abbr_m else ''

    after_abbr = raw_html
    if abbr_m:
        after_abbr = raw_html[abbr_m.end():]

    parts = re.split(r'<br\s*/?>', after_abbr)
    parts = [p.strip() for p in parts if p.strip()]

    title_raw = parts[0] if parts else ''
    title = clean(title_raw).rstrip(' ,')

    authors_raw = parts[1] if len(parts) > 1 else ''
    authors = clean(authors_raw).rstrip(' .')

    venue_raw = parts[2] if len(parts) > 2 else ''
    venue_m = re.search(r'<i>(.*?)</i>', venue_raw)
    venue = clean(venue_m.group(1)) if venue_m else ''

    rest_text = clean(venue_raw)
    # Find all 4-digit numbers starting with 20, pick the last one that looks like a plausible year
    year_candidates = re.findall(r'\b(20\d{2})\b', rest_text)
    year = '2024'
    for y in reversed(year_candidates):
        if 2015 <= int(y) <= 2030:
            year = y
            break

    vol_m = re.search(r'vol\.\s*([\d]+)', rest_text, re.IGNORECASE)
    pages_m = re.search(r'pp\.\s*([\d]+-[\d]+)', rest_text, re.IGNORECASE)
    extra = ''
    if vol_m:
        extra += f'vol. {vol_m.group(1)}'
    if pages_m:
        extra += f', pp. {pages_m.group(1)}'

    return {
        'abbr': abbr,
        'title': title,
        'authors': authors,
        'venue': venue,
        'year': year,
        'extra': extra,
    }


def write_pub(pub, category, index, out_dir):
    slug = slugify(pub['title'])
    month = (index // 28) + 1
    day = (index % 28) + 1
    date = f"{pub['year']}-{month:02d}-{day:02d}"
    filename = f"{date}-{slug}.md"

    citation = f'{pub["authors"]}. \"{pub["title"]}.\" *{pub["venue"]}*, {pub["year"]}.'

    content = f"""---
title: "{pub['title'].replace('"', "'")}"
collection: publications
category: {category}
permalink: /publication/{slug}
date: {date}
venue: '{pub['venue'].replace("'", "''")}'
citation: '{pub["authors"].replace("'", "''")}. ({pub["year"]}). &quot;{pub["title"].replace("'", "''")}&quot; <i>{pub["venue"]}</i>.'
---

**[{pub['abbr']}]** {pub['title']}

{pub['authors']}.

*{pub['venue']}*{', ' + pub['extra'] if pub['extra'] else ''}, {pub['year']}.
"""

    path = os.path.join(out_dir, filename)
    with open(path, 'w') as f:
        f.write(content)
    return filename


def main():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    os.makedirs(OUT_DIR, exist_ok=True)
    # Clear old sample publications
    for old in os.listdir(OUT_DIR):
        if old.endswith('.md'):
            os.remove(os.path.join(OUT_DIR, old))

    sections = [
        ('Book', 'books'),
        ('Journal and Magazine', 'manuscripts'),
        ('Conferences', 'conferences'),
        ('Working Papers', 'preprints'),
    ]

    total = 0
    for h3_title, category in sections:
        ol_html = extract_section(html, h3_title)
        if not ol_html:
            print(f'  WARNING: No items found for section "{h3_title}"')
            continue

        items = parse_items(ol_html)
        print(f'  {h3_title}: {len(items)} items')

        for i, item_html in enumerate(items):
            pub = parse_pub(item_html)
            fn = write_pub(pub, category, i, OUT_DIR)
            total += 1

    print(f'\nGenerated {total} publication files in {OUT_DIR}')


if __name__ == '__main__':
    main()
