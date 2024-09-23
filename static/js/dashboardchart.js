// Google Charts loader
google.charts.load('current', {'packages':['corechart']});

// Variables for storing chart data
let waterlevelHistory = [];
let weightHistory = [];
let turbHistory = [];
let timeLabels = [];

function formatTimeAMPM(timeString) {
    let [hours, minutes] = timeString.split(':');
    let ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12; // Convert to 12-hour format
    return `${hours}:${minutes} ${ampm}`;
}

// Function to draw charts
function drawCharts() {
    // Draw Water Level Chart
    let waterlevelData = google.visualization.arrayToDataTable([
        ['Time', 'Water Level'],
        ...timeLabels.map((time, index) => [formatTimeAMPM(time), waterlevelHistory[index]])
    ]);
    let waterlevelOptions = {title: 'Water Level', curveType: 'function', legend: { position: 'bottom' }};
    let waterlevelChart = new google.visualization.LineChart(document.getElementById('waterlevelChart'));
    waterlevelChart.draw(waterlevelData, waterlevelOptions);

    // Draw Turbidity Chart
    let turbData = google.visualization.arrayToDataTable([
        ['Time', 'Turbidity'],
        ...timeLabels.map((time, index) => [formatTimeAMPM(time), turbHistory[index]])
    ]);
    let turbOptions = {title: 'Turbidity', curveType: 'function', legend: { position: 'bottom' }};
    let turbChart = new google.visualization.LineChart(document.getElementById('turbChart'));
    turbChart.draw(turbData, turbOptions);

    // Draw Weight Chart
    let weightData = google.visualization.arrayToDataTable([
        ['Time', 'Weight'],
        ...timeLabels.map((time, index) => [formatTimeAMPM(time), weightHistory[index]])
    ]);
    let weightOptions = {title: 'Bowl Weight', curveType: 'function', legend: { position: 'bottom' }};
    let weightChart = new google.visualization.LineChart(document.getElementById('weightChart'));
    weightChart.draw(weightData, weightOptions);

    // Draw Summary Chart
    let summaryData = google.visualization.arrayToDataTable([
        ['Time', 'Water Level', 'Turbidity', 'Weight'],
        ...timeLabels.map((time, index) => [formatTimeAMPM(time), waterlevelHistory[index], turbHistory[index], weightHistory[index]])
    ]);
    let summaryOptions = {title: 'Summary', curveType: 'function', legend: { position: 'bottom' }};
    let summaryChart = new google.visualization.LineChart(document.getElementById('summaryChart'));
    summaryChart.draw(summaryData, summaryOptions);
}

// Fetch and update data every 5 seconds
setInterval(() => {
    fetch('/mqtt_data')
        .then(response => response.json())
        .then(data => {
            let currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            let waterLevel = parseFloat(data.waterlevelreservoir);
            let bowlPercentage = parseFloat(data.waterlevelbowlpercentage);
            let turbidity = parseFloat(data.turbiditysensor);

            waterlevelHistory.push(waterLevel);
            weightHistory.push(bowlPercentage);
            turbHistory.push(turbidity);
            timeLabels.push(currentTime);

            // Maintain a max history size of 100 entries
            if (waterlevelHistory.length > 100) {
                waterlevelHistory.shift();
                weightHistory.shift();
                turbHistory.shift();
                timeLabels.shift();
            }

            // After data is fetched, draw charts immediately
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

            // Update bowl and reservoir water level bars
            let bowlWaterElement = document.getElementById("bowlWaterLeft");
            let reservWaterLeftIcon = document.getElementById("reservWaterLeft");

            reservWaterLeftIcon.style.width = data.waterlevelreservoir + "%";
            reservWaterLeftIcon.setAttribute("aria-valuenow", data.waterlevelreservoir);
            reservWaterLeftIcon.innerHTML = data.waterlevelreservoir + "%";

            bowlWaterElement.style.width = data.waterlevelbowlpercentage + "%";
            bowlWaterElement.setAttribute("aria-valuenow", data.waterlevelbowlpercentage);
            bowlWaterElement.innerHTML = data.waterlevelbowlpercentage + "%";

            // Add appropriate progress bar color
            reservWaterLeftIcon.classList.remove('progress-bar-warning', 'progress-bar-danger', 'progress-bar-success');
            bowlWaterElement.classList.remove('progress-bar-warning', 'progress-bar-danger', 'progress-bar-success');

            if (data.waterlevelbowlpercentage < 40) {
                bowlWaterElement.classList.add('progress-bar-danger');
            } else if (data.waterlevelbowlpercentage < 70) {
                bowlWaterElement.classList.add('progress-bar-warning');
            } else {
                bowlWaterElement.classList.add('progress-bar-success');
            }

            if (data.waterlevelreservoir < 40) {
                reservWaterLeftIcon.classList.add('progress-bar-danger');
            } else if (data.waterlevelreservoir < 70) {
                reservWaterLeftIcon.classList.add('progress-bar-warning');
            } else {
                reservWaterLeftIcon.classList.add('progress-bar-success');
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}, 5000);

// Periodically fetch connection data
setInterval(() => {
    fetch('/conn_data')
        .then(response => response.json())
        .then(conndata => {
            document.getElementById("ipaddrdisplay").innerHTML = "<p>" + conndata.ipaddr + "</p>";
            document.getElementById("rssidisplay").innerText = "-" + conndata.rssi;
            if (conndata.rssi > 80 && conndata.rssi <= 99){
                document.getElementById("conntype").innerHTML = "<b>Wi-Fi</b>";
                document.getElementById("connquality").innerHTML = "<b style='color: red;'>Poor</b>";
            } else if (conndata.rssi > 67 && conndata.rssi <= 80) {
                document.getElementById("conntype").innerHTML = "<b>Wi-Fi</b>";
                document.getElementById("connquality").innerHTML = "<b style='color: orange;'>Fair</b>";
            } else if (conndata.rssi >= 0 && conndata.rssi <= 67) {
                document.getElementById("conntype").innerHTML = "<b>Wi-Fi</b>";
                document.getElementById("connquality").innerHTML = "<b style='color: green;'>Good</b>";
            } else {
                document.getElementById("conntype").innerHTML = "<b>Copper (Network Cable) or unknown</b>";
                document.getElementById("connquality").innerHTML = "<b style='color: gray;'>Unknown or copper connection</b>";
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}, 2000);
