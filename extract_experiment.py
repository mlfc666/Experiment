#!/usr/bin/env python3
import re
import html
import urllib.request
import os
import json

def extract_experiment(html_path, output_dir, base_url):
    """Extract experiment content from HTML and convert to Markdown"""

    # Read HTML
    with open(html_path, 'rb') as f:
        content = f.read().decode('utf-8')

    # Unescape JSON-style escapes
    content = content.replace('\\"', '"').replace('\\\\', '\\')

    # Extract write div content
    match = re.search(r'<div id="write"[^>]*>(.*)', content, re.DOTALL)
    if not match:
        print(f"No write div found in {html_path}")
        return

    text = match.group(1)

    # Extract images
    img_pattern = r'<img[^>]*src="([^"]+\.(png|jpg|jpeg|gif|svg|webp))"[^>]*/?>'
    images = re.findall(img_pattern, text)
    print(f"Found {len(images)} images")

    # Download images
    img_dir = os.path.join(output_dir, 'images')
    os.makedirs(img_dir, exist_ok=True)

    downloaded_imgs = []
    for img, ext in images:
        clean_path = img.replace('\\', '/')
        filename = clean_path.split('/')[-1]
        img_url = f"{base_url}/{clean_path}".replace('\\', '/')
        local_path = os.path.join(img_dir, filename)

        try:
            urllib.request.urlretrieve(img_url, local_path)
            downloaded_imgs.append((img, filename))
            print(f"  Downloaded: {filename}")
        except Exception as e:
            print(f"  Failed to download {img_url}: {e}")

    # Replace image paths in text
    for img, filename in downloaded_imgs:
        text = re.sub(
            r'<img[^>]*src="[^"]*' + re.escape(img) + r'"[^>]*>',
            f'![{filename}](images/{filename})',
            text
        )

    # Convert HTML to Markdown
    text = re.sub(r'<h2[^>]*><a[^>]*name="([^"]*)"[^>]*></a><span>([^<]*)</span></h2>', r'\n## \2\n', text)
    text = re.sub(r'<h3[^>]*><a[^>]*name="([^"]*)"[^>]*></a><span>([^<]*)</span></h3>', r'\n### \2\n', text)
    text = re.sub(r'<h4[^>]*><a[^>]*name="([^"]*)"[^>]*></a><span>([^<]*)</span></h4>', r'\n#### \2\n', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<p[^>]*>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<li[^>]*>', '- ', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<ul[^>]*>', '\n', text)
    text = re.sub(r'</ul>', '\n', text)
    text = re.sub(r'<ol[^>]*/?>', '\n', text)
    text = re.sub(r'</ol>', '\n', text)
    text = re.sub(r'<span[^>]*>([^<]*)</span>', r'\1', text)
    text = re.sub(r'<div[^>]*class="CodeMirror[^"]*"[^>]*>.*?</div>\s*</div>', '', text, flags=re.DOTALL)
    text = re.sub(r'<div class="cm-s-inner[^"]*"[^>]*>.*?</div>\s*</div>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'x{10,}', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' +\n', '\n', text)
    text = re.sub(r'\n +', '\n', text)
    text = text.strip()

    # Save Markdown
    md_path = os.path.join(output_dir, '实验.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"Saved Markdown to {md_path}")
    return text

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 4:
        print("Usage: extract_experiment.py <html_path> <output_dir> <base_url>")
        sys.exit(1)

    html_path = sys.argv[1]
    output_dir = sys.argv[2]
    base_url = sys.argv[3]

    extract_experiment(html_path, output_dir, base_url)