import os
import re

pub_dir = '_publications'
for filename in os.listdir(pub_dir):
    if not filename.endswith('.md'):
        continue
    filepath = os.path.join(pub_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split frontmatter and body
    parts = content.split('---', 2)
    if len(parts) >= 3:
        frontmatter = parts[1]
        body = parts[2]
        
        # Find the tag in body, e.g., **[ToN]**
        tag_match = re.search(r'\*\*(\[.*?\])\*\*', body)
        if tag_match:
            tag = tag_match.group(1)
            
            # Check if title already has the tag
            # Frontmatter title might be: title: "Title" or title: Title
            title_match = re.search(r'^title:\s*(.*)$', frontmatter, re.MULTILINE)
            if title_match:
                old_title_line = title_match.group(0)
                title_content = title_match.group(1).strip()
                
                # Strip quotes if present
                has_quotes = False
                if title_content.startswith('"') and title_content.endswith('"'):
                    title_content = title_content[1:-1]
                    has_quotes = True
                elif title_content.startswith("'") and title_content.endswith("'"):
                    title_content = title_content[1:-1]
                    has_quotes = True
                
                if not title_content.startswith(tag):
                    new_title_content = f"{tag} {title_content}"
                    if has_quotes:
                        new_title_line = f'title: "{new_title_content}"'
                    else:
                        new_title_line = f'title: {new_title_content}'
                    
                    frontmatter = frontmatter.replace(old_title_line, new_title_line)
        
        # We want to remove the body entirely since it just duplicates the title/author/venue
        # OR we can just remove the excerpt in the HTML layout. But removing the body is safer 
        # and cleans up the files.
        new_content = f"---{frontmatter}---"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

print("Done fixing publications.")
