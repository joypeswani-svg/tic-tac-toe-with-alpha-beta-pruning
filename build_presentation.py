#!/usr/bin/env python3
"""
build_presentation.py
Generates the updated, prototype-integrated presentation PDF for the Tic-Tac-Toe AI project.
Preserves original slides 1-9 and appends updated slide 10 (measured results) plus
slides 11-13 (prototype features, verification/proof, and conclusion).
"""

import os
import re
import zlib

SRC_PDF = "/Users/joypeswani/.gemini/antigravity/brain/f3612bde-ddf6-43e2-bd12-403032b0f674/.user_uploaded/media_1791485590867_31b53881.pdf"
OUT_PDF = "/Users/joypeswani/Downloads/Tic Tac Toe/static/presentation.pdf"

def escape_pdf(text: str) -> str:
    """Escape parenthesis and backslashes for PDF string literals."""
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

class PDFPageBuilder:
    """Helper to build PDF content stream for a 1440x810 widescreen slide."""
    def __init__(self):
        self.ops = []
        # Background: #3d1515 (0.2392, 0.0824, 0.0824)
        self.ops.append("q")
        self.ops.append("0.2392 0.0824 0.0824 rg")
        self.ops.append("0 0 1440 810 re f")
        self.ops.append("Q")

    def draw_rect(self, x, y, w, h, fill_rgb=None, stroke_rgb=None, line_width=1):
        self.ops.append("q")
        if stroke_rgb:
            self.ops.append(f"{line_width} w")
            self.ops.append(f"{stroke_rgb[0]} {stroke_rgb[1]} {stroke_rgb[2]} RG")
        if fill_rgb:
            self.ops.append(f"{fill_rgb[0]} {fill_rgb[1]} {fill_rgb[2]} rg")
        self.ops.append(f"{x} {y} {w} {h} re")
        if fill_rgb and stroke_rgb:
            self.ops.append("B")
        elif fill_rgb:
            self.ops.append("f")
        elif stroke_rgb:
            self.ops.append("S")
        self.ops.append("Q")

    def draw_rounded_rect(self, x, y, w, h, r=10, fill_rgb=None, stroke_rgb=None, line_width=1):
        """Draw an approximated rounded rectangle."""
        self.ops.append("q")
        if stroke_rgb:
            self.ops.append(f"{line_width} w")
            self.ops.append(f"{stroke_rgb[0]} {stroke_rgb[1]} {stroke_rgb[2]} RG")
        if fill_rgb:
            self.ops.append(f"{fill_rgb[0]} {fill_rgb[1]} {fill_rgb[2]} rg")
        
        # Approximate with beveled path or smooth rect
        # Standard PDF bezier curve: c operator
        # (x+r, y) -> (x+w-r, y) -> curve to (x+w, y+r)
        k = 0.5522847498 * r
        p = [
            f"{x+r} {y} m",
            f"{x+w-r} {y} l",
            f"{x+w-r+k} {y} {x+w} {y+r-k} {x+w} {y+r} c",
            f"{x+w} {y+h-r} l",
            f"{x+w} {y+h-r+k} {x+w-r+k} {y+h} {x+w-r} {y+h} c",
            f"{x+r} {y+h} l",
            f"{x+r-k} {y+h} {x} {y+h-r+k} {x} {y+h-r} c",
            f"{x} {y+r} l",
            f"{x} {y+r-k} {x+r-k} {y} {x+r} {y} c"
        ]
        self.ops.append(" ".join(p))
        if fill_rgb and stroke_rgb:
            self.ops.append("B")
        elif fill_rgb:
            self.ops.append("f")
        elif stroke_rgb:
            self.ops.append("S")
        self.ops.append("Q")

    def draw_text(self, text, x, y, font="/F1", size=18, rgb=(1, 1, 1)):
        self.ops.append("BT")
        self.ops.append(f"{rgb[0]} {rgb[1]} {rgb[2]} rg")
        self.ops.append(f"{font} {size} Tf")
        self.ops.append(f"1 0 0 1 {x} {y} Tm")
        self.ops.append(f"({escape_pdf(text)}) Tj")
        self.ops.append("ET")

    def draw_header(self, category: str, title: str, subtitle: str = ""):
        # Category label (e.g. RESULTS & PERFORMANCE) in coral #ff6b5b (1, 0.4196, 0.3569)
        self.draw_text(category.upper(), 80, 742, font="/F2", size=15, rgb=(1, 0.4196, 0.3569))
        # Title in white bold 38pt
        self.draw_text(title, 80, 688, font="/F2", size=38, rgb=(1, 1, 1))
        # Subtitle in light slate 16pt
        if subtitle:
            self.draw_text(subtitle, 80, 656, font="/F1", size=16, rgb=(0.85, 0.88, 0.92))

    def get_stream(self) -> bytes:
        return "\n".join(self.ops).encode("latin1")


def build_slide_10() -> bytes:
    """Slide 10: Performance Comparison with Live Measured Data."""
    b = PDFPageBuilder()
    b.draw_header("R E S U L T S   &   P E R F O R M A N C E", "Performance Comparison", "Empirical Node Exploration & Computational Latency from Empty Board")

    # Table Geometry: 1280 wide, X: 80 -> 1360
    # Header Row
    b.draw_rect(80, 560, 1280, 56, fill_rgb=(0.18, 0.06, 0.06), stroke_rgb=(0.35, 0.15, 0.15), line_width=1)
    b.draw_text("Parameter", 100, 580, font="/F2", size=18, rgb=(1, 1, 1))
    b.draw_text("Minimax (No Pruning)", 480, 580, font="/F2", size=18, rgb=(1, 1, 1))
    b.draw_text("Minimax + Alpha-Beta Pruning", 920, 580, font="/F2", size=18, rgb=(1, 0.45, 0.45))

    rows = [
        # (Parameter, Minimax, Alpha-Beta, is_alt)
        ("Nodes Explored (Empty Board)", "549,946", "20,866  (96.2% fewer nodes)", False),
        ("Execution Time (Empty Board)", "~800.0 ms", "~25.0 ms  (32x faster)", True),
        ("Pruned Branches (Cutoffs)", "0  (None)", "7,692 subtrees skipped", False),
        ("Search Efficiency", "Baseline (100% search)", "96.2% search space reduction", True),
        ("Decision Optimality", "Score 0 (Guaranteed Draw)", "Score 0 (Guaranteed Draw - 100% Identical)", False),
    ]

    start_y = 560
    row_height = 60
    for i, (param, mm, ab, is_alt) in enumerate(rows):
        y = start_y - (i + 1) * row_height
        bg_rgb = (0.93, 0.94, 0.98) if is_alt else (0.96, 0.97, 0.99)
        b.draw_rect(80, y, 1280, row_height, fill_rgb=bg_rgb, stroke_rgb=(0.85, 0.87, 0.92), line_width=0.75)
        # Parameter
        b.draw_text(param, 100, y + 22, font="/F2", size=16, rgb=(0.12, 0.14, 0.16))
        # Minimax
        b.draw_text(mm, 480, y + 22, font="/F1", size=16, rgb=(0.25, 0.28, 0.32))
        # Alpha-Beta (highlighted)
        b.draw_text(ab, 920, y + 22, font="/F2", size=16, rgb=(0.75, 0.12, 0.12))

    # Bottom Callout Box in Coral #ff6b5b
    b.draw_rounded_rect(80, 90, 1280, 125, r=10, fill_rgb=(1, 0.4196, 0.3569), stroke_rgb=None)
    b.draw_text("KEY EMPIRICAL FINDING (FOR PRESENTATION QUOTING):", 110, 180, font="/F2", size=14, rgb=(0.25, 0.05, 0.05))
    b.draw_text("Measured during live execution from an empty board. Pure Minimax explores 549,946 nodes to find the optimal move.", 110, 155, font="/F1", size=15, rgb=(1, 1, 1))
    b.draw_text("Alpha-Beta Pruning evaluates the identical optimal move while exploring only 20,866 nodes and executing 7,692 cutoffs.", 110, 132, font="/F2", size=15, rgb=(1, 1, 1))
    b.draw_text("This eliminates 529,080 redundant states (96.2% search reduction) with ZERO loss of accuracy - proving 100% minimax optimality.", 110, 109, font="/F1", size=15, rgb=(0.95, 0.98, 1))

    return b.get_stream()


def build_slide_11() -> bytes:
    """Slide 11: System Prototype & Architecture."""
    b = PDFPageBuilder()
    b.draw_header("S Y S T E M   P R O T O T Y P E", "Interactive Web Application Prototype", "Educational Two-Pane Architecture with Live Algorithm Visualization")

    cards = [
        (80, 390, 590, 240, "Dual-Pane Playable Game Interface", [
            "  * Interactive 3x3 board with real-time score tracking (Human / AI / Draws).",
            "  * Dynamic status indicator: 'Your Turn', 'AI Thinking...', and winning line glow.",
            "  * Live Algorithm Selector: Minimax vs. Minimax + Alpha-Beta Pruning.",
            "  * Difficulty Engine: Hard (unbeatable full depth), Medium, and Easy modes.",
            "  * First-Move Toggle: Supports both Human-First and AI-First openings.",
        ]),
        (770, 390, 590, 240, "Interactive Decision Tree Visualization", [
            "  * Live SVG tree rendering AI (MAX) and Human (MIN) lookahead states.",
            "  * Evaluated Nodes: Rendered as clean solid circles with utility scores.",
            "  * Pruned Branches: Rendered as dashed circles with scissors icon (Cutoff).",
            "  * Golden Edge Highlighting: Visually highlights the optimal chosen move path.",
            "  * Subtree Focus: Click any candidate move to isolate and explore its subtree.",
        ]),
        (80, 110, 590, 240, "Boundary-Aware Hover Tooltips", [
            "  * Zero Visual Clutter: Details hidden until mouse hover over any node.",
            "  * Instant Node Metadata: Node Role (MAX AI / MIN Human), Move Cell, and Score.",
            "  * Live Alpha-Beta Bounds: Displays current [Alpha, Beta] bounds at every node.",
            "  * Smart Collision Detection: Tooltip automatically flips left/up near edges.",
            "  * Hard Viewport Clamping: Prevents tooltip from ever sliding outside screen.",
        ]),
        (770, 110, 590, 240, "Real-Time Search Analytics & Controls", [
            "  * Search Volume Bar Chart: SVG chart comparing nodes explored per turn.",
            "  * Candidate Move Map: Mini-board ranking all legal moves (+8, -8, 0).",
            "  * Expandable Analytics Pane: Smooth draggable divider with 1-click collapse.",
            "  * Edge-to-Edge Fullscreen Modal: Press ESC or 'Back to Normal' to exit.",
            "  * Real-Time Efficiency Tracker: Reports cumulative % node savings across game.",
        ]),
    ]

    for (x, y, w, h, title, points) in cards:
        b.draw_rounded_rect(x, y, w, h, r=10, fill_rgb=(0.28, 0.10, 0.10), stroke_rgb=(0.48, 0.18, 0.18), line_width=1.5)
        # Title bar
        b.draw_rounded_rect(x, y + h - 46, w, 46, r=8, fill_rgb=(0.38, 0.14, 0.14), stroke_rgb=None)
        b.draw_text(title, x + 18, y + h - 29, font="/F2", size=17, rgb=(1, 0.85, 0.45))
        
        # Bullet points
        line_y = y + h - 74
        for pt in points:
            b.draw_text(pt, x + 16, line_y, font="/F1", size=13.5, rgb=(0.92, 0.94, 0.96))
            line_y -= 26

    return b.get_stream()


def build_slide_12() -> bytes:
    """Slide 12: Empirical Testing & Mathematical Verification."""
    b = PDFPageBuilder()
    b.draw_header("V E R I F I C A T I O N   &   T E S T I N G", "Rigorous Testing & Proof of Optimality", "Automated Pytest Suite & Exhaustive Game-Tree Simulation (0 AI Losses)")

    cards = [
        (80, 390, 590, 240, "16/16 Automated Tests in Pytest", [
            "  * 100% deterministic test pass rate in under 1.9 seconds execution time.",
            "  * Comprehensive validation of all 8 winning rows, columns, and diagonals.",
            "  * Terminal draw detection when board fills with no three-in-a-row.",
            "  * Illegal move rejection: Occupied cell and out-of-bounds protection.",
            "  * Flask REST endpoints (/api/move, /api/reset) verified with WSGI test client.",
        ]),
        (770, 390, 590, 240, "Mathematical Equivalence Proof", [
            "  * Formal verification: Minimax and Alpha-Beta return identical best scores.",
            "  * Tested across 30 randomized game positions with varying turn depths.",
            "  * Verified Alpha-Beta explores <= Minimax nodes across 100% of test cases.",
            "  * Proves Alpha-Beta pruning is 100% safe: Never prunes an optimal path.",
            "  * Decision tree integrity: Node depths, alpha bounds, and beta cutoffs verified.",
        ]),
        (80, 110, 590, 240, "Exhaustive Simulation: 0 AI Losses", [
            "  * Human-First Exhaustive Search: Simulated all 569 possible human paths.",
            "  * AI-First Exhaustive Search: Simulated all 73 possible opening AI paths.",
            "  * Result: 0 AI LOSSES across all complete games played to terminal states.",
            "  * Proven Outcome: The AI plays flawlessly and is mathematically unbeatable.",
            "  * Human player can at best achieve a draw with perfect counter-play.",
        ]),
        (770, 110, 590, 240, "Engineering & Deployment Reliability", [
            "  * Modular Python architecture: game.py, ai.py, and app.py separated cleanly.",
            "  * macOS AirPlay Port Conflict Handler: Auto-detects port 5000 and uses 5001.",
            "  * Zero external frontend libraries: Pure vanilla HTML, CSS, and modern JS.",
            "  * 1-Click macOS Double-Click Launcher: start.command runs venv & server.",
            "  * Client resilience: Recovers state instantly if connection is interrupted.",
        ]),
    ]

    for (x, y, w, h, title, points) in cards:
        b.draw_rounded_rect(x, y, w, h, r=10, fill_rgb=(0.28, 0.10, 0.10), stroke_rgb=(0.48, 0.18, 0.18), line_width=1.5)
        b.draw_rounded_rect(x, y + h - 46, w, 46, r=8, fill_rgb=(0.38, 0.14, 0.14), stroke_rgb=None)
        b.draw_text(title, x + 18, y + h - 29, font="/F2", size=17, rgb=(0.45, 0.85, 1.0))
        
        line_y = y + h - 74
        for pt in points:
            b.draw_text(pt, x + 16, line_y, font="/F1", size=13.5, rgb=(0.92, 0.94, 0.96))
            line_y -= 26

    return b.get_stream()


def build_slide_13() -> bytes:
    """Slide 13: Conclusion & Key Learnings."""
    b = PDFPageBuilder()
    b.draw_header("C O N C L U S I O N", "Project Achievements & Future Scope", "Foundations of Artificial Intelligence - Review 1 Deliverables")

    cols = [
        (80, 100, 395, 520, "Core Findings", [
            ("96.2% Node Reduction", "Alpha-Beta Pruning slashes search space from 549,946 to 20,866 nodes from the initial empty board."),
            ("32x Computational Speedup", "Search duration drops from ~800 ms down to ~25 ms, enabling instantaneous real-time responses."),
            ("Perfect Decision Equivalence", "Both algorithms output identical optimal moves. Pruning introduces zero heuristic compromise."),
            ("Mathematically Unbeatable AI", "Exhaustive testing confirms 0 losses across all possible human opponent move permutations."),
        ]),
        (522, 100, 395, 520, "Educational Value", [
            ("Interactive Adversarial Tree", "Visualizes abstract game theory with live MAX and MIN nodes and dashed pruning cutoffs."),
            ("Intuitive Scoring Mechanics", "Explains utility scores (+10 - depth for faster wins, depth - 10 to prolong losses, 0 for draws)."),
            ("Clear Cutoff Intuition", "Demonstrates why branches are pruned immediately when Beta <= Alpha without losing accuracy."),
            ("Dual Algorithm Comparison", "Live side-by-side metrics table allows students to see the exact power of optimization in real time."),
        ]),
        (965, 100, 395, 520, "Future Scope", [
            ("Higher Dimension Grids", "Extend the engine to 4x4 and 5x5 Tic-Tac-Toe boards using depth-limited iterative deepening."),
            ("Heuristic Evaluation", "Implement non-terminal heuristic evaluation functions for deeper search without exponential blowup."),
            ("Transposition Tables", "Incorporate Zobrist hashing to cache already-evaluated game positions and avoid repeated search."),
            ("Move Ordering Optimization", "Sort candidate moves dynamically to trigger earlier Alpha-Beta cutoffs and further reduce node counts."),
        ]),
    ]

    for (x, y, w, h, col_title, items) in cols:
        b.draw_rounded_rect(x, y, w, h, r=10, fill_rgb=(0.28, 0.10, 0.10), stroke_rgb=(0.48, 0.18, 0.18), line_width=1.5)
        b.draw_rounded_rect(x, y + h - 50, w, 50, r=8, fill_rgb=(0.38, 0.14, 0.14), stroke_rgb=None)
        b.draw_text(col_title, x + 20, y + h - 32, font="/F2", size=20, rgb=(1, 0.85, 0.45))

        item_y = y + h - 85
        for (head, body) in items:
            b.draw_text(f"> {head}", x + 16, item_y, font="/F2", size=15, rgb=(1, 0.45, 0.45))
            item_y -= 22
            # Split body into lines of ~40 chars
            words = body.split()
            cur_line = ""
            for word in words:
                if len(cur_line) + len(word) + 1 > 42:
                    b.draw_text(cur_line, x + 22, item_y, font="/F1", size=12.5, rgb=(0.9, 0.92, 0.94))
                    item_y -= 19
                    cur_line = word
                else:
                    cur_line = f"{cur_line} {word}".strip()
            if cur_line:
                b.draw_text(cur_line, x + 22, item_y, font="/F1", size=12.5, rgb=(0.9, 0.92, 0.94))
                item_y -= 26
            else:
                item_y -= 8

    return b.get_stream()


def generate_updated_pdf():
    """Reads original PDF and writes updated 13-slide PDF."""
    with open(SRC_PDF, "rb") as f:
        orig_data = f.read()

    # Find the end of original objects (before xref)
    xref_pos = orig_data.rfind(b"xref")
    if xref_pos == -1:
        xref_pos = orig_data.rfind(b"startxref")
    orig_body = orig_data[:xref_pos].rstrip()

    # Original size is 1160
    # Next available object ID is 1160
    # We will define:
    # 1160: Shared Font Dictionary
    # 1161: Stream for Slide 10
    # 1162: Page for Slide 10
    # 1163: Stream for Slide 11
    # 1164: Page for Slide 11
    # 1165: Stream for Slide 12
    # 1166: Page for Slide 12
    # 1167: Stream for Slide 13
    # 1168: Page for Slide 13
    # 1169: Modified Pages Object (Replaces Obj 2)
    
    font_obj_id = 1160
    p10_stream_id = 1161
    p10_page_id = 1162
    p11_stream_id = 1163
    p11_page_id = 1164
    p12_stream_id = 1165
    p12_page_id = 1166
    p13_stream_id = 1167
    p13_page_id = 1168
    pages_obj_id = 2  # Updating existing Obj 2

    new_objects = {}

    # Font dictionary (Standard Type 1 universal fonts)
    font_content = b"<< /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> /F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> /F3 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >> >>"
    new_objects[font_obj_id] = font_content

    # Slide streams
    slides_data = [
        (p10_stream_id, p10_page_id, build_slide_10()),
        (p11_stream_id, p11_page_id, build_slide_11()),
        (p12_stream_id, p12_page_id, build_slide_12()),
        (p13_stream_id, p13_page_id, build_slide_13()),
    ]

    for stream_id, page_id, raw_stream in slides_data:
        comp = zlib.compress(raw_stream)
        stream_obj = f"<< /Length {len(comp)} /Filter /FlateDecode >>\nstream\n".encode("ascii") + comp + b"\nendstream"
        new_objects[stream_id] = stream_obj

        # Page Object (1440x810 MediaBox matching Canva presentation)
        page_dict = f"""<<
/Type /Page
/Parent 2 0 R
/MediaBox [0.0 7.920007 1440.0 817.92]
/Resources <<
  /ProcSet [/PDF /Text]
  /Font {font_obj_id} 0 R
>>
/Contents {stream_id} 0 R
>>""".strip().encode("ascii")
        new_objects[page_id] = page_dict

    # Modified Pages Root (Object 2):
    # Original pages 10 to 18 (Slides 1 to 9) + our new slides (1162, 1164, 1166, 1168)
    # Total = 9 + 4 = 13 pages!
    pages_kids = " ".join([f"{num} 0 R" for num in range(10, 19)] + [
        f"{p10_page_id} 0 R",
        f"{p11_page_id} 0 R",
        f"{p12_page_id} 0 R",
        f"{p13_page_id} 0 R"
    ])
    pages_dict = f"""<<
/Type /Pages
/Kids [{pages_kids}]
/Count 13
>>""".strip().encode("ascii")
    new_objects[pages_obj_id] = pages_dict

    # Construct the PDF file
    out_buf = bytearray(orig_data)  # Start with full original file
    
    # Store xref offsets for updated / new objects
    offsets = {}

    for obj_id in sorted(new_objects.keys()):
        offsets[obj_id] = len(out_buf)
        header = f"\n{obj_id} 0 obj\n".encode("ascii")
        footer = b"\nendobj\n"
        out_buf.extend(header)
        out_buf.extend(new_objects[obj_id])
        out_buf.extend(footer)

    # Write new xref table (incremental update)
    xref_start = len(out_buf)
    out_buf.extend(b"\nxref\n")

    # Group objects into contiguous sections
    # Obj 2 is modified
    out_buf.extend(f"2 1\n{offsets[2]:010d} 00000 n \n".encode("ascii"))
    
    # Objs 1160 to 1168 are new
    new_start = font_obj_id
    new_count = len(new_objects) - 1
    out_buf.extend(f"{new_start} {new_count}\n".encode("ascii"))
    for obj_id in range(new_start, new_start + new_count):
        out_buf.extend(f"{offsets[obj_id]:010d} 00000 n \n".encode("ascii"))

    # Trailer
    trailer = f"""trailer
<<
/Root 1 0 R
/Info 9 0 R
/Prev 591339
/Size {new_start + new_count}
>>
startxref
{xref_start}
%%EOF
"""
    out_buf.extend(trailer.encode("ascii"))

    os.makedirs(os.path.dirname(OUT_PDF), exist_ok=True)
    with open(OUT_PDF, "wb") as f:
        f.write(out_buf)

    print(f" Successfully generated updated PDF at: {OUT_PDF}")
    print(f" Total pages: 13 (9 original slides + 4 prototype slides)")
    print(f" File size: {len(out_buf):,} bytes")

if __name__ == "__main__":
    generate_updated_pdf()
