// ##################### RESULTS CHART #######################
const results = JSON.parse(document.getElementById('results').textContent);
const labels = []
const values = []
results.map(item => {
    labels.push(item.result_display)
    values.push(item.count)
})

const ctx = document.getElementById('resultsChart');
const myChart = new Chart(ctx, {
    type: 'pie',
    data: {
        datasets: [{
            data: values,
            backgroundColor: [
                '#8fd57f', '#DAF7A6', '#e67e22', '#d98880',
                '#FFC300', '#FF5733', '#b03a2e',
            ],
        }],
        labels: labels
    },
    options: {
        legend: {
            position: 'right',
        },
    }
});

// ##################### DAY OF WEEK #######################

const weekday = JSON.parse(document.getElementById('weekday').textContent);
const labels2 = []
const values2 = []
const dia = ["Domingo", "Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado"];
weekday.map(item => {
    labels2.push(dia[item.weekday - 1])
    values2.push(item.count)
})

const ctx2 = document.getElementById('weekdayChart');

const weekdayChart = new Chart(ctx2, {
    type: 'pie',
    data: {
        datasets: [{
            data: values2,
            backgroundColor: [
                '#8fd57f', '#DAF7A6', '#e67e22', '#d98880',
                '#FFC300', '#FF5733', '#b03a2e',
            ],
        }],
        labels: labels2
    },
    options: {
        legend: {
            position: 'right',
        },
    }
});