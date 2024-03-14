// Function to populate the camera selector
async function populateCameraSelector() {
    // Get the camera selector element
    const cameraSelector = document.getElementById('camera-input');

    // Remove all existing options from the camera selector
    for (let i = cameraSelector.options.length - 1; i >= 0; i--) {
        cameraSelector.remove(i);
    }

    try {
        // Enumerate all media devices
        const devices = await navigator.mediaDevices.enumerateDevices();

        // Filter out only video input devices (cameras)
        const cameras = devices.filter(device => device.kind === 'videoinput');

        // Add each camera as an option to the camera selector
        cameras.forEach(camera => {
            const option = document.createElement('option');
            option.value = camera.deviceId;
            option.text = camera.label;
            cameraSelector.appendChild(option);
        });
    } catch (error) {
        console.error('Error enumerating devices:', error);
    }
}

// Call the function to populate the camera selector
populateCameraSelector();

// Function to get the stream from the selected camera device
function getStreamFromDevice() {
    // Get the video element for displaying the camera output
    const video = document.getElementById('camera-output');
    // Get the camera selector element
    const cameraSelector = document.getElementById('camera-input');

    // Get the ID of the selected camera device
    const selectedDeviceId = cameraSelector.value;

    // Request access to the selected camera device
    window.navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: selectedDeviceId } } })
        .then(stream => {
            // Set the stream as the source for the video element
            video.srcObject = stream;
            // Play the video once metadata is loaded
            video.onloadedmetadata = (e) => {
                video.play();
            };
        })
        .catch(() => {
            // Alert the user if permission to access the camera is denied
            alert('You have denied the browser permission to access the webcam and microphone.');
        });
}
