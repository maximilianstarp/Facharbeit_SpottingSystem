// Function to populate the controller selector
async function populateControllerSelector() {
    // Get the controller selector element
    const controllerSelector = document.getElementById('controller-input');

    // Remove all existing options from the controller selector
    for (let i = controllerSelector.options.length - 1; i >= 0; i--) {
        controllerSelector.remove(i);
    }

    try {
        // Get the list of connected gamepads
        const gamepads = navigator.getGamepads();

        // Iterate over each gamepad and add it as an option to the controller selector
        gamepads.forEach(gamepad => {
            if (gamepad && gamepad.buttons.length > 0 && gamepad.axes.length > 0) {
                const option = document.createElement('option');
                option.value = gamepad.id;
                option.text = gamepad.id;
                controllerSelector.appendChild(option);
            }
        });
    } catch (error) {
        console.error('Error enumerating devices:', error);
    }
}

// Call the function to populate the controller selector
populateControllerSelector();

// Function to get data from the selected controller
function getDataFromController(gamepadId) {
    // Get the list of connected gamepads
    const gamepads = navigator.getGamepads();
    // Find the gamepad with the matching ID
    const gamepad = Array.from(gamepads).find(gamepad => gamepad && gamepad.id === gamepadId);

    // Controller output Construct
    const retVal = {"Axis 0": 0, "Axis 1": 0};

    // Loop for 1st and 2nd axis of PS4 Controller (Left Stick)
    for (let k = 0; k < 2; k++) {
        let axisValue = gamepad.axes[k];

        const deadZoneThreshold = 0.2;
        // Handle axis value here
        if (Math.abs(axisValue) < deadZoneThreshold) {
            axisValue = 0;
        }

        // Fill the return value
        retVal['Axis ' + k] = axisValue * (-1);
    }
    return retVal;
}
