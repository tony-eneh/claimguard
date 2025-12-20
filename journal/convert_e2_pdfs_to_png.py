from __future__ import annotations

from pathlib import Path

import fitz  # pymupdf


def pdf_to_png(pdf_path: Path, dpi: int = 300) -> Path:
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    doc = fitz.open(pdf_path)
    try:
        if doc.page_count < 1:
            raise ValueError(f"No pages in {pdf_path}")
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        out_path = pdf_path.with_suffix(".png")
        pix.save(out_path)
        return out_path
    finally:
        doc.close()


def main() -> None:
    figures_dir = Path(__file__).resolve().parent / "figures"
    pdfs = [
        figures_dir / "e2_latency_comparison.pdf",
        figures_dir / "e2_throughput_comparison.pdf",
        figures_dir / "e2_policy_comparison.pdf",
    ]

    missing = [p for p in pdfs if not p.exists()]
    if missing:
        raise SystemExit("Missing PDFs:\n" + "\n".join(str(p) for p in missing))

    for pdf in pdfs:
        out = pdf_to_png(pdf, dpi=300)
        print(f"Wrote {out.name}")


if __name__ == "__main__":
    main()
