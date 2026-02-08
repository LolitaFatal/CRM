document.addEventListener('DOMContentLoaded', async () => {
    // Revenue Bar Chart
    try {
        const revRes = await fetch('/api/dashboard/revenue-chart');
        const revData = await revRes.json();

        if (revData.success) {
            const ctx = document.getElementById('revenueChart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: revData.data.labels,
                        datasets: [{
                            label: 'הכנסות (₪)',
                            data: revData.data.values,
                            backgroundColor: 'rgba(25, 127, 230, 0.7)',
                            borderColor: '#197fe6',
                            borderWidth: 1,
                            borderRadius: 6,
                            borderSkipped: false,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                rtl: true,
                                textDirection: 'rtl',
                                callbacks: {
                                    label: (ctx) => `₪${ctx.parsed.y.toLocaleString()}`
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                position: 'right',
                                ticks: {
                                    callback: (val) => `₪${val.toLocaleString()}`,
                                    font: { family: 'Heebo' }
                                },
                                grid: { color: 'rgba(0,0,0,0.05)' }
                            },
                            x: {
                                ticks: { font: { family: 'Heebo', weight: 'bold', size: 11 } },
                                grid: { display: false }
                            }
                        }
                    }
                });
            }
        }
    } catch (e) {
        // Chart failed to load — not critical
    }

    // Appointment Status Doughnut
    try {
        const aptRes = await fetch('/api/dashboard/appointment-chart');
        const aptData = await aptRes.json();

        if (aptData.success) {
            const ctx = document.getElementById('appointmentChart');
            if (ctx) {
                const d = aptData.data;
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['הושלם', 'מתוזמן', 'בוטל', 'לא הגיע'],
                        datasets: [{
                            data: [d.completed, d.scheduled, d.cancelled, d.no_show],
                            backgroundColor: ['#197fe6', '#078838', '#e73908', '#f59e0b'],
                            borderWidth: 2,
                            borderColor: '#fff',
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '65%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                rtl: true,
                                labels: {
                                    font: { family: 'Heebo', size: 12 },
                                    padding: 16,
                                    usePointStyle: true,
                                    pointStyleWidth: 12,
                                }
                            },
                            tooltip: {
                                rtl: true,
                                textDirection: 'rtl',
                            }
                        }
                    }
                });
            }
        }
    } catch (e) {
        // Chart failed to load — not critical
    }
});
