#!/usr/bin/env python3
"""
PDF Generator Module
Creates personalized invitation cards by adding Gujarati names to the template PDF
"""

import os
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor


class InvitationPDFGenerator:
    """
    Generate personalized invitation PDFs by overlaying Gujarati names
    on the template invitation card
    """
    
    # PDF Configuration from problem statement
    TEMPLATE_PDF = "Invitation card.pdf"
    OUTPUT_FILENAME = "Vadhel Sarthak's Wedding Invitation.pdf"
    
    # Text positions as specified in requirements
    # Page 1: x=170, y=497
    # Page 4: x=95, y=197
    PAGE_1_POSITION = (170, 490)
    PAGE_4_POSITION = (95, 186)
    
    # Font configuration (red color, 13-15pt size)
    FONT_SIZE_MIN = 13
    FONT_SIZE_MAX = 15
    FONT_SIZE = 15  # Middle of the range
    FONT_COLOR = HexColor('#DC143C')  # Crimson red
    
    # Gujarati font path (will try to use if available)
    GUJARATI_FONT_PATH = "fonts/NotoSansGujarati-Regular.ttf"
    FONT_NAME = "GujaratiFont"
    
    def __init__(self):
        """Initialize the PDF generator and register fonts"""
        self.font_registered = False
        self._register_gujarati_font()
    
    def _register_gujarati_font(self):
        """Register Gujarati font if available"""
        try:
            if os.path.exists(self.GUJARATI_FONT_PATH):
                pdfmetrics.registerFont(TTFont(self.FONT_NAME, self.GUJARATI_FONT_PATH))
                self.font_registered = True
                print(f"✓ Gujarati font registered from {self.GUJARATI_FONT_PATH}")
            else:
                print(f"⚠ Gujarati font not found at {self.GUJARATI_FONT_PATH}")
                print(f"  Using Helvetica as fallback. Download a Gujarati TTF font and place it at:")
                print(f"  {self.GUJARATI_FONT_PATH}")
                self.FONT_NAME = "Helvetica"
        except Exception as e:
            print(f"⚠ Could not register Gujarati font: {e}")
            print(f"  Using Helvetica as fallback")
            self.FONT_NAME = "Helvetica"
    
    def _create_text_overlay(self, text, position, page_width, page_height):
        """
        Create a PDF overlay with text at specified position
        
        Args:
            text: The text to add (Gujarati name)
            position: Tuple of (x, y) coordinates
            page_width: Width of the page in points
            page_height: Height of the page in points
        
        Returns:
            BytesIO object containing the overlay PDF
        """
        # Create a BytesIO buffer for the overlay
        packet = io.BytesIO()
        
        # Create canvas with same size as the page
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))
        
        # Set font and color
        can.setFont(self.FONT_NAME, self.FONT_SIZE)
        can.setFillColor(self.FONT_COLOR)
        
        # Draw the text at the specified position
        # Note: PDF coordinates start from bottom-left
        # The y-coordinate from top is: page_height - y
        x, y = position
        can.drawString(x, page_height - y, text)
        
        # Save the canvas
        can.save()
        
        # Move to the beginning of the BytesIO buffer
        packet.seek(0)
        return packet
    
    def generate_personalized_invitation(self, gujarati_name, output_path=None, return_bytes=False):
        """
        Generate a personalized invitation card with the guest's Gujarati name
        
        Args:
            gujarati_name: The guest's name in Gujarati script
            output_path: Optional custom output path (defaults to OUTPUT_FILENAME)
            return_bytes: If True, returns PDF as bytes instead of saving to file
        
        Returns:
            Path to the generated PDF file (if return_bytes=False)
            BytesIO object containing PDF (if return_bytes=True)
        """
        if output_path is None and not return_bytes:
            output_path = self.OUTPUT_FILENAME
        
        # Read the template PDF
        template_reader = PdfReader(self.TEMPLATE_PDF)
        pdf_writer = PdfWriter()
        
        # Process each page
        for page_num in range(len(template_reader.pages)):
            page = template_reader.pages[page_num]
            
            # Get page dimensions
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Add text overlay for pages 1 and 4 (0-indexed: 0 and 3)
            if page_num == 0:  # Page 1
                overlay_packet = self._create_text_overlay(
                    gujarati_name,
                    self.PAGE_1_POSITION,
                    page_width,
                    page_height
                )
                overlay_reader = PdfReader(overlay_packet)
                overlay_page = overlay_reader.pages[0]
                page.merge_page(overlay_page)
            
            elif page_num == 3:  # Page 4
                overlay_packet = self._create_text_overlay(
                    gujarati_name,
                    self.PAGE_4_POSITION,
                    page_width,
                    page_height
                )
                overlay_reader = PdfReader(overlay_packet)
                overlay_page = overlay_reader.pages[0]
                page.merge_page(overlay_page)
            
            # Add the (possibly modified) page to output
            pdf_writer.add_page(page)
        
        # Return as bytes or save to file
        if return_bytes:
            # Return PDF as BytesIO
            pdf_bytes = io.BytesIO()
            pdf_writer.write(pdf_bytes)
            pdf_bytes.seek(0)
            print(f"✓ Generated personalized invitation as bytes")
            print(f"  Guest name: {gujarati_name}")
            return pdf_bytes
        else:
            # Write to output file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            print(f"✓ Generated personalized invitation: {output_path}")
            print(f"  Guest name: {gujarati_name}")
            
            return output_path
    
    def cleanup_generated_pdf(self, pdf_path=None):
        """
        Clean up the generated PDF file
        
        Args:
            pdf_path: Path to the PDF file to delete (defaults to OUTPUT_FILENAME)
        """
        if pdf_path is None:
            pdf_path = self.OUTPUT_FILENAME
        
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                print(f"✓ Cleaned up generated PDF: {pdf_path}")
        except Exception as e:
            print(f"⚠ Could not delete {pdf_path}: {e}")


# Convenience function for easy import and use
def generate_invitation_pdf(gujarati_name):
    """
    Generate a personalized invitation PDF
    
    Args:
        gujarati_name: The guest's name in Gujarati script
    
    Returns:
        Path to the generated PDF file
    """
    generator = InvitationPDFGenerator()
    return generator.generate_personalized_invitation(gujarati_name)


# Test the module if run directly
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
    else:
        test_name = "tesing pdf"  # Ramesh Patel in Gujarati
    
    print(f"Testing PDF generation with name: {test_name}")
    output_file = generate_invitation_pdf(test_name)
    print(f"\nGenerated PDF: {output_file}")
    print(f"Check the file to verify the name appears on pages 1 and 4")
