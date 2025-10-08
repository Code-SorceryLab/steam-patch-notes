import re

# Converts HTML code to plain text
def strip_html(s: str) -> str:
    if not s:
        return ""
    import html
    s = html.unescape(s)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.IGNORECASE)
    s = re.sub(r"<[^>]+>", "", s)  
    s = re.sub(r"\[/?(b|i|u|quote|list|\*|url|img|h[1-6])(?:=[^\]]+)?\]", "", s, flags=re.IGNORECASE)
    # s = re.sub(r"\n{3,}", "\n\n", s)
    s = s.replace("[p]", "\n").replace("[/p]", "\n")
    # s = s.sub(r"[p]|[/p]", "\n",s)
    return s.strip()

# Filtering to identify patch notes
def is_patch_note(title: str, contents: str) -> bool:
    
    keywords = re.compile(r"\b(patch|update|hotfix|release|version|release notes?|changelog|changes|bug\s*fix(es)?)\b",re.IGNORECASE)
    
    if keywords.search(title or ""):
        return True
    
    return bool(keywords.search(contents) or re.search(r"(^|\n)\s*(?:- |\* |• )", contents))



        # With HTML strip funtion
        # content = strip_html(item.get("contents", ""))
        
                # Regex cleaning
        # if is_patch_note(title,content):