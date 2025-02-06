from fastapi import APIRouter, UploadFile, File, HTTPException, Depends # type: ignore
from app.services.face_verification import FaceVerificationService
from app.schemas.verification import VerificationResponse, VerificationResult
import os

router = APIRouter()
face_service = FaceVerificationService()

@router.post("/upload-passport", response_model=VerificationResponse)
async def upload_passport(file: UploadFile = File(...)):
    try:
        # Save and process passport image
        file_path = await face_service.save_passport_image(file)
        face_service.process_passport_image(file_path)
        
        return VerificationResponse(
            success=True,
            message="Passport image processed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-face", response_model=VerificationResponse)
async def verify_face(file: UploadFile = File(...)):
    try:
        # Save verification image temporarily
        file_path = await face_service.save_passport_image(file)
        
        # Verify face
        result = face_service.verify_face_image(file_path)
        
        # Clean up temporary file
        os.remove(file_path)
        
        return VerificationResponse(
            success=True,
            message="Face verification completed",
            match_found=result["is_match"],
            confidence=result["confidence"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze-face")
async def analyze_face(file: UploadFile = File(...)):
    try:
        # Save image temporarily
        file_path = await face_service.save_passport_image(file)
        
        # Analyze face
        analysis = face_service.detect_face_landmarks(file_path)
        
        # Clean up temporary file
        os.remove(file_path)
        
        return {
            "success": True,
            "message": "Face analysis completed",
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 