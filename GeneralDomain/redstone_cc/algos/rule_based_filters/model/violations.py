from typing import List

from .document import Document


class Violations:
    def __init__(self):
        self.doc_violations = set()
        self.line_violations = {}
        self.excluded_lines = set()

    def doc(self, key):
        if key in self.doc_violations:
            raise KeyError(f"Document violation {key} has already been set")
        self.doc_violations.add(key)

    def line(self, key, lines: List[int]):
        if key in self.line_violations:
            raise KeyError(f"Line violation {key} has already been set")
        lines = list(set(lines))
        lines.sort()
        self.line_violations[key] = lines
        self.excluded_lines.update(lines)

    def apply_to_doc(self, doc: Document) -> str | None:
        if len(self.doc_violations) > 0:
            return None

        res = []
        for i, line in enumerate(doc.sents):
            if i not in self.excluded_lines:
                res.append(line)
        return "\n".join(res)
