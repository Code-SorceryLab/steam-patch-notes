from pathlib import Path
import json
import re

class GameData:
    def __init__(self, data):
        self.data = data
    
    # Creating instance using cls
    @classmethod    
    def from_file(cls, file_path):
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)
    
    def filter_notes(self):
        """_summary_
            Filters notes in self.data to retain only patch notes based on title and contents.
            Loops over the notes and applies is_patch_note to each note.
            Updates self.data['notes'] and self.data['total_notes'] accordingly.
        """
        self.data['notes'] = [note for note in self.data.get("notes") if self.is_patch_note(note.get("title", ""), note.get("contents", ""))]
        self.data["total_notes"] = len(self.data["notes"])

    def is_patch_note(self, title, contents):
        
        keywords = re.compile(r"\b(patch|update|hotfix|release|version|release notes?|changelog|changes|bug\s*fix(es)?)\b",re.IGNORECASE)
            
        if keywords.search(title or ""):
            return True
        return bool(keywords.search(contents) or re.search(r"(^|\n)\s*(?:- |\* |• )", contents))

    def html_to_text(self):
        for note in self.data["notes"]:
            content = note["notes"]
            note["notes"] = self.strip_html(content)
    
    # Converts HTML code to plain text
    @staticmethod
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