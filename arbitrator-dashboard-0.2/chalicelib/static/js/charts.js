$(document).ready(function() {

    $(h_prices_idv).highcharts({
        chart: h_prices_chart,
        title: h_prices_title,
        xAxis: h_prices_xAxis,
        yAxis: h_prices_yAxis,
        series: h_prices_data,
        tooltip: {split: true,
            valueSuffix: ` ZAR`,
        }
    }),

    
    $(h_arb_idv).highcharts({
        chart: h_arb_chart,
        title: h_arb_title,
        xAxis: h_arb_xAxis,
        yAxis: h_arb_yAxis,
        series: h_arb_data,
        tooltip: {split: true,
            valueSuffix: `%`,
        }
    });
});

// document.addEventListener('DOMContentLoaded', function () {
//     var myChart = Highcharts.chart('arb_chart_test', {
//         chart: {
//             type: 'bar'
//         },
//         title: {
//             text: 'Fruit Consumption'
//         },
//         xAxis: {
//             categories: ['Apples', 'Bananas', 'Oranges']
//         },
//         yAxis: {
//             title: {
//                 text: 'Fruit eaten'
//             }
//         },
//         series: [{
//             name: 'Jane',
//             data: [1, 0, 4]
//         }, {
//             name: 'John',
//             data: [5, 7, 3]
//         }]
//     });

//     var arb_chart = Highcharts.chart('arb_chart', {
//         chart: h_arb_chart,
//         title: h_arb_title,
//         xAxis: h_arb_xAxis,
//         yAxis: h_arb_yAxis,
//         series: h_arb_data
//     });
// });

