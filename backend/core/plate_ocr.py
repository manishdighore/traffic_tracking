"""
License Plate OCR Module
Reads text from license plate images using EasyOCR and Tesseract
Based on: https://github.com/BarthPaleologue/ALPR
"""
import cv2
import numpy as np
from typing import Optional
import warnings

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    warnings.warn("EasyOCR not installed. Install with: pip install easyocr")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    warnings.warn("pytesseract not installed. Install with: pip install pytesseract")


class PlateOCR:
    """License plate OCR reader supporting EasyOCR and Tesseract"""
    
    def __init__(self, use_tesseract: bool = False):
        """
        Initialize OCR reader
        
        Args:
            use_tesseract: If True, use Tesseract OCR. Otherwise use EasyOCR (default)
        """
        self.use_tesseract = use_tesseract
        
        # European license plates typically only contain alphanumeric characters
        # Excluding I, O, U in some countries (like France) to avoid confusion
        self.allowed_chars = "ABCDEFGHJKLMNPQRSTVWXYZ0123456789- "
        
        if not use_tesseract:
            if not EASYOCR_AVAILABLE:
                print("⚠️  Warning: EasyOCR not available. OCR will be disabled.")
                self.reader = None
                return
            
            print("Initializing EasyOCR...")
            self.reader = easyocr.Reader(['en'], gpu=False)
            print("EasyOCR initialized.")
        else:
            if not TESSERACT_AVAILABLE:
                print("⚠️  Warning: Tesseract not available. OCR will be disabled.")
                self.reader = None
                return
            
            print("Using Tesseract OCR...")
            self.reader = True  # Just a flag for tesseract
        
        # Initialize super resolution for upscaling small plates
        self._init_super_resolution()
    
    def _init_super_resolution(self):
        """Initialize super resolution model for upscaling small images"""
        try:
            print("Initializing super resolution...")
            
            # Check if opencv-contrib is available and has the super resolution module
            if not hasattr(cv2, 'dnn_superres'):
                print("⚠️  opencv-contrib-python not properly installed. Super resolution disabled.")
                self.sr = None
                return
            
            # Try to create DnnSuperResImpl
            try:
                self.sr = cv2.dnn_superres.DnnSuperResImpl_create()
            except AttributeError:
                # Fallback for different OpenCV versions
                print("⚠️  Super resolution API not available in this OpenCV version.")
                self.sr = None
                return
            
            # Try to load ESPCN model (smaller and faster than EDSR)
            model_path = "super_resolution/ESPCN_x2.pb"
            try:
                self.sr.readModel(model_path)
                self.sr.setModel("espcn", 2)
                print("Super resolution initialized (ESPCN x2).")
            except:
                # If model doesn't exist, disable super resolution
                print("⚠️  Super resolution model not found. Upscaling disabled.")
                self.sr = None
        except Exception as e:
            print(f"⚠️  Could not initialize super resolution: {e}")
            self.sr = None
    
    def preprocess_plate(self, plate_img: np.ndarray) -> np.ndarray:
        """
        Preprocess plate image for better OCR results
        
        Args:
            plate_img: Input plate image
            
        Returns:
            Preprocessed image
        """
        # Upscale if image is too small
        if self.sr is not None and plate_img.shape[1] < 128:
            try:
                plate_img = self.sr.upsample(plate_img)
            except:
                pass  # Continue without upscaling
        
        # Convert to grayscale
        if len(plate_img.shape) == 3:
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_img
        
        # Histogram equalization for better contrast
        gray = cv2.equalizeHist(gray)
        
        # Optional: Apply sharpening
        # kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        # gray = cv2.filter2D(gray, -1, 0.2 * kernel)
        
        return gray
    
    def read(self, plate_img: np.ndarray) -> Optional[str]:
        """
        Read text from license plate image
        
        Args:
            plate_img: License plate image (cropped)
            
        Returns:
            Detected text or None if reading failed
        """
        if self.reader is None:
            return None
        
        if plate_img is None or plate_img.size == 0:
            return None
        
        try:
            # Preprocess image
            processed = self.preprocess_plate(plate_img)
            
            if not self.use_tesseract:
                # Use EasyOCR
                results = self.reader.readtext(
                    processed,
                    allowlist=self.allowed_chars,
                    detail=1
                )
                
                if len(results) == 0:
                    return None
                
                # Sort results by x-coordinate (left to right)
                results = sorted(results, key=lambda r: r[0][0][0])
                
                # Concatenate all detected text
                plate_text = "".join([result[1] for result in results])
                
            else:
                # Use Tesseract
                # PSM 6: Assume uniform block of text
                # OEM 3: Default LSTM OCR engine
                custom_config = r'--oem 3 --psm 6'
                plate_text = pytesseract.image_to_string(
                    processed,
                    config=custom_config
                )
            
            # Clean up result
            plate_text = plate_text.replace("-", "").replace(" ", "").strip()
            plate_text = plate_text.upper()
            
            # Filter out non-alphanumeric characters
            plate_text = ''.join(c for c in plate_text if c.isalnum())
            
            # Return None if text is too short (probably false detection)
            if len(plate_text) < 4:
                return None
            
            return plate_text
            
        except Exception as e:
            print(f"OCR failed: {e}")
            return None
    
    def read_with_confidence(self, plate_img: np.ndarray) -> tuple[Optional[str], float]:
        """
        Read text from license plate with confidence score
        
        Args:
            plate_img: License plate image
            
        Returns:
            Tuple of (text, confidence) or (None, 0.0)
        """
        if self.reader is None or plate_img is None or plate_img.size == 0:
            return None, 0.0
        
        try:
            processed = self.preprocess_plate(plate_img)
            
            if not self.use_tesseract:
                results = self.reader.readtext(
                    processed,
                    allowlist=self.allowed_chars,
                    detail=1
                )
                
                if len(results) == 0:
                    return None, 0.0
                
                # Sort by x-coordinate
                results = sorted(results, key=lambda r: r[0][0][0])
                
                # Get text and average confidence
                plate_text = "".join([result[1] for result in results])
                avg_confidence = sum([result[2] for result in results]) / len(results)
                
                # Clean text
                plate_text = plate_text.replace("-", "").replace(" ", "").strip()
                plate_text = plate_text.upper()
                plate_text = ''.join(c for c in plate_text if c.isalnum())
                
                if len(plate_text) < 4:
                    return None, 0.0
                
                return plate_text, avg_confidence
            else:
                # Tesseract doesn't provide confidence in the same way
                plate_text = pytesseract.image_to_string(
                    processed,
                    config=r'--oem 3 --psm 6'
                )
                
                plate_text = plate_text.replace("-", "").replace(" ", "").strip()
                plate_text = plate_text.upper()
                plate_text = ''.join(c for c in plate_text if c.isalnum())
                
                if len(plate_text) < 4:
                    return None, 0.0
                
                # Return a generic confidence since Tesseract output doesn't include it
                return plate_text, 0.8
                
        except Exception as e:
            print(f"OCR failed: {e}")
            return None, 0.0
    
    @staticmethod
    def validate_plate_format(plate_text: str, country: str = "EU") -> bool:
        """
        Validate license plate format for specific country
        
        Args:
            plate_text: Detected plate text
            country: Country code (EU, FR, RO, etc.)
            
        Returns:
            True if format is valid
        """
        if not plate_text or len(plate_text) < 4:
            return False
        
        # Basic validation for European plates (6-8 characters)
        if country == "EU":
            return 6 <= len(plate_text) <= 9
        
        # Add specific country validations if needed
        # French plates: AB-123-CD (7 chars without dashes)
        if country == "FR":
            return len(plate_text) == 7
        
        # Romanian plates: B-123-ABC (7-8 chars)
        if country == "RO":
            return 7 <= len(plate_text) <= 8
        
        return True


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings
    Useful for matching detected plates with known plates
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Edit distance
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        
        for j, c2 in enumerate(s2):
            # Common OCR confusions
            if c1 == '7' and c2 == 'Z' or c1 == 'Z' and c2 == '7':
                cost = 0
            elif c1 == '1' and c2 == 'I' or c1 == 'I' and c2 == '1':
                cost = 0
            elif c1 == '0' and c2 == 'O' or c1 == 'O' and c2 == '0':
                cost = 0
            elif c1 == 'B' and c2 == '8' or c1 == '8' and c2 == 'B':
                cost = 0
            else:
                cost = 0 if c1 == c2 else 1
            
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + cost
            
            current_row.append(min(insertions, deletions, substitutions))
        
        previous_row = current_row
    
    return previous_row[-1]


def match_plate_to_database(
    detected_plate: str,
    known_plates: list[str],
    threshold: int = 2
) -> tuple[Optional[str], int]:
    """
    Match detected plate to a list of known plates using fuzzy matching
    
    Args:
        detected_plate: Detected plate text
        known_plates: List of known license plates
        threshold: Maximum edit distance to consider a match
        
    Returns:
        Tuple of (best_match, distance) or (None, inf)
    """
    best_match = None
    best_distance = float('inf')
    
    for known_plate in known_plates:
        distance = levenshtein_distance(detected_plate, known_plate)
        
        if distance < best_distance:
            best_distance = distance
            best_match = known_plate
    
    if best_distance <= threshold:
        return best_match, best_distance
    
    return None, best_distance
