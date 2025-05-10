// app/static/js/dashboard_charts.js
document.addEventListener('DOMContentLoaded', function () {
    const chartFontColor = '#ccd6f6'; // Light Text
    const chartGridColor = 'rgba(136, 146, 176, 0.2)'; // Medium text, low alpha
    const chartAccentColor = '#64ffda'; // Accent
    const chartDangerColor = '#f85149'; // Danger

    // --- Category Chart (Pie) ---
    const categoryCtx = document.getElementById('categoryChart')?.getContext('2d');
    if (categoryCtx && typeof categoryLabels !== 'undefined' && categoryLabels.length > 0) {
        // Function to generate colors - you can customize this
        const generateColors = (numColors) => {
            const colors = [
                '#64ffda', '#ffca28', '#ef5350', '#66bb6a', '#ab47bc',
                '#29b6f6', '#ffa726', '#ec407a', '#9ccc65', '#7e57c2'
            ]; // Add more colors if needed
            let result = [];
            for (let i = 0; i < numColors; i++) {
                result.push(colors[i % colors.length]);
            }
            return result;
        };

        new Chart(categoryCtx, {
            type: 'pie', // Or 'doughnut'
            data: {
                labels: categoryLabels,
                datasets: [{
                    label: 'Fraud Counts',
                    data: categoryData,
                    backgroundColor: generateColors(categoryLabels.length),
                    borderColor: '#0a192f', // Match primary background
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // Allow custom sizing via CSS
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: chartFontColor,
                            font: { size: 12, family: 'Poppins' }
                        }
                    },
                    tooltip: {
                        bodyFont: { family: 'Poppins' },
                        titleFont: { family: 'Poppins' }
                    }
                }
            }
        });
    } else {
        console.log("Category chart canvas or data not found.");
    }


    // --- Hourly Chart (Bar) ---
    const hourlyCtx = document.getElementById('hourlyChart')?.getContext('2d');
    if (hourlyCtx && typeof hourlyLabels !== 'undefined' && hourlyLabels.length > 0) {
        new Chart(hourlyCtx, {
            type: 'bar', // Or 'line'
            data: {
                labels: hourlyLabels, // Should be 00:00 to 23:00
                datasets: [{
                    label: 'Fraudulent Transactions',
                    data: hourlyData, // Counts per hour
                    backgroundColor: 'rgba(248, 81, 73, 0.6)', // Danger color with alpha
                    borderColor: chartDangerColor,
                    borderWidth: 1,
                    borderRadius: 4, // Rounded bars
                    barThickness: 'flex', // Responsive bar thickness
                    maxBarThickness: 30 // Max width per bar
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: chartFontColor,
                            font: { family: 'Poppins' },
                            precision: 0 // Show only whole numbers for counts
                        },
                        grid: {
                            color: chartGridColor,
                            zeroLineColor: chartGridColor
                        }
                    },
                    x: {
                        ticks: {
                            color: chartFontColor,
                            font: { family: 'Poppins', size: 10 } // Smaller font for hours
                        },
                        grid: {
                            display: false // Hide vertical grid lines
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false // Hide legend for single dataset bar chart
                    },
                     tooltip: {
                        bodyFont: { family: 'Poppins' },
                        titleFont: { family: 'Poppins' }
                    }
                }
            }
        });
     } else {
        console.log("Hourly chart canvas or data not found.");
     }
});