from dataclasses import dataclass, field
from typing import List, Optional

# Structures to hold patch notes
@dataclass
class PatchNote:
    title: str
    date: str
    url: Optional[str]
    content: str  

@dataclass
class GameData:
    app_id: str
    count: int
    notes: List[PatchNote] = field(default_factory=list)

    @classmethod
    def process_instance(cls, raw_data: dict):

        # loop over notes and create PatchNote instances
        notes = [
            PatchNote(
                title=note.get("title"),
                date=note.get("date"),
                url=note.get("url"),
                content=note.get("content","")
            )
            for note in raw_data.get("notes", [])
        ]
        return cls(
            app_id=raw_data.get("appId"),
            count=raw_data.get("count", 0),
            notes=notes
        )
