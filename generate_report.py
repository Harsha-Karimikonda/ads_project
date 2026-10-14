"""
COP 5536 Fall 2026 Programming Project - Job Scheduler
generate_report.py: Generates the project PDF report (report.pdf)
Pure Python implementation with no external dependencies.
"""

import os
import sys

class PDFCanvas:
    """A minimal, self-contained PDF generator for structured reports."""
    def __init__(self):
        self.pages = []
        self.current_commands = []
        self.page_width = 612
        self.page_height = 792
        self.margin = 54  # 0.75 in
        self.y = self.page_height - self.margin

    def new_page(self):
        if self.current_commands:
            self.pages.append("\n".join(self.current_commands))
            self.current_commands = []
        self.y = self.page_height - self.margin

    def check_page_break(self, needed_space=30):
        if self.y < self.margin + needed_space:
            self.new_page()

    def draw_line(self, x1, y1, x2, y2, r=0.7, g=0.7, b=0.7, width=1):
        self.current_commands.append(f"{r} {g} {b} RG {width} w {x1} {y1} m {x2} {y2} l S")

    def draw_rect(self, x, y, w, h, fill_r=0.95, fill_g=0.95, fill_b=0.95, stroke=False):
        cmd = f"{fill_r} {fill_g} {fill_b} rg {x} {y} {w} {h} re f"
        self.current_commands.append(cmd)

    def draw_text(self, text, font="F1", size=10, x=54, y=None, r=0.1, g=0.1, b=0.1):
        if y is None:
            y = self.y
        # Escape parenthesis
        clean_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        self.current_commands.append(f"BT /{font} {size} Tf {r} {g} {b} rg {x} {y} Td ({clean_text}) Tj ET")

    def add_title(self, title, subtitle=None):
        self.draw_rect(self.margin, self.y - 45, self.page_width - 2 * self.margin, 55, 0.92, 0.94, 0.98)
        self.draw_line(self.margin, self.y - 45, self.page_width - self.margin, self.y - 45, 0.2, 0.4, 0.7, width=2)
        self.draw_text(title, font="F2", size=16, x=self.margin + 12, y=self.y - 20, r=0.1, g=0.2, b=0.45)
        if subtitle:
            self.draw_text(subtitle, font="F1", size=10, x=self.margin + 12, y=self.y - 36, r=0.3, g=0.35, b=0.45)
        self.y -= 60

    def add_section_header(self, text):
        self.check_page_break(40)
        self.y -= 14
        self.draw_text(text, font="F2", size=12, x=self.margin, y=self.y, r=0.12, g=0.25, b=0.55)
        self.draw_line(self.margin, self.y - 4, self.page_width - self.margin, self.y - 4, 0.8, 0.85, 0.92, width=1)
        self.y -= 14

    def add_subsection_header(self, text):
        self.check_page_break(25)
        self.y -= 8
        self.draw_text(text, font="F2", size=10.5, x=self.margin, y=self.y, r=0.15, g=0.15, b=0.2)
        self.y -= 12

    def add_paragraph(self, text, indent=0, font="F1", size=9.5, line_spacing=13, r=0.15, g=0.15, b=0.15):
        max_chars = 95 - int(indent / 6)
        words = text.split()
        lines = []
        curr = []
        curr_len = 0
        for w in words:
            if curr_len + len(w) + 1 > max_chars:
                lines.append(" ".join(curr))
                curr = [w]
                curr_len = len(w)
            else:
                curr.append(w)
                curr_len += len(w) + 1
        if curr:
            lines.append(" ".join(curr))

        for l in lines:
            self.check_page_break(line_spacing + 5)
            self.draw_text(l, font=font, size=size, x=self.margin + indent, y=self.y, r=r, g=g, b=b)
            self.y -= line_spacing

    def add_bullet(self, bold_prefix, text, indent=12):
        self.check_page_break(25)
        prefix_len = len(bold_prefix)
        self.draw_text("-", font="F2", size=9.5, x=self.margin + indent - 10, y=self.y, r=0.2, g=0.4, b=0.7)
        self.draw_text(bold_prefix, font="F2", size=9.5, x=self.margin + indent, y=self.y, r=0.15, g=0.15, b=0.2)
        
        # Draw remainder of text
        rem_x = self.margin + indent + int(prefix_len * 5.5) + 3
        # Simple line wrap
        max_chars = 92 - int(indent / 6)
        words = text.split()
        first_line_chars = max_chars - prefix_len
        curr = []
        curr_len = 0
        lines = []
        for w in words:
            target_limit = first_line_chars if not lines else max_chars
            if curr_len + len(w) + 1 > target_limit:
                lines.append(" ".join(curr))
                curr = [w]
                curr_len = len(w)
            else:
                curr.append(w)
                curr_len += len(w) + 1
        if curr:
            lines.append(" ".join(curr))

        if lines:
            self.draw_text(lines[0], font="F1", size=9.5, x=rem_x, y=self.y, r=0.2, g=0.2, b=0.2)
            self.y -= 13
            for l in lines[1:]:
                self.check_page_break(18)
                self.draw_text(l, font="F1", size=9.5, x=self.margin + indent, y=self.y, r=0.2, g=0.2, b=0.2)
                self.y -= 13
        else:
            self.y -= 13

    def save(self, filename="report.pdf"):
        if self.current_commands:
            self.pages.append("\n".join(self.current_commands))
            self.current_commands = []

        total_pages = len(self.pages)
        objects = []
        def add_obj(content):
            objects.append(content)
            return len(objects)

        # 1: Catalog
        add_obj("<< /Type /Catalog /Pages 2 0 R >>")
        
        # 2: Pages
        page_refs = [f"{i + 3} 0 R" for i in range(total_pages)]
        add_obj(f"<< /Type /Pages /Kids [{' '.join(page_refs)}] /Count {total_pages} >>")

        # Fonts (Helvetica, Helvetica-Bold, Courier)
        font_f1 = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font_f2 = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        font_f3 = add_obj("<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")

        # For each page, create content stream and page object
        for page_idx, stream_text in enumerate(self.pages):
            # Page footer
            footer_text = f"Page {page_idx + 1} of {total_pages}"
            full_stream = (
                f"{stream_text}\n"
                f"BT /F1 8 Tf 0.5 0.5 0.5 rg {self.page_width - self.margin - 50} 30 Td ({footer_text}) Tj ET\n"
                f"BT /F1 8 Tf 0.5 0.5 0.5 rg {self.margin} 30 Td (COP 5536 Fall 2026 - Advanced Data Structures Project Report) Tj ET\n"
                f"0.8 0.8 0.8 RG 0.5 w {self.margin} 42 m {self.page_width - self.margin} 42 l S"
            )
            stream_obj = add_obj(f"<< /Length {len(full_stream.encode('latin1'))} >>\nstream\n{full_stream}\nendstream")
            add_obj(
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.page_width} {self.page_height}] "
                f"/Contents {stream_obj} 0 R /Resources << /Font << /F1 {font_f1} 0 R /F2 {font_f2} 0 R /F3 {font_f3} 0 R >> >> >>"
            )

        # Update Pages object with actual Page IDs
        actual_page_objs = [f"{i} 0 R" for i in range(len(objects) - 2 * total_pages + 2, len(objects) + 1, 2)]
        # Replace Pages object content
        objects[1] = f"<< /Type /Pages /Kids [{' '.join(actual_page_objs)}] /Count {total_pages} >>"

        # Serialize PDF
        pdf_bytes = ["%PDF-1.4\n%\\xe2\\xe3\\xcf\\xd3\n".encode("latin1")]
        offsets = []
        current_offset = len(pdf_bytes[0])

        for i, obj in enumerate(objects, 1):
            offsets.append(current_offset)
            s = f"{i} 0 obj\n{obj}\nendobj\n"
            b = s.encode("latin1")
            pdf_bytes.append(b)
            current_offset += len(b)

        xref_offset = current_offset
        xref = [f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"]
        for off in offsets:
            xref.append(f"{off:010d} 00000 n \n")
        trailer = f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
        pdf_bytes.append("".join(xref).encode("latin1"))
        pdf_bytes.append(trailer.encode("latin1"))

        with open(filename, "wb") as f:
            for chunk in pdf_bytes:
                f.write(chunk)
        print(f"Generated {filename} successfully ({total_pages} pages).")


def build_report():
    pdf = PDFCanvas()

    # Title Banner
    pdf.add_title(
        "COP 5536 Fall 2026: Job Scheduler Project Report",
        "Author: Student | Language: Python 3 | Architecture & Implementation Summary"
    )

    # 1. Program Organization
    pdf.add_section_header("1. Program Organization & Modular Architecture")
    pdf.add_paragraph(
        "The project is structured in a strictly decoupled, modular architecture adhering to submission requirements. "
        "The primary data structures are isolated into separate standalone modules completely independent of scheduler "
        "logic and input parsing, allowing independent inspection and verification by automated grading harnesses."
    )
    pdf.y -= 4
    pdf.add_bullet("job.py: ", "Defines the Job entity with unique identifier, priority, execution time estimates, delta offsets, timestamps, and lifecycle states (WAITING, RUNNING, COMPLETED, CANCELLED).")
    pdf.add_bullet("avl_tree.py: ", "Implements a complete self-balancing AVL Tree from scratch, keyed by job_id. Maintains node references to Job objects, tracks rotation counts, and provides tree-shape level-order output.")
    pdf.add_bullet("max_heap.py: ", "Implements an array-based Binary Max Heap from scratch for WAITING jobs. Includes position indexing for O(log n) removals/updates, dual scheduling modes, and bottom-up rebuilds.")
    pdf.add_bullet("jobScheduler.py: ", "The central discrete-event simulation driver. Coordinates capacity constraints (k), advances the simulation clock, manages running job completions, and dispatches commands.")
    pdf.add_bullet("test_scheduler.py: ", "Test harness verifying all cases from TestCases.docx and comprehensive rotation/edge-case tests.")
    pdf.add_bullet("Makefile: ", "Prepares execution permissions, compiles Python bytecode, and exposes clean and test targets.")

    # 2. Classes and Modules
    pdf.add_section_header("2. Classes and Data Structures Overview")
    pdf.add_subsection_header("2.1 Job Entity (job.py)")
    pdf.add_paragraph(
        "Every submitted job is instantiated as exactly one Job object, which is then shared via direct reference across "
        "the AVL Tree, Binary Max Heap, Running Priority Queue, and Cancelled List. State transitions (start, complete, "
        "cancel) update the object in-place, eliminating redundant records across the system."
    )
    pdf.y -= 4

    pdf.add_subsection_header("2.2 AVL Tree (avl_tree.py)")
    pdf.add_paragraph(
        "The AVL Tree serves as the primary dictionary for all active (non-cancelled) jobs, keyed by job_id. Each node "
        "records its subtree height. The balance factor is computed as BF = height(left) - height(right). Whenever |BF| > 1 "
        "after an insertion or deletion, the tree restores balance using primitive left and right rotations. "
        "Four rebalancing cases are handled: Left-Left (single right rotation), Right-Right (single left rotation), "
        "Left-Right (left rotation on child followed by right rotation on parent), and Right-Left (right rotation on child "
        "followed by left rotation on parent). Counters for primitive left and right rotations are explicitly tracked. "
        "Deletion replaces internal nodes with their inorder successor (minimum node of the right subtree)."
    )

    # 3. Data Structure Representations (Page break as needed)
    pdf.add_section_header("3. Data Structure Representations & Mechanics")
    pdf.add_subsection_header("3.1 Binary Max Heap & Priority Inversion Tracking (max_heap.py)")
    pdf.add_paragraph(
        "The waiting queue is implemented as a Binary Max Heap using a 0-indexed flat list. For any element at index i, "
        "its parent is located at floor((i - 1) / 2) and its children at 2i + 1 and 2i + 2. "
        "Crucially, the Max Heap maintains an internal hash map (pos: job_id -> index) that is updated on every element "
        "swap. This enables O(log n) arbitrary job cancellations (remove) and priority updates (update_priority) without "
        "resorting to O(n) linear scans. The heap supports two scheduling rankings:"
    )
    pdf.y -= 4
    pdf.add_bullet("PRIORITY Mode: ", "Higher priority > earlier submission time > smaller job_id.")
    pdf.add_bullet("SHORT_JOBS Mode: ", "Smaller estimated_time > higher priority > earlier submission time > smaller job_id.")
    pdf.add_paragraph(
        "When the SHORT_JOBS command is encountered, the heap switches mode permanently and executes a linear-time "
        "bottom-up heapify (rebuild) starting from floor(n/2) - 1 down to 0, incrementing the rebuilds statistic."
    )

    pdf.add_subsection_header("3.2 Running Jobs & Discrete Event Simulation")
    pdf.add_paragraph(
        "Concurrency is strictly constrained to at most k RUNNING jobs. Running jobs are tracked in a Min-Heap priority "
        "queue ordered by completion time. Before processing any command at timestamp t, the simulation clock advances and "
        "all running jobs with completion time <= clock are marked COMPLETED, freeing capacity slots. "
        "When PROCESS_NEXT is invoked at capacity, the clock fast-forwards to the earliest completion time among running jobs, "
        "completes those jobs simultaneously, and immediately launches the next highest-ranking waiting job."
    )

    # 4. Additional Libraries
    pdf.add_section_header("4. External and Standard Libraries Used")
    pdf.add_paragraph(
        "In accordance with project guidelines, the program relies strictly on default Python 3 standard library modules, "
        "guaranteeing 100% portable out-of-the-box execution on any standard Ubuntu LTS installation:"
    )
    pdf.y -= 4
    pdf.add_bullet("heapq (standard library): ", "Used exclusively to maintain the Min-Heap priority queue tracking the completion times of RUNNING jobs, as explicitly permitted by the project specification.")
    pdf.add_bullet("list (standard library): ", "Used for the Cancelled Jobs List to preserve FIFO cancellation order.")
    pdf.add_bullet("sys, os (standard library): ", "Used for command-line arguments and input/output file path management.")
    pdf.add_paragraph(
        "No third-party packages (such as NumPy, PyPI packages, or external binary dependencies) are used."
    )

    pdf.save("report.pdf")


if __name__ == "__main__":
    build_report()
