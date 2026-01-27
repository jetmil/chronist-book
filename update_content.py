#!/usr/bin/env python3
"""Update CHRONIST HTML book content from updated markdown"""

import re
import html as html_module

def parse_markdown(md_content):
    """Parse markdown content and extract chapters"""
    chapters = []
    current_chapter = None
    current_content = []

    lines = md_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # PROLOGUE
        if line.startswith('## ПРОЛОГ:'):
            if current_chapter:
                current_chapter['content'] = '\n'.join(current_content)
                chapters.append(current_chapter)

            title = line.replace('## ПРОЛОГ:', '').strip()
            current_chapter = {
                'id': 'prologue',
                'type': 'prologue',
                'part': 'Пролог',
                'title': 'Пролог',
                'subtitle': title,
                'meta': ''
            }
            current_content = []
            i += 1
            continue

        # PARTS
        if line.startswith('## ЧАСТЬ'):
            i += 1
            continue

        # INTERLUDES
        if line.startswith('## ИНТЕРЛЮДИЯ') or ('ИНТЕРЛЮДИЯ' in line and line.startswith('##')):
            if current_chapter:
                current_chapter['content'] = '\n'.join(current_content)
                chapters.append(current_chapter)

            match = re.search(r'(\d+)[:.]\s*(.+)', line)
            if match:
                num = match.group(1)
                title = match.group(2).strip()
                interlude_id = f'interlude{num}'
            else:
                title = line.replace('##', '').replace('ИНТЕРЛЮДИЯ', '').strip(': ')
                interlude_id = f'interlude{len([c for c in chapters if "interlude" in c.get("id", "")]) + 1}'

            current_chapter = {
                'id': interlude_id,
                'type': 'interlude',
                'part': 'Интерлюдия',
                'title': 'Интерлюдия',
                'subtitle': title,
                'meta': ''
            }
            current_content = []
            i += 1
            continue

        # CHAPTERS
        if line.startswith('### Глава'):
            if current_chapter:
                current_chapter['content'] = '\n'.join(current_content)
                chapters.append(current_chapter)

            match = re.match(r'###\s*Глава\s*(\d+[а-яА-Яa-zA-Z-]*)[.:]\s*(.+)', line)
            if match:
                num = match.group(1)
                title = match.group(2).strip()
            else:
                num = str(len([c for c in chapters if c.get('type') == 'chapter']) + 1)
                title = line.replace('###', '').replace('Глава', '').strip()

            chapter_num = int(re.sub(r'[^0-9]', '', num) or 0)
            if chapter_num <= 8:
                part = 'Часть I: Сигнал'
            elif chapter_num <= 16:
                part = 'Часть II: Спуск'
            else:
                part = 'Часть III: Исцеление'

            current_chapter = {
                'id': f'ch{num}',
                'type': 'chapter',
                'part': part,
                'title': f'Глава {num}',
                'subtitle': title,
                'meta': ''
            }
            current_content = []
            i += 1
            continue

        # EPILOGUE
        if line.startswith('## ЭПИЛОГ:') or line.startswith('## Эпилог'):
            if current_chapter:
                current_chapter['content'] = '\n'.join(current_content)
                chapters.append(current_chapter)

            title = line.replace('## ЭПИЛОГ:', '').replace('## Эпилог:', '').strip()
            current_chapter = {
                'id': 'epilogue',
                'type': 'epilogue',
                'part': 'Эпилог',
                'title': 'Эпилог',
                'subtitle': title or 'Сто лет спустя',
                'meta': ''
            }
            current_content = []
            i += 1
            continue

        # Meta (date/location)
        if line.startswith('**') and ('год' in line.lower() or '20' in line or 'миллиард' in line.lower()):
            if current_chapter:
                current_chapter['meta'] = line.replace('**', '').strip()
            i += 1
            continue

        if current_chapter:
            current_content.append(line)

        i += 1

    if current_chapter:
        current_chapter['content'] = '\n'.join(current_content)
        chapters.append(current_chapter)

    return chapters


def format_content(content):
    """Convert markdown content to HTML with styling"""
    content = content.strip()
    if not content:
        return ''

    paragraphs = re.split(r'\n\n+', content)
    html_parts = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if para == '---':
            html_parts.append('<div class="scene-break">* * *</div>')
            continue

        if para.startswith('**') and para.endswith('**') and ('год' in para.lower() or 'миллиард' in para.lower()):
            continue

        if para.startswith('*') and para.endswith('*') and not para.startswith('**'):
            inner = para.strip('*')
            if any(phrase in inner.lower() for phrase in ['мама', 'тиа', 'река течёт', 'наконец-то', 'ты готова', 'геос', 'эпоха', 'холодные']):
                html_parts.append(f'<div class="voice-geos"><p>{html_module.escape(inner)}</p></div>')
            else:
                html_parts.append(f'<p><em>{html_module.escape(inner)}</em></p>')
            continue

        if para.startswith('**"') and '**' in para[3:]:
            inner = para.replace('**', '').strip('"')
            html_parts.append(f'<div class="voice-elisa">{html_module.escape(inner)}</div>')
            continue

        text = para
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

        if text.startswith('—') or text.startswith('-'):
            text = text.lstrip('—- ')
            html_parts.append(f'<p class="dialogue">{text}</p>')
        else:
            html_parts.append(f'<p>{text}</p>')

    return '\n'.join(html_parts)


# Chapter image mapping
chapter_images = {
    'prologue': 'prologue.png',
    'ch1': 'ch1.png', 'ch2': 'ch2.png', 'ch3': 'ch3.png', 'ch4': 'ch4.png',
    'ch5': 'ch5.png', 'ch6': 'ch6.png', 'ch7': 'ch7.png', 'ch8': 'ch8.png',
    'interlude1': 'interlude1.png',
    'ch9': 'ch9.png', 'ch10': 'ch10.png', 'ch11': 'ch11.png', 'ch12': 'ch12.png',
    'ch13': 'ch13.png', 'ch14': 'ch14.png', 'ch15': 'ch15.png', 'ch16': 'ch16.png',
    'interlude2': 'interlude2.png',
    'ch17': 'ch17.png', 'ch18': 'ch18.png', 'ch19': 'ch19.png', 'ch19b': 'ch19b.png',
    'ch20': 'ch20.png', 'ch21': 'ch21.png', 'ch22': 'ch22.png', 'ch23': 'ch23.png',
    'epilogue': 'epilogue.png',
}


def generate_chapter_html(chapter, prev_chapter=None, next_chapter=None):
    """Generate HTML for a single chapter"""
    content_html = format_content(chapter.get('content', ''))

    # Image
    img_file = chapter_images.get(chapter['id'], '')
    img_html = ''
    if img_file:
        img_html = f'<img src="images/{img_file}" alt="Иллюстрация к главе" class="chapter-image" onload="this.classList.add(\'loaded\')" loading="lazy">'

    # Navigation
    nav_html = '<div class="chapter-nav">'
    if prev_chapter:
        nav_html += f'<a href="#{prev_chapter["id"]}">← {prev_chapter["title"]}</a>'
    else:
        nav_html += '<span></span>'
    if next_chapter:
        nav_html += f'<a href="#{next_chapter["id"]}">{next_chapter["title"]} →</a>'
    else:
        nav_html += '<span></span>'
    nav_html += '</div>'

    return f'''
    <section class="chapter {chapter['type']} reveal" id="{chapter['id']}">
        <div class="chapter-header">
            <p class="chapter-part">{chapter['part']}</p>
            <h2 class="chapter-title">{chapter['title']}</h2>
            <p class="chapter-subtitle">{chapter['subtitle']}</p>
            {f'<p class="chapter-meta">{chapter["meta"]}</p>' if chapter.get('meta') else ''}
        </div>
        {img_html}
        <div class="chapter-content">
            {content_html}
        </div>
        {nav_html}
    </section>
'''


def update_book():
    """Update book content"""
    # Read markdown
    with open('../ХРОНИСТ_v3_БЕСТСЕЛЛЕР.md', 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Parse chapters
    chapters = parse_markdown(md_content)
    print(f"Found {len(chapters)} chapters")

    # Generate HTML for each chapter
    chapters_html = []
    for i, chapter in enumerate(chapters):
        prev_ch = chapters[i-1] if i > 0 else None
        next_ch = chapters[i+1] if i < len(chapters)-1 else None
        chapters_html.append(generate_chapter_html(chapter, prev_ch, next_ch))
        print(f"  - {chapter['title']}: {chapter.get('subtitle', '')}")

    all_chapters = '\n'.join(chapters_html)

    # Read current HTML
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Replace content between chapters-container tags
    pattern = r'(<div id="chapters-container">).*?(</div>\s*</main>)'
    replacement = f'\\1{all_chapters}\\2'

    new_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

    # Write updated HTML
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"\nBook updated successfully!")
    print(f"Total chapters: {len(chapters)}")


if __name__ == '__main__':
    update_book()
