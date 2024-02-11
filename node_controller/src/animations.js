// camera stream correct size calculation
function setCameraSize() {
    const cameraParent = document.getElementById('video-parent');
    const cameraOutput = document.getElementById('camera-output');
  
    // Calculate and retrieve the width and height of the div
    const height = cameraParent.clientHeight;
    cameraOutput.style.height = `${height}px`;
}
// eventlistener for resize the window -> update the camera size
window.addEventListener('resize', setCameraSize);
// on first call set size
setCameraSize();

// server input storing
function submitData() {
    ipServer = document.getElementById('ip-server-input').value;
    token = document.getElementById('token-input').value;
    show = document.getElementById('show-input').value;

    if (ipServer != "") localStorage.setItem("ip-server", ipServer);
    if (token != "") localStorage.setItem("token", token)
    if (show != "") localStorage.setItem("show", show)

    setPlaceholder();
}

// placeholder server data
function setPlaceholder(){
    document.getElementById('ip-server-input').placeholder = localStorage.getItem("ip-server");
    document.getElementById('token-input').placeholder = localStorage.getItem("token");
    document.getElementById('show-input').placeholder = localStorage.getItem("show");
}
setPlaceholder();

// handle return data function
async function handleReturnValues(data) {
    try {
        document.getElementById('out-dist').value = data.Distance;
        document.getElementById('out-point').value = `(${data.Point.x},${data.Point.y},${data.Point.z})`;
        document.getElementById('out-pan-mh').value = data['Pan-MH'];
        document.getElementById('out-tilt-mh').value = data['Tilt-MH'];
        document.getElementById('out-pan-cam').value = data['Pan-Cam'];
        document.getElementById('out-tilt-cam').value = data['Tilt-Cam'];
    } catch {
        document.getElementById('out-dist').value = "Return Error";
    }

}

// handle errors
async function handleFetchErrors(error) {
    switch(error) {
        case "Controller not Found/Wrong Controller":
            document.getElementById('controller-input').classList.add('error');
            break;
        case "Controller found":
            document.getElementById('controller-input').classList.remove('error');
            break;
        case 401:
            document.getElementById('token-input').classList.add('error');
            document.getElementById('ip-server-input').classList.remove('error');
            document.getElementById('show-input').classList.remove('error');
            break;
        case 405:
            document.getElementById('show-input').classList.add('error');
            document.getElementById('token-input').classList.remove('error');
            document.getElementById('ip-server-input').classList.remove('error');
            break;
        case 402:
            document.getElementById('show-input').classList.add('error');
            document.getElementById('token-input').classList.add('error');
            document.getElementById('ip-server-input').classList.remove('error');
            break;
        case "Server not found":
            document.getElementById('ip-server-input').classList.add('error');
            document.getElementById('token-input').classList.remove('error');
            document.getElementById('show-input').classList.remove('error');
            break;
        case 200:
            document.getElementById('token-input').classList.remove('error');
            document.getElementById('ip-server-input').classList.remove('error');
            document.getElementById('show-input').classList.remove('error');
            break;
    }
}

function clearErrorState() {
    // Remove the error class from all text fields
    const inputElement = document.querySelectorAll('#server input, #inputs select');
    inputElement.forEach(inputElement => {
        inputElement.classList.remove('error');
    });
}