const labels = JSON.parse(document.getElementById('labels').textContent);
const values = JSON.parse(document.getElementById('values').textContent);
const concluded = JSON.parse(document.getElementById('concluded').textContent);
const pending = JSON.parse(document.getElementById('pending').textContent);

// Results chart
const ctx = document.getElementById('listsChart');
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


// Lists chart
let lists_labels;
if (concluded === 0 && pending === 0)
    lists_values = []
else
    lists_labels = ['Concluído', 'Pendente']
const ctx2 = document.getElementById('resultsChart');
data = {
    datasets: [{
        data: [concluded, pending],
        backgroundColor: [
            '#7fb3d5',
            '#d98880',
        ],
    }],
    labels: lists_labels
};
const resultsChart = new Chart(ctx2, {
    type: 'pie',
    data: data,
    options: {
        legend: {
            position: 'right',
        },
    }
});