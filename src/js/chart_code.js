async function get_sensor_data(sensor_name) {
    var url = `/get_sensor_data/${sensor_name}`;
    try {
        const response = await fetch(url);
        if (!response.ok) {
            console.error('Server responded with not OK status');
            return [];
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        return [];
    }
};

async function update_chart() {
    var dropdown = document.getElementById('sensor-select');
    var chart_name = dropdown.options[dropdown.selectedIndex].text;
    // replace spaces with underscores
    data = await get_sensor_data(chart_name.split(' ').join('_'));

    // remove old chart if it exists
    let chartStatus = Chart.getChart('simple_chart');
    if (chartStatus != undefined) {
        chartStatus.destroy();
    }

    const ctx = document.getElementById('simple_chart').getContext('2d');
    const new_chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: data['data'].length }, (_, i) => i + 1),
            datasets: [{
                label: `Sensor data for ${chart_name}`,
                data: data['data'],
                fill: false
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    ticks: {
                        // don't show all labels
                        callback: function(value, index, values) {
                            if (value % 500 === 0 || value === 0) {
                                return value;
                            }
                        }
                    },
                    display: true,
                    title: {
                        display: true,
                        text: 'Most recent'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Value'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            responsive: true,
            maintainAspectRatio: false
        }
    });
};

window.onload = function(event) {
    update_chart();
    var menu = document.getElementById('sensor-select');
    menu.addEventListener('change', function() {
        update_chart();
    });
};
