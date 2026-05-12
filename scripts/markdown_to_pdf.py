#!/usr/bin/env python3
"""Generate a simple A4 PDF from a Markdown file using only the stdlib."""

from __future__ import annotations

import argparse
import textwrap
from pathlib import Path


PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT = 56
TOP = 790
BOTTOM = 54
LINE_HEIGHT = 14
TITLE_SIZE = 16
BODY_SIZE = 10
FONT = "Helvetica"
MAX_CHARS = 92


def clean_line(line: str) -> tuple[str, int]:
    stripped = line.strip()
    if not stripped:
        return "", BODY_SIZE

    if stripped.startswith("# "):
        return stripped[2:].strip(), TITLE_SIZE
    if stripped.startswith("## "):
        return stripped[3:].strip(), 13
    if stripped.startswith("### "):
        return stripped[4:].strip(), 12
    if stripped.startswith("- "):
        return f"* {stripped[2:].strip()}", BODY_SIZE
    if stripped.startswith("  - "):
        return f"  * {stripped[4:].strip()}", BODY_SIZE

    return stripped.replace("`", ""), BODY_SIZE


def escape_pdf_text(value: str) -> str:
    normalized = value.encode("latin-1", errors="replace").decode("latin-1")
    return normalized.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def paginate(lines: list[str]) -> list[list[tuple[str, int]]]:
    pages: list[list[tuple[str, int]]] = [[]]
    y = TOP

    for raw_line in lines:
        cleaned, size = clean_line(raw_line)

        if not cleaned:
            if y - LINE_HEIGHT < BOTTOM:
                pages.append([])
                y = TOP
            else:
                pages[-1].append(("", BODY_SIZE))
                y -= LINE_HEIGHT
            continue

        wrap_width = 70 if size > BODY_SIZE else MAX_CHARS
        wrapped = textwrap.wrap(cleaned, width=wrap_width) or [cleaned]

        for index, part in enumerate(wrapped):
            if y - LINE_HEIGHT < BOTTOM:
                pages.append([])
                y = TOP
            line_size = size if index == 0 else BODY_SIZE
            pages[-1].append((part, line_size))
            y -= LINE_HEIGHT + (4 if line_size > BODY_SIZE else 0)

    return pages


def page_stream(lines: list[tuple[str, int]]) -> bytes:
    y = TOP
    commands = ["BT", f"/F1 {BODY_SIZE} Tf"]

    for text, size in lines:
        if text:
            commands.append(f"/F1 {size} Tf")
            commands.append(f"1 0 0 1 {LEFT} {y} Tm")
            commands.append(f"({escape_pdf_text(text)}) Tj")
        y -= LINE_HEIGHT + (4 if size > BODY_SIZE else 0)

    commands.append("ET")
    return ("\n".join(commands) + "\n").encode("latin-1", errors="replace")


def build_pdf(markdown: str) -> bytes:
    pages = paginate(markdown.splitlines())
    objects: list[bytes] = []

    def add_object(content: bytes) -> int:
        objects.append(content)
        return len(objects)

    catalog_id = add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add_object(b"")
    font_id = add_object(f"<< /Type /Font /Subtype /Type1 /BaseFont /{FONT} >>".encode())

    page_ids: list[int] = []
    for page in pages:
        stream = page_stream(page)
        stream_id = add_object(
            b"<< /Length "
            + str(len(stream)).encode()
            + b" >>\nstream\n"
            + stream
            + b"endstream"
        )
        page_id = add_object(
            (
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
                f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
                f"/Contents {stream_id} 0 R >>"
            ).encode()
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id, content in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode())
        output.extend(content)
        output.extend(b"\nendobj\n")

    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode())
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())

    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            "startxref\n"
            f"{xref_start}\n"
            "%%EOF\n"
        ).encode()
    )
    return bytes(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    markdown = args.input.read_text(encoding="utf-8")
    args.output.write_bytes(build_pdf(markdown))


if __name__ == "__main__":
    main()
