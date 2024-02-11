// Imports of the libraries specified in Cargo.toml
use actix_web::{get, App, HttpServer, Responder}; // Library to build a web/API server
use byteorder::{ByteOrder, LittleEndian}; // Library to process the byte forms and the input of the serial ports
use serialport::new; // Connection to the serial port -> in this case to the GPIO pins of the Raspberry Pi to which the LiDAR is connected
use std::time::Duration; // Time library

// Method to create the route of the API
#[get("/")]
async fn index() -> impl Responder {
    // Get the distance value from the measure method below and format it to JSON to display it on API request
    let value = recursive_measure().await; // Await because recursive, to avoid hardware errors which return 0
    format!("{}", value);
}

// Main method -> will start automatically after starting the script
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Create the HTTP server -> bind it to the machine's IP and to port 8080
    HttpServer::new(|| {
        App::new().service(index)
    })
    .bind("0.0.0.0:8080")?
    .run()
    .await
}

// Async measure function, for the case a hardware error happens -> measure returns 0 -> to avoid error, it will measure again until the error is eliminated
async fn recursive_measure() -> u16 {
    // Loop = while true
    loop {
        // Calling measure method
        let result = measure();
        // If not 0 -> breaking out, returning result (in Rust not explicitly written)
        if result != 0 {
            break result;
        }
    }
}

// Method to call the serial port input of the LiDAR
fn measure() -> u16 {
    // Initializing the distance variable
    let mut distance: u16 = 0;

    // Initializing port variable -> assigning hardware interface to this variable
    let mut port = match new("/dev/ttyAMA0", 115200)
        .timeout(Duration::from_millis(100))
        .open()
    {
        Ok(port) => port,
        Err(_e) => {
            return 0;
        }
    };

    // Define an array to store the received data
    let mut buf = [0u8; 9];
    // Try to read in data from the serial port
    match port.read(buf.as_mut()) {
        Ok(_) => {
            // If it works:
            // Check if the data signal is correct by checking the starting bits
            if buf[0] == 0x59 && buf[1] == 0x59 {
                // If ok, read in distance (2nd and 3rd bit)
                distance = LittleEndian::read_u16(&buf[2..4]);
                // Other bits are temperature and strength
            } else {
                return 0; // For the case the start bits are wrong, just measure again -> solves the problem
            }
        }
        Err(e) => {
            // If reading in data does not work, raising error
            eprintln!("{:?}", e);
        }
    }
    return distance;
}