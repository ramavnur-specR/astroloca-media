# Astroloca quote-card template (locked 31 Oct 2026)
Collectible deck style: night-sky background, parchment card, navy ink (#1F3B4D), Marcellus font, number + label (ASK YOURSELF / TRY THIS), planet sticker, element at the bottom (fire/earth/air/water sets the accent colour), real logo bottom right. 1080x1350 (4:5), so no cropping.

Setup: `cd tools/cards && npm install` (fonts: @fontsource/marcellus, space-mono)
Render: `python3 render_card.py '[{"num":7,"kind":"question","element":"earth","line":"... <em>accent words</em>","out":"card.png","size":90}]'`
- kind: question | practice (practice adds a "tried it" checkbox)
- size: font px; ~90 for 10–12 words, ~104 for 8–9 words. Check the render visually.
