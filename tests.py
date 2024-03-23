import unittest
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
from SHDetector import detect_safety

class TestSafetyDetector(unittest.TestCase):
    def setUp(self):
        self.test_image_path = "images\pos_784.jpg"
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)  # Dummy image

    def test_detect_safety(self):
        # Mock the processImage function and cv2.rectangle
        with patch("your_module.processImage", return_value=self.test_image) as mock_processImage:
            with patch("cv2.rectangle") as mock_cv2_rectangle:
                result = detect_safety(self.test_image)

                # Ensure processImage is called with the correct argument
                mock_processImage.assert_called_once_with(self.test_image)

                # Ensure cv2.rectangle is called with the correct arguments
                mock_cv2_rectangle.assert_called_once()

                # Ensure the result is not None
                self.assertIsNotNone(result)

    def test_detect_safety_with_helmet(self):
        # Mock the processImage function and cv2.rectangle
        with patch("SHDetector.processImage", return_value=self.test_image) as mock_processImage:
            with patch("cv2.rectangle") as mock_cv2_rectangle:
                # Create example helmet coordinates
                helmet_coordinates = [(10, 10, 20, 20)]  # Example coordinates (x1, y1, x2, y2)
                
                with patch("SHDetector.helmet_coordinates", helmet_coordinates):
                    result = detect_safety(self.test_image)

                    # Ensure cv2.rectangle is called for each helmet coordinate
                    self.assertEqual(mock_cv2_rectangle.call_count, len(helmet_coordinates))

                    # Ensure the result is not None
                    self.assertIsNotNone(result)

    def test_detect_safety_no_image(self):
        # Test with no input image
        result = detect_safety(None)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
