/**
 * Sales Data Analysis System - Chart.js Visualizations
 */

let monthlyChartInstance = null;
let categoryChartInstance = null;
let topProductsChartInstance = null;
let trendChartInstance = null;
let categoryUnitsChartInstance = null;

// Palette for charts
const chartColors = [
    '#2563eb', '#10b981', '#f59e0b', '#7c3aed', '#ec4899',
    '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
];

function formatCurrency(val) {
    return '$' + Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function initAllCharts(data) {
    if (!data) return;

    // 1. Monthly Revenue Chart (Line)
    const ctxMonthly = document.getElementById('monthlyRevenueChart');
    if (ctxMonthly && data.monthly_revenue) {
        if (monthlyChartInstance) monthlyChartInstance.destroy();
        monthlyChartInstance = new Chart(ctxMonthly, {
            type: 'line',
            data: {
                labels: data.monthly_revenue.labels,
                datasets: [{
                    label: 'Monthly Revenue ($)',
                    data: data.monthly_revenue.data,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.12)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointBackgroundColor: '#2563eb',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `Revenue: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (v) => '$' + Number(v).toLocaleString()
                        },
                        grid: { color: '#f1f5f9' }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 2. Category-wise Revenue (Donut)
    const ctxCategory = document.getElementById('categoryRevenueChart');
    if (ctxCategory && data.category_revenue) {
        if (categoryChartInstance) categoryChartInstance.destroy();
        categoryChartInstance = new Chart(ctxCategory, {
            type: 'doughnut',
            data: {
                labels: data.category_revenue.labels,
                datasets: [{
                    data: data.category_revenue.data,
                    backgroundColor: chartColors.slice(0, data.category_revenue.labels.length),
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right' },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                cutout: '65%'
            }
        });
    }

    // 3. Top 5 Products by Sales Units & Revenue (Bar)
    const ctxTopProducts = document.getElementById('topProductsChart');
    if (ctxTopProducts && data.top_products) {
        if (topProductsChartInstance) topProductsChartInstance.destroy();
        topProductsChartInstance = new Chart(ctxTopProducts, {
            type: 'bar',
            data: {
                labels: data.top_products.labels,
                datasets: [
                    {
                        label: 'Units Sold',
                        data: data.top_products.quantities,
                        backgroundColor: '#3b82f6',
                        borderRadius: 6,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Revenue ($)',
                        data: data.top_products.revenues,
                        backgroundColor: '#10b981',
                        borderRadius: 6,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                if (ctx.datasetIndex === 1) {
                                    return `Revenue: ${formatCurrency(ctx.raw)}`;
                                }
                                return `Units: ${Number(ctx.raw).toLocaleString()} pcs`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        title: { display: true, text: 'Units' },
                        grid: { color: '#f1f5f9' }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        beginAtZero: true,
                        title: { display: true, text: 'Revenue ($)' },
                        grid: { drawOnChartArea: false },
                        ticks: {
                            callback: (v) => '$' + Number(v).toLocaleString()
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 4. Sales Trends Over Time (Daily Area Chart)
    const ctxTrend = document.getElementById('salesTrendChart');
    if (ctxTrend && data.sales_trend) {
        if (trendChartInstance) trendChartInstance.destroy();
        trendChartInstance = new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: data.sales_trend.labels,
                datasets: [{
                    label: 'Daily Sales ($)',
                    data: data.sales_trend.data,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.25,
                    borderWidth: 2,
                    pointRadius: 2,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `Sales: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: (v) => '$' + Number(v).toLocaleString()
                        },
                        grid: { color: '#f1f5f9' }
                    },
                    x: {
                        ticks: {
                            maxTicksLimit: 12
                        },
                        grid: { display: false }
                    }
                }
            }
        });
    }

    // 5. Category Units Sold (Bar Chart)
    const ctxCategoryUnits = document.getElementById('categoryUnitsChart');
    if (ctxCategoryUnits && data.category_units) {
        if (categoryUnitsChartInstance) categoryUnitsChartInstance.destroy();
        categoryUnitsChartInstance = new Chart(ctxCategoryUnits, {
            type: 'bar',
            data: {
                labels: data.category_units.labels,
                datasets: [{
                    label: 'Units Sold by Category',
                    data: data.category_units.data,
                    backgroundColor: '#7c3aed',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `Units: ${Number(ctx.raw).toLocaleString()} pcs`
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' }
                    },
                    y: {
                        grid: { display: false }
                    }
                }
            }
        });
    }
}
