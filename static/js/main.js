function triggerAction(action) {
    const url = "/manualactions/" + action;
    disableButtons(); // Temporary disable button to avoid from send multiple requests

    fetch(url)
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return response.text().then(text => { throw new Error(text || 'Unexpected error.'); });
        }
    })
    .then(data => {
        alert('Action "' + action + '" completed successfully.');
        window.location.href = '/dashboard';
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
        alert('Action failed: ' + error.message);
    })
    .finally(() => {
        enableButtons(); // Make button usable
    });
}

function disableButtons() {
    document.querySelectorAll('button').forEach(button => {
        button.disabled = true;
    });
}

function enableButtons() {
    document.querySelectorAll('button').forEach(button => {
        button.disabled = false;
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('RefreshPage').addEventListener('click', function() {
        location.reload();
    });

    document.getElementById('ChangeWater').addEventListener('click', function() {
        triggerAction('changewater');
    });

    document.getElementById('RefillWater').addEventListener('click', function() {
        triggerAction('refillwater');
    });

    document.getElementById('IntakeAnalysis').addEventListener('click', function() {
        triggerAction('dailyanalysis');
    });

    document.getElementById('CloseValve').addEventListener('click', function() {
        triggerAction('closevalve');
    });

    document.getElementById('ResetFeeder').addEventListener('click', function() {
        if (confirm("Danger Zone - You will lose connection with prototype for few minutes. Do you wish to continue?")) {
            triggerAction('restartfeeder');
        } else {
            return;
        }
    });
});


