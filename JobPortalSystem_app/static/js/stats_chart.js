document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('jobStatsChart').getContext('2d');
    const chartJobTitles = JSON.parse(document.getElementById('jobTitlesData').textContent);
    const chartAppCounts = JSON.parse(document.getElementById('appCountsData').textContent);

    if (chartJobTitles.length && chartAppCounts.length) {
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartJobTitles,
                datasets: [{
                    label: 'Số lượng ứng viên',
                    data: chartAppCounts,
                    backgroundColor: 'rgba(0, 150, 136, 0.7)',
                    borderRadius: 8,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Thống kê ứng viên theo bài đăng', color: '#009688', font: { size: 18, weight: 'bold' } }
                },
                scales: {
                    x: { 
                        title: { display: true, text: 'Bài đăng', color: '#009688', font: { weight: 'bold' } },
                        ticks: { color: '#00796b', font: { weight: 'bold' } }
                    },
                    y: { 
                        title: { display: true, text: 'Số lượng ứng viên', color: '#009688', font: { weight: 'bold' } }, 
                        beginAtZero: true,
                        ticks: { color: '#00796b', font: { weight: 'bold' } }
                    }
                }
            }
        });
    }
});