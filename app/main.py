from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from fastapi.responses import HTMLResponse # type: ignore
from app.api.endpoints import verification

app = FastAPI(title="Face Verification API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add root route
@app.get("/")
async def root():
    return {
        "message": "Face Verification API",
        "docs": "/docs",
        "endpoints": {
            "upload_passport": "/api/v1/upload-passport",
            "verify_face": "/api/v1/verify-face",
            "analyze_face": "/api/v1/analyze-face"
        }
    }


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(verification.router, prefix="/api/v1")

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Face Verification Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { display: flex; gap: 20px; }
            .section { flex: 1; padding: 20px; border: 1px solid #ccc; border-radius: 5px; }
            #status { margin-top: 20px; padding: 10px; border-radius: 5px; }
            .success { background-color: #dff0d8; color: #3c763d; }
            .error { background-color: #f2dede; color: #a94442; }
            video { width: 100%; max-width: 400px; }
            #passportPreview { max-width: 400px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <h1>Face Verification System Demo</h1>
        
        <div class="container">
            <div class="section">
                <h2>Step 1: Upload Passport Photo</h2>
                <input type="file" id="passportInput" accept="image/*">
                <img id="passportPreview" style="display: none;">
                <div id="uploadStatus"></div>
            </div>
            
            <div class="section">
                <h2>Step 2: Live Verification</h2>
                <video id="webcam" autoplay playsinline></video>
                <button id="verifyButton">Start Verification</button>
                <div id="verificationStatus"></div>
            </div>
        </div>

        <script>
            let isVerifying = false;
            let passportUploaded = false;

            // Passport upload handling
            document.getElementById('passportInput').addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (!file) return;

                // Show preview
                const preview = document.getElementById('passportPreview');
                preview.src = URL.createObjectURL(file);
                preview.style.display = 'block';

                // Upload to server
                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/api/v1/upload-passport', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    
                    if (result.success) {
                        document.getElementById('uploadStatus').innerHTML = 
                            '<div class="success">Passport uploaded successfully!</div>';
                        passportUploaded = true;
                    } else {
                        throw new Error(result.message);
                    }
                } catch (error) {
                    document.getElementById('uploadStatus').innerHTML = 
                        `<div class="error">Upload failed: ${error.message}</div>`;
                }
            });

            // Webcam handling
            async function setupWebcam() {
                const video = document.getElementById('webcam');
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    video.srcObject = stream;
                } catch (error) {
                    console.error('Error accessing webcam:', error);
                }
            }

            // Verification handling
            document.getElementById('verifyButton').addEventListener('click', async () => {
                if (!passportUploaded) {
                    alert('Please upload a passport photo first!');
                    return;
                }

                isVerifying = !isVerifying;
                const button = document.getElementById('verifyButton');
                button.textContent = isVerifying ? 'Stop Verification' : 'Start Verification';

                if (isVerifying) {
                    verificationLoop();
                }
            });

            async function verificationLoop() {
                if (!isVerifying) return;

                const video = document.getElementById('webcam');
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                canvas.getContext('2d').drawImage(video, 0, 0);

                // Convert canvas to blob
                const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
                const formData = new FormData();
                formData.append('file', blob);

                try {
                    const response = await fetch('/api/v1/verify-face', {
                        method: 'POST',
                        body: formData
                    });
                    const result = await response.json();
                    
                    const status = document.getElementById('verificationStatus');
                    if (result.match_found) {
                        status.innerHTML = `<div class="success">
                            Match found! Confidence: ${(result.confidence * 100).toFixed(2)}%
                        </div>`;
                    } else {
                        status.innerHTML = `<div class="error">No match found</div>`;
                    }
                } catch (error) {
                    console.error('Verification error:', error);
                }

                if (isVerifying) {
                    setTimeout(verificationLoop, 1000); // Check every second
                }
            }

            // Initialize webcam on page load
            setupWebcam();
        </script>
    </body>
    </html>
    """
