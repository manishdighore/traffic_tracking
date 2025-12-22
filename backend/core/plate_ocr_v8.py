"""
License Plate OCR Module with Format Validation
Reads text from license plate images using EasyOCR
Based on: https://github.com/sveyek/Video-ANPR
"""
import cv2
import numpy as np
from typing import Optional, Tuple
import warnings
import string

# Fix PIL compatibility for newer Pillow versions
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    warnings.warn("EasyOCR not installed. Install with: pip install easyocr")


class PlateOCR:
    """License plate OCR reader with format validation"""
    
    # Character mappings for ambiguous characters (UK/Indian format)
    CHAR_TO_INT = {
        'O': '0',
        'I': '1',
        'J': '3',
        'A': '4',
        'G': '6',
        'S': '5',
        'Z': '2',
        'B': '8'
    }
    
    INT_TO_CHAR = {
        '0': 'O',
        '1': 'I',
        '3': 'J',
        '4': 'A',
        '6': 'G',
        '5': 'S',
        '2': 'Z',
        '8': 'B'
    }
    
    def __init__(self, use_gpu: bool = False):
        """
        Initialize OCR reader
        
        Args:
            use_gpu: If True, use GPU for EasyOCR
        """
        self.reader = None
        
        if not EASYOCR_AVAILABLE:
            print("⚠️  Warning: EasyOCR not available. OCR will be disabled.")
            return
        
        print("Initializing EasyOCR...")
        try:
            self.reader = easyocr.Reader(['en'], gpu=use_gpu)
            print(f"✅ EasyOCR initialized (GPU={'enabled' if use_gpu else 'disabled'})")
        except Exception as e:
            print(f"❌ Error initializing EasyOCR: {e}")
            self.reader = None
    
    def preprocess_plate(self, plate_img: np.ndarray) -> np.ndarray:
        """
        Preprocess plate image for better OCR results
        
        Args:
            plate_img: Input plate image
            
        Returns:
            Preprocessed plate image
        """
        # Convert to grayscale
        if len(plate_img.shape) == 3:
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_img.copy()
        
        # Apply thresholding to get binary image
        _, thresh = cv2.threshold(gray, 64, 255, cv2.THRESH_BINARY_INV)
        
        return thresh
    
    def check_indian_format(self, text: str) -> bool:
        """
        Check if text matches Indian license plate format
        Indian format: XX00XX0000 or XX-00-XX-0000
        e.g., DL1CAA1234 or DL-01-CA-1234
        
        Args:
            text: Text to check
            
        Returns:
            True if matches format
        """
        # Remove spaces and dashes
        clean = text.replace(' ', '').replace('-', '').upper()
        
        # Indian plates are typically 9-10 characters
        if len(clean) < 9 or len(clean) > 10:
            return False
        
        # Pattern: 2-3 letters (state code) + 2 digits (district) + 1-2 letters (series) + 4 digits
        # Examples: DL1CAA1234 (10 chars), MH12AB1234 (10 chars)
        
        # Check first 2 characters are letters (state code)
        if not (clean[0].isalpha() and clean[1].isalpha()):
            return False
        
        # Third char can be letter or digit
        # If it's a letter, we have a 3-letter state code
        if clean[2].isalpha():
            # 3-letter state code format
            if len(clean) != 10:
                return False
            # Next 2 must be digits
            if not (clean[3].isdigit() and clean[4].isdigit()):
                return False
            # Next 1-2 must be letters
            if not (clean[5].isalpha() and clean[6].isalpha()):
                return False
            # Last 4 must be digits
            if not all(c.isdigit() for c in clean[7:11]):
                return False
        else:
            # 2-letter state code format
            if len(clean) < 9:
                return False
            # Next 2 must be digits
            if not (clean[2].isdigit() and clean[3].isdigit()):
                return False
            # Next 1-2 must be letters
            letters_start = 4
            letters_end = letters_start
            while letters_end < len(clean) and clean[letters_end].isalpha():
                letters_end += 1
            
            if letters_end - letters_start < 1 or letters_end - letters_start > 2:
                return False
            
            # Rest must be 4 digits
            if len(clean) - letters_end != 4:
                return False
            if not all(c.isdigit() for c in clean[letters_end:]):
                return False
        
        return True
    
    def check_uk_format(self, text: str) -> bool:
        """
        Check if text matches UK license plate format
        UK format: XX00XXX (7 characters)
        
        Args:
            text: Text to check
            
        Returns:
            True if matches format
        """
        clean = text.replace(' ', '').upper()
        
        if len(clean) != 7:
            return False
        
        # Pattern: 2 letters, 2 digits, 3 letters
        return (
            (clean[0].isalpha() or clean[0] in self.INT_TO_CHAR) and
            (clean[1].isalpha() or clean[1] in self.INT_TO_CHAR) and
            (clean[2].isdigit() or clean[2] in self.CHAR_TO_INT) and
            (clean[3].isdigit() or clean[3] in self.CHAR_TO_INT) and
            (clean[4].isalpha() or clean[4] in self.INT_TO_CHAR) and
            (clean[5].isalpha() or clean[5] in self.INT_TO_CHAR) and
            (clean[6].isalpha() or clean[6] in self.INT_TO_CHAR)
        )
    
    def format_uk_plate(self, text: str) -> str:
        """
        Format UK license plate text with character corrections
        
        Args:
            text: Raw text
            
        Returns:
            Formatted text
        """
        text = text.upper().replace(' ', '')
        if len(text) != 7:
            return text
        
        formatted = ''
        
        # Positions 0,1,4,5,6 should be letters
        # Positions 2,3 should be digits
        char_map = {
            0: self.INT_TO_CHAR,
            1: self.INT_TO_CHAR,
            4: self.INT_TO_CHAR,
            5: self.INT_TO_CHAR,
            6: self.INT_TO_CHAR,
            2: self.CHAR_TO_INT,
            3: self.CHAR_TO_INT
        }
        
        for i in range(7):
            if text[i] in char_map[i]:
                formatted += char_map[i][text[i]]
            else:
                formatted += text[i]
        
        return formatted
    
    def format_indian_plate(self, text: str) -> str:
        """
        Format Indian license plate text with standard formatting
        
        Args:
            text: Raw text
            
        Returns:
            Formatted text with dashes (XX-00-XX-0000)
        """
        clean = text.replace(' ', '').replace('-', '').upper()
        
        # Detect format based on length
        if len(clean) == 10 and clean[2].isalpha():
            # 3-letter state code: XXX-00-XX-0000
            return f"{clean[0:3]}-{clean[3:5]}-{clean[5:7]}-{clean[7:11]}"
        elif len(clean) >= 9:
            # 2-letter state code: XX-00-XX-0000
            # Find where letters end after state code
            letters_end = 4
            while letters_end < len(clean) and clean[letters_end].isalpha():
                letters_end += 1
            
            state = clean[0:2]
            district = clean[2:4]
            series = clean[4:letters_end]
            number = clean[letters_end:]
            
            return f"{state}-{district}-{series}-{number}"
        
        return clean
    
    def read_with_confidence(
        self,
        plate_img: np.ndarray,
        format_type: str = 'auto'
    ) -> Tuple[Optional[str], Optional[float]]:
        """
        Read license plate text with confidence score and format validation
        
        Args:
            plate_img: Cropped plate image
            format_type: 'uk', 'indian', or 'auto' to detect
            
        Returns:
            Tuple of (text, confidence) or (None, None) if reading fails
        """
        if self.reader is None:
            return None, None
        
        if plate_img.size == 0:
            return None, None
        
        try:
            # Preprocess image
            preprocessed = self.preprocess_plate(plate_img)
            
            # Try reading from preprocessed image
            detections = self.reader.readtext(preprocessed)
            
            if not detections:
                # Try original image
                detections = self.reader.readtext(plate_img)
            
            if not detections:
                return None, None
            
            # Process all detections
            for detection in detections:
                bbox, text, confidence = detection
                text = text.upper().replace(' ', '')
                
                # Try format detection
                if format_type == 'auto' or format_type == 'indian':
                    if self.check_indian_format(text):
                        formatted = self.format_indian_plate(text)
                        return formatted, confidence
                
                if format_type == 'auto' or format_type == 'uk':
                    if self.check_uk_format(text):
                        formatted = self.format_uk_plate(text)
                        return formatted, confidence
                
                # If no format matches but we have text, return it anyway if confidence is high
                if confidence > 0.7:
                    return text, confidence
            
            # Return best confidence even if format doesn't match
            if detections:
                bbox, text, confidence = max(detections, key=lambda x: x[2])
                return text.upper().replace(' ', ''), confidence
            
            return None, None
            
        except Exception as e:
            print(f"Error reading plate: {e}")
            return None, None
    
    def read(self, plate_img: np.ndarray, format_type: str = 'auto') -> Optional[str]:
        """
        Read license plate text (convenience method)
        
        Args:
            plate_img: Cropped plate image
            format_type: 'uk', 'indian', or 'auto'
            
        Returns:
            Extracted text or None
        """
        text, _ = self.read_with_confidence(plate_img, format_type)
        return text
