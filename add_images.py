#!/usr/bin/env python3
"""Add images to the CHRONIST HTML book"""
import re

# Read HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add CSS for chapter images
image_css = '''
        /* CHAPTER IMAGES */
        .chapter-image {
            width: 100%;
            max-width: 800px;
            margin: 0 auto 3rem;
            display: block;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), 0 0 40px rgba(212, 175, 55, 0.2);
            opacity: 0;
            transform: scale(0.95);
            transition: all 0.8s ease;
        }

        .chapter-image.loaded {
            opacity: 1;
            transform: scale(1);
        }

        .hero-cover {
            max-width: 400px;
            margin: 2rem auto;
            border-radius: 16px;
            box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(212, 175, 55, 0.3);
        }

        @media (max-width: 768px) {
            .chapter-image {
                border-radius: 8px;
            }
            .hero-cover {
                max-width: 280px;
            }
        }
'''

# Insert CSS before closing </style>
html = html.replace('    </style>', image_css + '\n    </style>')

# Add cover image to hero section
hero_cover = '''
        <img src="images/cover.png" alt="ХРОНИСТ - Обложка" class="hero-cover chapter-image" onload="this.classList.add('loaded')">
'''
html = html.replace(
    '<p class="hero-tagline">',
    hero_cover + '\n        <p class="hero-tagline">'
)

# Map of chapter IDs to image files
chapter_images = {
    'prologue': 'prologue.png',
    'ch1': 'ch1.png',
    'ch2': 'ch2.png',
    'ch3': 'ch3.png',
    'ch4': 'ch4.png',
    'ch5': 'ch5.png',
    'ch6': 'ch6.png',
    'ch7': 'ch7.png',
    'ch8': 'ch8.png',
    'interlude1': 'interlude1.png',
    'ch9': 'ch9.png',
    'ch10': 'ch10.png',
    'ch11': 'ch11.png',
    'ch12': 'ch12.png',
    'ch13': 'ch13.png',
    'ch14': 'ch14.png',
    'ch15': 'ch15.png',
    'ch16': 'ch16.png',
    'interlude2': 'interlude2.png',
    'ch17': 'ch17.png',
    'ch18': 'ch18.png',
    'ch19': 'ch19.png',
    'ch19b': 'ch19b.png',
    'ch20': 'ch20.png',
    'ch21': 'ch21.png',
    'ch22': 'ch22.png',
    'ch23': 'ch23.png',
    'epilogue': 'epilogue.png',
}

# Add images after each chapter header
for chapter_id, img_file in chapter_images.items():
    # Pattern to find the chapter header closing div
    pattern = rf'(id="{chapter_id}"[^>]*>.*?</div>\s*<div class="chapter-content">)'

    def add_image(match):
        return match.group(1).replace(
            '<div class="chapter-content">',
            f'<img src="images/{img_file}" alt="Иллюстрация к главе" class="chapter-image" onload="this.classList.add(\'loaded\')" loading="lazy">\n        <div class="chapter-content">'
        )

    html = re.sub(pattern, add_image, html, flags=re.DOTALL)

# Write updated HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Images added successfully!")
print(f"Added {len(chapter_images)} chapter images + cover")
