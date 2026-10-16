#!/usr/bin/env python3
"""Render a directory of SVG drawings using permitted local HTTP navigation."""
import functools
import http.server
from pathlib import Path
import sys
import threading
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

root = Path(sys.argv[1]).resolve()
folders = sys.argv[2:] or ['v8/plans', 'v8/croquis', 'v8/mobilier']
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(root)))
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        try:
            page = browser.new_page()
            count = 0
            for folder in folders:
                for svg in sorted((root / folder).glob('*.svg')):
                    _, _, width, height = map(float, ET.parse(svg).getroot().attrib['viewBox'].split())
                    page.set_viewport_size({'width': round(width), 'height': round(height)})
                    url = f'http://127.0.0.1:{server.server_port}/' + svg.relative_to(root).as_posix()
                    response = page.goto(url, wait_until='networkidle', timeout=30000)
                    assert response and response.status == 200, url
                    page.evaluate('document.fonts.ready')
                    page.screenshot(path=str(svg.with_suffix('.png')), timeout=30000)
                    count += 1
            assert count > 0, 'No SVG drawings found'
            print(f'Rendered {count} SVG drawings to PNG')
        finally:
            browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join()
