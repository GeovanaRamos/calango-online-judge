const labels = JSON.parse(document.getElementById('labels').textContent);
const values = JSON.parse(document.getElementById('values').textContent);

// Results chart
const ctx = document.getElementById('resultsChart');
data = {
    datasets: [{
        data: values,
        backgroundColor: [
            '#e67e22',
            '#7fb3d5',
            '#d98880',
            '#DAF7A6',
            '#FFC300',
            '#FF5733',
            '#b03a2e',
        ],
    }],
    labels: labels
};

const myChart = new Chart(ctx, {
    type: 'pie',
    data: data,
    options: {
        legend: {
            position: 'right',
        },
    }
});