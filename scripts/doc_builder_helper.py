"""Reusable DocxBuilder utility for professional competition documentation."""
import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

ns = nsdecls("w")

def format_run(run, font_name="Microsoft YaHei", size_pt=10.5, color_rgb=(0x26, 0x26, 0x26), bold=False, italic=False):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rPr.set(qn("w:eastAsia"), font_name)

class DocxBuilder:
    def __init__(self):
        self.doc = docx.Document()
        self.setup_page()

    def setup_page(self, margin_in=1.0):
        for section in self.doc.sections:
            section.top_margin = Inches(margin_in)
            section.bottom_margin = Inches(margin_in)
            section.left_margin = Inches(margin_in)
            section.right_margin = Inches(margin_in)
            section.page_width = Inches(8.27)  # A4
            section.page_height = Inches(11.69)

    def set_header_footer(self, header_title, footer_label="锡语华纹 · 比赛申报材料包"):
        for section in self.doc.sections:
            header = section.header
            p_hdr = header.paragraphs[0]
            p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p_hdr.text = ""
            r_hdr = p_hdr.add_run(header_title)
            format_run(r_hdr, font_name="Microsoft YaHei", size_pt=8.5, color_rgb=(0x88, 0x88, 0x88))

            footer = section.footer
            p_ftr = footer.paragraphs[0]
            p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            p_ftr.text = ""
            r_ftr = p_ftr.add_run(f"{footer_label}  |  第 ")
            format_run(r_ftr, font_name="Microsoft YaHei", size_pt=8.5, color_rgb=(0x88, 0x88, 0x88))
            
            run_page = p_ftr.add_run()
            fld_page = parse_xml(f'<w:fldSimple {ns} w:instr="PAGE"/>')
            run_page._r.append(fld_page)
            format_run(run_page, font_name="Microsoft YaHei", size_pt=8.5, color_rgb=(0x88, 0x88, 0x88))

            r_ftr2 = p_ftr.add_run(" 页")
            format_run(r_ftr2, font_name="Microsoft YaHei", size_pt=8.5, color_rgb=(0x88, 0x88, 0x88))

    def add_title_block(self, title, subtitle, meta_dict):
        p_title = self.doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_before = Pt(18)
        p_title.paragraph_format.space_after = Pt(8)
        r_title = p_title.add_run(title)
        format_run(r_title, font_name="Microsoft YaHei", size_pt=22, color_rgb=(0x1A, 0x2A, 0x3A), bold=True)

        if subtitle:
            p_sub = self.doc.add_paragraph()
            p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_sub.paragraph_format.space_after = Pt(20)
            r_sub = p_sub.add_run(subtitle)
            format_run(r_sub, font_name="Microsoft YaHei", size_pt=13, color_rgb=(0x4A, 0x65, 0x72), bold=False)

        # Meta table
        table = self.doc.add_table(rows=len(meta_dict), cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = table._tbl.tblPr
        tblBorders = parse_xml(f"""
        <w:tblBorders {ns}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="1A2A3A"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="1A2A3A"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
        """)
        tblPr.append(tblBorders)

        for i, (k, v) in enumerate(meta_dict.items()):
            row = table.rows[i]
            c0, c1 = row.cells[0], row.cells[1]
            c0.width = Inches(1.8)
            c1.width = Inches(4.2)
            
            p0 = c0.paragraphs[0]
            p0.paragraph_format.space_before = Pt(3)
            p0.paragraph_format.space_after = Pt(3)
            r0 = p0.add_run(k)
            format_run(r0, font_name="Microsoft YaHei", size_pt=10, color_rgb=(0x4A, 0x65, 0x72), bold=True)

            p1 = c1.paragraphs[0]
            p1.paragraph_format.space_before = Pt(3)
            p1.paragraph_format.space_after = Pt(3)
            r1 = p1.add_run(v)
            format_run(r1, font_name="Microsoft YaHei", size_pt=10, color_rgb=(0x22, 0x22, 0x22), bold=False)

        p_sp = self.doc.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(12)
        p_sp.paragraph_format.space_after = Pt(12)

    def add_heading_1(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        format_run(run, font_name="Microsoft YaHei", size_pt=16, color_rgb=(0x1A, 0x2A, 0x3A), bold=True)

    def add_heading_2(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        format_run(run, font_name="Microsoft YaHei", size_pt=13, color_rgb=(0x2C, 0x3E, 0x50), bold=True)

    def add_heading_3(self, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        format_run(run, font_name="Microsoft YaHei", size_pt=11.5, color_rgb=(0x5C, 0x4B, 0x2C), bold=True)

    def add_paragraph(self, text, bold_prefix=None, space_after=4):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.25
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            format_run(r_pre, font_name="Microsoft YaHei", size_pt=10.5, color_rgb=(0x1A, 0x2A, 0x3A), bold=True)
        r = p.add_run(text)
        format_run(r, font_name="Microsoft YaHei", size_pt=10.5, color_rgb=(0x26, 0x26, 0x26), bold=False)
        return p

    def add_bullet(self, text, bold_prefix=None):
        p = self.doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.2
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            format_run(r_pre, font_name="Microsoft YaHei", size_pt=10, color_rgb=(0x1A, 0x2A, 0x3A), bold=True)
        r = p.add_run(text)
        format_run(r, font_name="Microsoft YaHei", size_pt=10, color_rgb=(0x26, 0x26, 0x26), bold=False)

    def add_numbered(self, num_str, text, bold_prefix=None):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.2
        r_num = p.add_run(num_str + " ")
        format_run(r_num, font_name="Microsoft YaHei", size_pt=10, color_rgb=(0x1A, 0x2A, 0x3A), bold=True)
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            format_run(r_pre, font_name="Microsoft YaHei", size_pt=10, color_rgb=(0x1A, 0x2A, 0x3A), bold=True)
        r = p.add_run(text)
        format_run(r, font_name="Microsoft YaHei", size_pt=10, color_rgb=(0x26, 0x26, 0x26), bold=False)

    def add_callout(self, text, title="【核心提示】", border_color="1A2A3A", bg_color="F2F5F8"):
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.0)
        tcPr = cell._tc.get_or_add_tcPr()
        
        shd = parse_xml(f'<w:shd {ns} w:fill="{bg_color}"/>')
        borders = parse_xml(f"""
        <w:tcBorders {ns}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="30" w:space="0" w:color="{border_color}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
        """)
        cellMar = parse_xml(f"""
        <w:tcMar {ns}>
            <w:top w:w="140" w:type="dxa"/>
            <w:left w:w="180" w:type="dxa"/>
            <w:bottom w:w="140" w:type="dxa"/>
            <w:right w:w="180" w:type="dxa"/>
        </w:tcMar>
        """)
        tcPr.append(shd)
        tcPr.append(borders)
        tcPr.append(cellMar)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.2
        if title:
            r_title = p.add_run(title + "\n")
            format_run(r_title, font_name="Microsoft YaHei", size_pt=10, color_rgb=(0x1A, 0x2A, 0x3A), bold=True)
        r_text = p.add_run(text)
        format_run(r_text, font_name="Microsoft YaHei", size_pt=9.5, color_rgb=(0x33, 0x33, 0x33), bold=False)

        p_after = self.doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(4)

    def add_code_block(self, code_text):
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.0)
        tcPr = cell._tc.get_or_add_tcPr()
        
        shd = parse_xml(f'<w:shd {ns} w:fill="F6F8FA"/>')
        borders = parse_xml(f"""
        <w:tcBorders {ns}>
            <w:top w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
            <w:left w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
            <w:bottom w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
            <w:right w:val="single" w:sz="4" w:space="0" w:color="D0D7DE"/>
        </w:tcBorders>
        """)
        cellMar = parse_xml(f"""
        <w:tcMar {ns}>
            <w:top w:w="100" w:type="dxa"/>
            <w:left w:w="140" w:type="dxa"/>
            <w:bottom w:w="100" w:type="dxa"/>
            <w:right w:w="140" w:type="dxa"/>
        </w:tcMar>
        """)
        tcPr.append(shd)
        tcPr.append(borders)
        tcPr.append(cellMar)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(code_text.strip())
        format_run(r, font_name="Consolas", size_pt=9, color_rgb=(0x24, 0x29, 0x2E), bold=False)

        p_after = self.doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(4)

    def add_table(self, headers, rows, col_widths=None):
        table = self.doc.add_table(rows=len(rows) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        tblPr = table._tbl.tblPr
        tblBorders = parse_xml(f"""
        <w:tblBorders {ns}>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="1A2A3A"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="1A2A3A"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
        """)
        tblPr.append(tblBorders)

        # Header row
        hdr_row = table.rows[0]
        for col_idx, h_text in enumerate(headers):
            cell = hdr_row.cells[col_idx]
            shd = parse_xml(f'<w:shd {ns} w:fill="1A2A3A"/>')
            cell._tc.get_or_add_tcPr().append(shd)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(h_text)
            format_run(r, font_name="Microsoft YaHei", size_pt=9.5, color_rgb=(0xFF, 0xFF, 0xFF), bold=True)

        # Data rows
        for row_idx, r_data in enumerate(rows):
            row = table.rows[row_idx + 1]
            bg_col = "F8F9FA" if row_idx % 2 == 1 else "FFFFFF"
            for col_idx, val in enumerate(r_data):
                cell = row.cells[col_idx]
                if bg_col != "FFFFFF":
                    shd = parse_xml(f'<w:shd {ns} w:fill="{bg_col}"/>')
                    cell._tc.get_or_add_tcPr().append(shd)
                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.15
                r = p.add_run(str(val))
                format_run(r, font_name="Microsoft YaHei", size_pt=9, color_rgb=(0x22, 0x22, 0x22), bold=False)

        # Apply column widths if specified
        if col_widths:
            for row in table.rows:
                for col_idx, w in enumerate(col_widths):
                    row.cells[col_idx].width = Inches(w)

        p_after = self.doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(6)

    def add_picture_with_caption(self, image_path, caption=None, width_in=5.8):
        if not os.path.exists(image_path):
            return
        p_img = self.doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(6)
        p_img.paragraph_format.space_after = Pt(2)
        self.doc.add_picture(image_path, width=Inches(width_in))
        
        if caption:
            p_cap = self.doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(8)
            r_cap = p_cap.add_run(caption)
            format_run(r_cap, font_name="Microsoft YaHei", size_pt=8.5, color_rgb=(0x66, 0x66, 0x66), italic=True)

    def add_page_break(self):
        self.doc.add_page_break()

    def save(self, filepath):
        self.doc.save(filepath)
        print(f"Document saved to {filepath}")
