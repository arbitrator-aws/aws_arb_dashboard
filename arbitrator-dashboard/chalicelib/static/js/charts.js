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

