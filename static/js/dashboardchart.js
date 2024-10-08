// Google Charts loader
google.charts.load('current', {'packages':['corechart']});

// Variables for storing chart data
let weightHistory = [0];
let turbHistory = [0];
let timeLabels = [new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })];

// Function to format time as HH:MM AM/PM
function formatTimeAMPM(timeString) {
    let [hours, minutes] = timeString.split(':');
    let ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12; // Convert to 12-hour format
    return `${hours}:${minutes} ${ampm}`;
}

// Function to draw charts
function drawCharts() {
    // Get containers and check if they exist before drawing the chart
    const turbChartContainer = document.getElementById('turbChart');
    const weightChartContainer = document.getElementById('weightChart');
    const summaryChartContainer = document.getElementById('summaryChart');

    if (!turbChartContainer || !weightChartContainer || !summaryChartContainer) {
        console.error('One or more chart containers are not defined.');
        return;  // Exit the function if containers are missing
    }

    // Draw Turbidity Chart
    let turbData = google.visualization.arrayToDataTable([
        ['Time', 'Turbidity'],
        ...timeLabels.map((time, index) => [formatTimeAMPM(time), turbHistory[index]])
    ]);
    let turbOptions = {title: 'Turbidity', curveType: 'function', legend: { position: 'bottom' }};
    let turbChart = new google.visualization.LineChart(turbChartContainer);
    turbChart.draw(turbData, turbOptions);

    // Draw Weight Chart
    let weightData = google.visualization.arrayToDataTable([
        ['Time', 'Weight (g)'],
        ...timeLabels.map((time, index) => [formatTimeAMPM(time), weightHistory[index]])
    ]);
    let weightOptions = {title: 'Bowl Weight (g)', curveType: 'function', legend: { position: 'bottom' }};
    let weightChart = new google.visualization.LineChart(weightChartContainer);
    weightChart.draw(weightData, weightOptions);

    // Draw Summary Chart
    let summaryData = google.visualization.arrayToDataTable([
        ['Time', 'Turbidity', 'Weight (g)'],
        ...timeLabels.map((time, index) => [formatTimeAMPM(time), turbHistory[index], weightHistory[index]])
    ]);
    let summaryOptions = {title: 'Summary', curveType: 'function', legend: { position: 'bottom' }};
    let summaryChart = new google.visualization.LineChart(summaryChartContainer);
    summaryChart.draw(summaryData, summaryOptions);
}

// Load Google Charts and set the callback once
google.charts.setOnLoadCallback(drawCharts);

// Periodic data fetch and update charts
setInterval(() => {
    fetch('/mqtt_data')
        .then(response => response.json())
        .then(data => {
            let currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            let bowlPercentage = parseFloat(data.waterlevelbowlpercentage);
            let turbidity = parseFloat(data.turbiditysensor);

            // Push new data into the arrays
            weightHistory.push(bowlPercentage);
            turbHistory.push(turbidity);
            timeLabels.push(currentTime);

            // Limit the history arrays to 100 entries
            if (weightHistory.length > 100) {
                weightHistory.shift();
                turbHistory.shift();
                timeLabels.shift();
            }

            // Draw charts after new data is pushed
            drawCharts();

            // Dynamic update for water quality
            if (isNaN(data.turbiditysensor)) {
                document.getElementById("water_quality_bowl").innerHTML = "<b style='color: gray;'>No sensor detected</b>";
                document.getElementById("notifyWarn").style.display = "block";
            } else if (data.turbiditysensor <= 1) {
                document.getElementById("water_quality_bowl").innerHTML = "<b style='color: green;'>Good</b>";
                document.getElementById("notifyWarn").style.display = "none";
            } else if (data.turbiditysensor <= 4.9) {
                document.getElementById("water_quality_bowl").innerHTML = "<b style='color: orange;'>Fair</b>";
                document.getElementById("notifyWarn").style.display = "none";
            } else {
                document.getElementById("water_quality_bowl").innerHTML = "<b style='color: red;'>Bad</b>";
                document.getElementById("notifyWarn").innerHTML = "<strong>Warning: </strong>Change water in bowl is necessary.";
                document.getElementById("notifyWarn").style.display = "block";
            }

            // Update bowl water level bar
            let bowlWaterElement = document.getElementById("bowlWaterLeft");

            bowlWaterElement.style.width = data.waterlevelbowlpercentage + "%";
            bowlWaterElement.setAttribute("aria-valuenow", data.waterlevelbowlpercentage);
            bowlWaterElement.innerHTML = data.waterlevelbowlpercentage + "%";

            // Add appropriate progress bar color
            bowlWaterElement.classList.remove('progress-bar-warning', 'progress-bar-danger', 'progress-bar-success');

            if (data.waterlevelbowlpercentage < 40) {
                bowlWaterElement.classList.add('progress-bar-danger');
            } else if (data.waterlevelbowlpercentage < 70) {
                bowlWaterElement.classList.add('progress-bar-warning');
            } else {
                bowlWaterElement.classList.add('progress-bar-success');
            }

            let waterLevelResolv = document.getElementById("waterLevelReserv");
            if (isNaN(data.waterlevelreservoir)) {
                waterLevelResolv.innerText = "No reservoir detected";
            }
            else {
                if (data.waterlevelreservoir == 1) {
                    waterLevelResolv.innerText = "Good (Enough water)";
                }
                else {
                    waterLevelResolv.innerText = "Low (Less water)";
                    document.getElementById("notifyWarn").innerHTML = "<strong>Warning: </strong>Refill water reservoir is required.";
                    document.getElementById("notifyWarn").style.display = "block";
                }
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}, 5000);

setInterval(() => {
    fetch('/conn_data')
        .then(response => response.json())
        .then(conndata => {
            document.getElementById("ipaddrdisplay").innerHTML = "<p>" + conndata.ipaddr + "</p>";
            document.getElementById("rssidisplay").innerText = conndata.rssi;
            if (conndata.rssi > 80 && conndata.rssi <= 99){
                document.getElementById("conntype").innerHTML = "<b>Wi-Fi</b>";
                document.getElementById("connquality").innerHTML = "<b style='color: red;'>Poor</b>";
                document.getElementById("notifyWarn").innerHTML = "<strong>Warning: </strong>Connection is poor. Please consider to change the position.";
                document.getElementById("notifyWarn").style.display = "block";
            } else if (conndata.rssi > 67 && conndata.rssi <= 80) {
                document.getElementById("conntype").innerHTML = "<b>Wi-Fi</b>";
                document.getElementById("connquality").innerHTML = "<b style='color: orange;'>Fair</b>";
                document.getElementById("notifyWarn").style.display = "none";
            } else if (conndata.rssi >= 0 && conndata.rssi <= 67) {
                document.getElementById("conntype").innerHTML = "<b>Wi-Fi</b>";
                document.getElementById("connquality").innerHTML = "<b style='color: green;'>Good</b>";
                document.getElementById("notifyWarn").style.display = "none";
            } else {
                document.getElementById("conntype").innerHTML = "<b>Network Cable or unknown</b>";
                document.getElementById("connquality").innerHTML = "<b style='color: gray;'>Unknown or cable connection</b>";
                document.getElementById("notifyWarn").innerHTML = "<strong>Warning: </strong>Prototype is not connected to Wi-Fi, or using cable connection.";
                document.getElementById("notifyWarn").style.display = "block";
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}, 2000);
