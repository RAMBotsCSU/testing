// Assume you have a WebSocket connection
var socket = new WebSocket("ws://yourserveraddress");

// Chart.js dataset initialization
var data = {
    labels: [],
    datasets: [{
        label: "Strength Data",
        borderColor: "blue",
        backgroundColor: "rgba(0, 0, 255, 0.2)",
        data: []
    }]
};

// Initialize Chart.js instance
var ctx = document.getElementById("myChart").getContext("2d");
var chart = new Chart(ctx, {
    type: "line",
    data: data,
    options: {
        responsive: true,
        scales: {
            x: { display: true },
            y: { display: true }
        }
    }
});

// Function to generate a timestamp for labels
function startTime() {
    return new Date().toLocaleTimeString();
}

// WebSocket event listener for incoming messages
socket.onmessage = function(event) {
    console.log("Raw event data:", event.data);
    
    try {
        var myObj = JSON.parse(event.data);
        var keys = Object.keys(myObj);

        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            console.log("Processing key:", key);

            if (key === "Strength") {
                var force = parseFloat(myObj[key]);
                console.log("Force value:", force);

                if (!isNaN(force)) {
                    data.labels.push(startTime());
                    data.datasets[0].data.push(force);
                    
                    // Keep only the last 20 data points for better visualization
                    if (data.labels.length > 20) {
                        data.labels.shift();
                        data.datasets[0].data.shift();
                    }

                    chart.update(); // Update the chart
                } else {
                    console.error("Invalid force value for Strength:", myObj[key]);
                }
            }

            // Update the HTML element with the same ID as the key, if it exists
            var element = document.getElementById(key);
            if (element) {
                element.innerHTML = myObj[key];
            } else {
                console.warn(`Element with ID '${key}' not found.`);
            }
        }
    } catch (error) {
        console.error("Error parsing JSON:", error);
    }
};

// Handle WebSocket connection errors
socket.onerror = function(error) {
    console.error("WebSocket Error:", error);
};

// Handle WebSocket closure
socket.onclose = function() {
    console.warn("WebSocket connection closed.");
};
