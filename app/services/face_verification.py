from deepface import DeepFace # type: ignore
import cv2 # type: ignore
import numpy as np # type: ignore
from pathlib import Path
from app.core.config import settings
import uuid

class FaceVerificationService:
    def __init__(self):
        self.passport_path = None
        self.model_name = "VGG-Face"  # You can also use "Facenet", "OpenFace", "DeepFace", "DeepID", "ArcFace" or "Dlib"
        self.distance_metric = "cosine"
        self.threshold = 0.3  # Adjust this value for stricter/looser matching

    async def save_passport_image(self, file) -> Path:
        """Save uploaded passport image and return the path"""
        file_extension = file.filename.split('.')[-1]
        file_name = f"{uuid.uuid4()}.{file_extension}"
        file_path = settings.UPLOAD_DIR / file_name

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return file_path


    def process_passport_image(self, image_path: Path):
        """Process passport image and verify it contains a face"""
        try:
            # Verify the image contains a face
            DeepFace.extract_faces(str(image_path))
            self.passport_path = image_path
            return True
        except Exception as e:
            raise ValueError(f"No face found in passport image or invalid image: {str(e)}")

    def verify_face_image(self, verification_image_path: Path):
        """Verify a face image against stored passport image"""
        if self.passport_path is None:
            raise ValueError("No passport image has been processed")

        try:
            # Verify faces
            result = DeepFace.verify(
                img1_path=str(self.passport_path),
                img2_path=str(verification_image_path),
                model_name=self.model_name,
                distance_metric=self.distance_metric
            )

            # Calculate confidence (convert distance to a 0-1 scale)
            confidence = 1 - min(result['distance'] / self.threshold, 1.0)
            
            return {
                "is_match": result['verified'],
                "confidence": confidence
            }
            
        except Exception as e:
            raise ValueError(f"Error during face verification: {str(e)}")

    def detect_face_landmarks(self, image_path: Path):
        """Optional: Analyze facial landmarks and attributes"""
        try:
            analysis = DeepFace.analyze(
                img_path=str(image_path),
                actions=['age', 'gender', 'race', 'emotion']
            )
            return analysis
        except Exception as e:
            raise ValueError(f"Error analyzing face: {str(e)}") 