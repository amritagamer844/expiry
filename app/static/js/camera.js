// Camera capture functionality
let currentStream;
let targetInputId;
let videoElement;
let canvasElement;
let previewElement;

function initCamera() {
    videoElement = document.getElementById('camera-video');
    canvasElement = document.getElementById('camera-canvas');
    previewElement = document.getElementById('camera-preview');

    // Setup camera capture buttons
    document.getElementById('capture-expiry-btn').addEventListener('click', function () {
        openCamera('expiry_image');
    });

    document.getElementById('capture-barcode-btn').addEventListener('click', function () {
        openCamera('barcode_image');
    });

    // Setup take photo button
    document.getElementById('take-photo-btn').addEventListener('click', takePhoto);

    // Setup use photo button
    document.getElementById('use-photo-btn').addEventListener('click', usePhoto);

    // When camera modal is closed, stop the stream
    $('#cameraModal').on('hidden.bs.modal', stopCamera);
}

function openCamera(inputId) {
    targetInputId = inputId;

    // Reset UI
    videoElement.style.display = 'block';
    previewElement.style.display = 'none';
    document.getElementById('take-photo-btn').style.display = 'block';
    document.getElementById('use-photo-btn').style.display = 'none';

    // Start camera with highest available resolution
    navigator.mediaDevices.getUserMedia({
        video: {
            width: { ideal: 1920 },
            height: { ideal: 1080 },
            facingMode: 'environment' // Use back camera on mobile devices
        },
        audio: false
    })
        .then(function (stream) {
            currentStream = stream;
            videoElement.srcObject = stream;

            // Show the camera modal
            const cameraModal = new bootstrap.Modal(document.getElementById('cameraModal'));
            cameraModal.show();
        })
        .catch(function (error) {
            console.error('Error accessing camera:', error);
            alert('Could not access the camera. Please make sure you have granted camera permissions.');
        });
}

function takePhoto() {
    if (!currentStream) return;

    // Get video dimensions
    const width = videoElement.videoWidth;
    const height = videoElement.videoHeight;

    // Set canvas dimensions to match video
    canvasElement.width = width;
    canvasElement.height = height;

    // Draw current video frame to canvas
    const context = canvasElement.getContext('2d');
    context.drawImage(videoElement, 0, 0, width, height);

    // Convert canvas to image
    const imageDataUrl = canvasElement.toDataURL('image/jpeg');
    previewElement.src = imageDataUrl;

    // Update UI
    videoElement.style.display = 'none';
    previewElement.style.display = 'block';
    document.getElementById('take-photo-btn').style.display = 'none';
    document.getElementById('use-photo-btn').style.display = 'block';
}

function usePhoto() {
    if (!previewElement.src) return;

    // Convert data URL to File object
    fetch(previewElement.src)
        .then(res => res.blob())
        .then(blob => {
            const file = new File([blob], `camera-capture-${Date.now()}.jpg`, { type: 'image/jpeg' });

            // Create a FileList-like object
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);

            // Set the file to the target input
            const fileInput = document.getElementById(targetInputId);
            fileInput.files = dataTransfer.files;

            // Trigger change event to update the UI
            const event = new Event('change', { bubbles: true });
            fileInput.dispatchEvent(event);

            // Close the modal
            const cameraModal = bootstrap.Modal.getInstance(document.getElementById('cameraModal'));
            cameraModal.hide();

            // Process the image automatically
            if (targetInputId === 'expiry_image') {
                document.getElementById('process-expiry-btn').click();
            } else if (targetInputId === 'barcode_image') {
                document.getElementById('process-barcode-btn').click();
            }
        });
}

function stopCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
}

// Initialize camera when the document is ready
document.addEventListener('DOMContentLoaded', initCamera);
