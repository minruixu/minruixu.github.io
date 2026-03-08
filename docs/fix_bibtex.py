import os

pub_dir = '_publications'
for filename in os.listdir(pub_dir):
    if not filename.endswith('.md'):
        continue
    filepath = os.path.join(pub_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The issue here is we want to ensure Bibtex is updated or the order of buttons in the layout is all that's needed.
    # The layout change I just did puts `Paper` button before `BibTeX` button in _includes/archive-single.html.
    # So I don't need to change markdown files for this.
print("Done")
