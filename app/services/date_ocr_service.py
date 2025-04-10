from typing import Optional
import cv2
import numpy as np
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import re
from datetime import datetime
import os
from flask import current_app
from io import BytesIO

class DateOCRService:
    """Service for extracting dates from images using Azure Computer Vision."""
    
    def __init__(self):
        """Initialize the Azure Computer Vision service."""
        # Get Azure credentials from environment variables
        self.subscription_key = os.getenv('AZURE_VISION_KEY')
        self.endpoint = os.getenv('AZURE_VISION_ENDPOINT')
        
        # Initialize vision client only if credentials are available
        self.vision_client = None
        if self.subscription_key and self.endpoint:
            try:
                # Ensure endpoint ends with a slash
                if not self.endpoint.endswith('/'):
                    self.endpoint = self.endpoint + '/'
                
                self.vision_client = ComputerVisionClient(
                    endpoint=self.endpoint,
                    credentials=CognitiveServicesCredentials(self.subscription_key)
                )
                print(f"Azure Computer Vision service initialized successfully with endpoint: {self.endpoint}")
            except Exception as e:
                print(f"Error initializing Azure Computer Vision: {str(e)}")
        else:
            print("Azure credentials not found. OCR service will not be available.")
            if not self.subscription_key:
                print("Missing AZURE_VISION_KEY")
            if not self.endpoint:
                print("Missing AZURE_VISION_ENDPOINT")

    def preprocess_image(self, image_data: bytes) -> bytes:
        """Preprocess the image to improve OCR accuracy."""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply gentle noise reduction
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Apply adaptive thresholding with gentler parameters
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply gentle morphological operations
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Save debug image
            debug_dir = os.path.join(current_app.root_path, 'debug_images')
            os.makedirs(debug_dir, exist_ok=True)
            debug_path = os.path.join(debug_dir, 'preprocessed.png')
            cv2.imwrite(debug_path, cleaned)
            print(f"Saved preprocessed image to {debug_path}")
            
            # Convert back to bytes
            _, img_encoded = cv2.imencode('.png', cleaned)
            return img_encoded.tobytes()
            
        except Exception as e:
            print(f"Error in image preprocessing: {str(e)}")
            return image_data  # Return original image if preprocessing fails

    def correct_ocr_errors(self, text: str) -> str:
        """Correct common OCR misreads."""
        corrections = {
            'マ': 'M', '了': 'L', 'ー': '-', 'つ': 'T', 'Ⅵ': '6', '「': '(',
            'see': 'exp', 'beee': 'date', 'expiry': 'exp', 'date': 'date',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05',
            'jun': '06', 'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10',
            'nov': '11', 'dec': '12'
        }
        
        corrected = text.lower()
        for wrong, right in corrections.items():
            corrected = corrected.replace(wrong.lower(), right.lower())
        return corrected

    def extract_date(self, image_data: bytes) -> Optional[str]:
        """
        Extract date from image data using Azure Computer Vision OCR.
        Returns the date in YYYY-MM-DD format if found, None otherwise.
        """
        try:
            # Check if Azure service is available
            if not self.vision_client:
                print("Azure Computer Vision service not available")
                return None

            # Preprocess image
            processed_image = self.preprocess_image(image_data)
            
            # Create a file-like object from the bytes
            image_stream = BytesIO(processed_image)
            
            # Call Azure OCR
            ocr_result = self.vision_client.recognize_printed_text_in_stream(
                image=image_stream
            )
            
            # Extract all text from OCR results
            text_blocks = []
            for region in ocr_result.regions:
                for line in region.lines:
                    text = ' '.join([word.text for word in line.words])
                    text_blocks.append(text)
                    print(f"Detected text: {text}")
            
            # Join all text blocks and clean up
            full_text = ' '.join(text_blocks)
            full_text = self.correct_ocr_errors(full_text)
            print(f"Full text after correction: {full_text}")
            
            # Date patterns to look for
            date_patterns = [
                # Numeric formats
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',  # DD-MM-YYYY or DD/MM/YYYY
                r'\d{2,4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY-MM-DD or YYYY/MM/DD
                r'\d{1,2}[-/]\d{1,2}[-/]\d{2}',    # DD-MM-YY or DD/MM/YY
                r'\d{2}[-/]\d{1,2}[-/]\d{2,4}',    # YY-MM-DD or YY/MM/YYYY
                # Expiry date specific patterns
                r'exp(?:iry)?\s*date\s*[:]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'exp(?:iry)?\s*date\s*[:]?\s*(\d{2,4}[-/]\d{1,2}[-/]\d{1,2})',
                r'exp(?:iry)?\s*date\s*[:]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2})',
                r'exp(?:iry)?\s*date\s*[:]?\s*(\d{2}[-/]\d{1,2}[-/]\d{2,4})',
                # Month name formats
                r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{2,4}',
                # Expiry with month names
                r'exp(?:iry)?\s*date\s*[:]?\s*(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{2,4}'
            ]
            
            # Try each pattern
            for pattern in date_patterns:
                matches = re.findall(pattern, full_text)
                if matches:
                    date_str = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    print(f"Found potential date: {date_str}")
                    try:
                        # Try different date formats
                        formats = [
                            '%d-%m-%Y', '%d/%m/%Y',  # DD-MM-YYYY or DD/MM/YYYY
                            '%Y-%m-%d', '%Y/%m/%d',  # YYYY-MM-DD or YYYY/MM/DD
                            '%d-%m-%y', '%d/%m/%y',  # DD-MM-YY or DD/MM/YY
                            '%y-%m-%d', '%y/%m/%d',  # YY-MM-DD or YY/MM/DD
                            '%B %d, %Y', '%b %d, %Y' # Month name formats
                        ]
                        
                        for fmt in formats:
                            try:
                                date_obj = datetime.strptime(date_str, fmt)
                                # Validate year is reasonable
                                if 2000 <= date_obj.year <= 2100:
                                    formatted_date = date_obj.strftime('%Y-%m-%d')
                                    print(f"Successfully parsed date: {formatted_date}")
                                    return formatted_date
                            except ValueError:
                                continue
                            
                    except Exception as e:
                        print(f"Error parsing date {date_str}: {str(e)}")
                        continue
            
            print("No valid date found in text")
            return None
            
        except Exception as e:
            print(f"Error in OCR processing: {str(e)}")
            return None 