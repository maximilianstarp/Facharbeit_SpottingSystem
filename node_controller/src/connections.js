async function sendData(isFirst) {
    const serverIp = localStorage.getItem("ip-server");
    const serverToken = localStorage.getItem("token");
    const serverShow = localStorage.getItem("show");
    const gamepadId = document.getElementById('controller-input').value;

    let cData;

    try {
        cData = getDataFromController(gamepadId);
    } catch (error) {
        handleFetchErrors("Controller not Found/Wrong Controller");
        // Retry on the next frame if c_data is not received
        requestAnimationFrame(() => sendData(false));
        return;
    }
    // If c_data is still undefined after trying to get it, retry on the next frame
    if (typeof cData === 'undefined') {
        handleFetchErrors("Controller not Found/Wrong Controller");
        requestAnimationFrame(() => sendData(false));
        return;
    }
    handleFetchErrors("Controller found")

    // Define the f_data based on the input elements
    let fData = {
        "speed": document.getElementById("speed-fader").value,
        "dim": document.getElementById("dim-fader").value,
        "cto": document.getElementById("cto-fader").value,
        "zoom": document.getElementById("zoom-fader").value,
        "focus": document.getElementById("focus-fader").value
    };
    // In first Loop, set new data = old data before comparing
    if(isFirst) localStorage.setItem("f-data-old", JSON.stringify(fData))

    if (JSON.stringify(cData) === JSON.stringify({ 'Axis 0':0, 'Axis 1':0 }) && JSON.stringify(fData) === localStorage.getItem("f-data-old")) {
        requestAnimationFrame(() => sendData(false));
        return;
    }

    // Update f_data_old in local storage
    localStorage.setItem("f-data-old", JSON.stringify(fData))

    // Construct the fetch URL with the server IP and the endpoint path
    const url = `http://${serverIp}/controller/input?show_name=${serverShow}&data_input=${JSON.stringify(Object.assign({}, fData, cData))}`;

    // Construct the request options
    const options = {
        method: 'POST',
        headers: {
            'Authorization': `${serverToken}`,
            'Content-Type': 'application/json'
        }
    };

    try {
        const response = await fetch(url, options);
        handleFetchErrors(response.status)
        const data = await response.json();
        handleReturnValues(data);
    } catch (error) {
        handleFetchErrors("Server not found")
    }

    // Schedule the next frame to call send_data again
    requestAnimationFrame(() =>  {
        sendData(false);
    });
}
sendData(true);