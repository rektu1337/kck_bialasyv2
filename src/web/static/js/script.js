let profilesData = {};
let chartInstance = null;

// Fetch data from local Flask API
async function loadData() {
    try {
        const response = await fetch('/api/profiles');
        profilesData = await response.json();
        populateUserSelect();
    } catch (error) {
        console.error("Błąd podczas pobierania danych:", error);
    }
}

function populateUserSelect() {
    const select = document.getElementById('userSelect');
    select.innerHTML = '';
    const users = Object.keys(profilesData);
    
    if (users.length === 0) {
        select.innerHTML = '<option value="">Brak danych</option>';
        return;
    }

    users.forEach(user => {
        const opt = document.createElement('option');
        opt.value = user;
        opt.textContent = user;
        select.appendChild(opt);
    });

    // Trigger update for first user
    updateDashboard(users[0]);
    
    select.addEventListener('change', (e) => {
        updateDashboard(e.target.value);
    });
}

function updateDashboard(username) {
    if (!profilesData[username]) return;

    const data = profilesData[username];
    const total = data.total_reps || 0;
    const perfect = data.perfect_reps || 0;
    const history = data.history || [];

    // Update top stats
    document.getElementById('statTotalReps').textContent = total;
    document.getElementById('statPerfectReps').textContent = perfect;
    
    const accuracy = total > 0 ? Math.round((perfect / total) * 100) : 0;
    document.getElementById('statAccuracy').textContent = accuracy + '%';

    // Prepare chart data
    const labels = history.map(session => session.date);
    const repsData = history.map(session => session.reps);
    const perfectData = history.map(session => session.perfect_reps);

    renderChart(labels, repsData, perfectData);
}

function renderChart(labels, repsData, perfectData) {
    const ctx = document.getElementById('historyChart').getContext('2d');
    
    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Wszystkie powtórzenia',
                    data: repsData,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                },
                {
                    label: 'Perfekcyjne powtórzenia',
                    data: perfectData,
                    borderColor: '#2196F3',
                    backgroundColor: 'rgba(33, 150, 243, 0.2)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#444' },
                    ticks: { color: '#ccc' }
                },
                x: {
                    grid: { color: '#444' },
                    ticks: { color: '#ccc' }
                }
            },
            plugins: {
                legend: { labels: { color: '#fff' } }
            }
        }
    });
}

// Init
loadData();