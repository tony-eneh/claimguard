from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


LATEX_ENV_STRIP = [
    "figure",
    "table",
    "lstlisting",
    "algorithm",
]


@dataclass
class SectionStat:
    title: str
    level: str  # section/subsection/subsubsection
    words: int
    start_line: int


def strip_environments(tex: str) -> str:
    for env in LATEX_ENV_STRIP:
        tex = re.sub(
            rf"\\\\begin\{{{re.escape(env)}\}}[\s\S]*?\\\\end\{{{re.escape(env)}\}}",
            " ",
            tex,
            flags=re.IGNORECASE,
        )
    return tex


def rough_word_count(tex: str) -> int:
    tex = re.sub(r"%.*", "", tex)
    tex = strip_environments(tex)
    tex = re.sub(r"\\\\cite\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\\\(ref|label|url|href)\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\\\[A-Za-z@]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", tex)
    tex = re.sub(r"[{}]", " ", tex)
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-']+", tex)
    return len(words)


def main() -> None:
    paper = Path(__file__).resolve().parent / "paper.tex"
    raw = paper.read_text(encoding="utf-8", errors="ignore")
    lines = raw.splitlines()

    # Capture \section and \subsection headings with line numbers
    heading_re = re.compile(r"^(\\section|\\subsection|\\subsubsection)\{(.+)\}\s*$")
    headings: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines, start=1):
        m = heading_re.match(line.strip())
        if m:
            cmd, title = m.group(1), m.group(2)
            level = cmd.lstrip("\\")
            headings.append((i, level, title))

    stats: list[SectionStat] = []
    for idx, (start_line, level, title) in enumerate(headings):
        end_line = headings[idx + 1][0] - 1 if idx + 1 < len(headings) else len(lines)
        chunk = "\n".join(lines[start_line - 1 : end_line])
        stats.append(SectionStat(title=title, level=level, words=rough_word_count(chunk), start_line=start_line))

    print(f"Detected headings: {len(stats)}")
    print("Top sections by rough word count (excluding figures/tables/listings):")
    for st in sorted(stats, key=lambda s: s.words, reverse=True)[:15]:
        print(f"- {st.level:13} L{st.start_line:4d}  {st.words:5d}  {st.title}")


if __name__ == "__main__":
    main()
