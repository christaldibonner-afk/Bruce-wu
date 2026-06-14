"""创建测试 PDF 文件的脚本"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from pathlib import Path


def create_text_pdf():
    """创建文本型测试 PDF"""
    fixtures_dir = Path(__file__).parent
    pdf_path = fixtures_dir / "sample_text.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    # 第一页
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1*inch, height - 1*inch, "Test Document")

    c.setFont("Helvetica", 12)
    c.drawString(1*inch, height - 2*inch, "This is a test PDF document.")
    c.drawString(1*inch, height - 2.3*inch, "It contains multiple lines of text.")
    c.drawString(1*inch, height - 2.6*inch, "Used for testing the PDF converter.")

    c.save()

    print(f"Created: {pdf_path}")


if __name__ == '__main__':
    create_text_pdf()
