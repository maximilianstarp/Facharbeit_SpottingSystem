// Calculate and set the correct size of the camera stream
function setCameraSize() {
    const cameraParent = document.getElementById('video-parent');
    const cameraOutput = document.getElementById('camera-output');
  
    // Calculate and retrieve the width and height of the div
    const height = cameraParent.clientHeight;
    cameraOutput.style.height = `${height}px`;
}

// Event listener for window resize to update the camera size accordingly
window.addEventListener('resize', setCameraSize);
// Set the camera size on the first call
setCameraSize();

// Function to store server input data
function submitData() {
    // Retrieve input values
    ipServer = document.getElementById('ip-server-input').value;
    token = document.getElementById('token-input').value;
    show = document.getElementById('show-input').value;

    // Store input values in local storage if they are not empty
    if (ipServer != "") localStorage.setItem("ip-server", ipServer);
    if (token != "") localStorage.setItem("token", token)
    if (show != "") localStorage.setItem("show", show)

    // Set placeholder values
    setPlaceholder();
}

// Function to set placeholder server data
function setPlaceholder(){
    document.getElementById('ip-server-input').placeholder = localStorage.getItem("ip-server");
    document.getElementById('token-input').placeholder = localStorage.getItem("token");
    document.getElementById('show-input').placeholder = localStorage.getItem("show");
}
setPlaceholder();

// Function to handle returned data
async function handleReturnValues(data) {
    try {
        // Update UI elements with returned data
        document.getElementById('out-dist').value = data.Distance;
        document.getElementById('out-point').value = `(${data.Point.x},${data.Point.y},${data.Point.z})`;
        document.getElementById('out-pan-mh').value = data['Pan-MH'];
        document.getElementById('out-tilt-mh').value = data['Tilt-MH'];
        document.getElementById('out-pan-cam').value = data['Pan-Cam'];
        document.getElementById('out-tilt-cam').value = data['Tilt-Cam'];
    } catch {
        // Handle error if data retrieval fails
        document.getElementById('out-dist').value = "Return Error";
    }
}

// Function to handle fetch errors
async function handleFetchErrors(error) {
    switch(error) {
        case "Controller not Found/Wrong Controller":
            // Indicate error if controller is not found or incorrect
            document.getElementById('controller-input').classList.add('error');
            break;
        case "Controller found":
            // Remove error if controller is found
            document.getElementById('controller-input').classList.remove('error');
            break;
        case 401:
            // Indicate error for unauthorized access
            document.getElementById('token-input').classList.add('error');
            document.getElementById('ip-server-input').classList.remove('error');
            document.getElementById('show-input').classList.remove('error');
            break;
        case 405:
            // Indicate error for method not allowed
            document.getElementById('show-input').classList.add('error');
            document.getElementById('token-input').classList.remove('error');
            document.getElementById('ip-server-input').classList.remove('error');
            break;
        case 402:
            // Indicate error for payment required
            document.getElementById('show-input').classList.add('error');
            document.getElementById('token-input').classList.add('error');
            document.getElementById('ip-server-input').classList.remove('error');
            break;
        case "Server not found":
            // Indicate error if server is not found
            document.getElementById('ip-server-input').classList.add('error');
            document.getElementById('token-input').classList.remove('error');
            document.getElementById('show-input').classList.remove('error');
            break;
        case 200:
            // Remove errors
            document.getElementById('token-input').classList.remove('error');
            document.getElementById('ip-server-input').classList.remove('error');
            document.getElementById('show-input').classList.remove('error');
            break;
    }
}

// Function to clear error state
function clearErrorState() {
    // Remove the error class from all text fields
    const inputElements = document.querySelectorAll('#server input, #inputs select');
    inputElements.forEach(inputElement => {
        inputElement.classList.remove('error');
    });
}
