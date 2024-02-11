// Function to populate the camera selector
async function populateCameraSelector() {
    const cameraSelector = document.getElementById('camera-input');

    for(let i = cameraSelector.options.length - 1; i >= 0; i--) {
        cameraSelector.remove(i);
    }

    try {
        const devices = await navigator.mediaDevices.enumerateDevices();

        const cameras = devices.filter(device => device.kind === 'videoinput');

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
populateCameraSelector();

function getStreamFromDevice() {
    const video = document.getElementById('camera-output');
    const cameraSelector = document.getElementById('camera-input');

    const selectedDeviceId = cameraSelector.value;

    window.navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: selectedDeviceId } } })
        .then(stream => {
            video.srcObject = stream;
            video.onloadedmetadata = (e) => {
                video.play();
            };
        })
        .catch(() => {
            alert('You have given browser the permission to run Webcam and mic ;( ');
        });
}