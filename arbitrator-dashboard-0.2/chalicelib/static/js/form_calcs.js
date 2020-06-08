// Declare thee formatter funcitons first
var euro_formatter = new Intl.NumberFormat('en-ZA', {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 2
})
var rand_formatter = new Intl.NumberFormat('en-ZA', {
    style: 'currency',
    currency: 'ZAR',
    minimumFractionDigits: 2
})
var btc_formatter = new Intl.NumberFormat('en-ZA', {
    style: 'currency',
    currency: 'BTC',
    minimumFractionDigits: 2
})

// populate initial fields
document.getElementById("ov_luno_zar").innerHTML = rand_formatter.format(luno)
document.getElementById("ov_kraken_zar").innerHTML = rand_formatter.format(krakene*window.rate_padded)
document.getElementById("ov_rate_padded").innerHTML = rand_formatter.format(window.rate_padded)

document.getElementById("rate_padding").value = rate_padding
document.getElementById("rate_api").innerHTML = rand_formatter.format(rate_api)
document.getElementById("krakene").innerHTML = euro_formatter.format(krakene)
document.getElementById("krakenz").innerHTML = rand_formatter.format(krakene * window.rate_padded);
document.getElementById("luno").innerHTML = rand_formatter.format(luno);

// initialise calculations
window.onload = function () {
    rate_padder();
    local_charges_update();
    remote_charges_update();
    init_arb = returns_update();
    document.getElementById("ov_arb").innerHTML = init_arb.toFixed(2) + "%";
};

function rate_padding_change() {
    window.rate_padding = parseFloat(document.getElementById(`rate_padding`).value)
    rate_padder();
    kraken_zar_update();
    remote_charges_update();
    returns_update();
}

function rate_change() {
    kraken_zar_update();
    remote_charges_update();
    returns_update();
}

function capital_investment_change() {
    local_charges_update();
    returns_update();
}

function local_charges_change() {
    returns_update();
}

function rate_padder() {
    window.rate_padded = rate_api + window.rate_padding
    document.getElementById(`padded_rate`).innerHTML = rand_formatter.format(window.rate_padded);
};

function kraken_zar_update() {
    window.krakenz = krakene * window.rate_padded
    document.getElementById(`krakenz`).innerHTML = rand_formatter.format(krakene * window.rate_padded);
};

function local_charges_update() {
    var cap = parseFloat(document.getElementById(`capital_investment`).value);
    var fee = cap * .0055;
    if (fee < 160.00) {
        fee = 160.00;
    } else if (fee > 675.00) {
        fee = 675.00;
    }
    document.getElementById(`local_charges`).value = fee.toFixed(2);
};

function remote_charges_update() {
    rem_charges = 10.00 * window.rate_padded
    document.getElementById(`remote_charges`).value = rem_charges.toFixed(2);
};

function returns_update() {
    var cap = parseFloat(document.getElementById(`capital_investment`).value);
    var local_charges = parseFloat(document.getElementById(`local_charges`).value);
    var remote_charges = parseFloat(document.getElementById(`remote_charges`).value);
    var swift_fees = parseFloat(document.getElementById(`swift_fees`).value);
    var kraken_trade_fees = parseFloat(document.getElementById(`kraken_trade_fees`).value);
    var luno_trade_fees = parseFloat(document.getElementById(`luno_trade_fees`).value);
    var luno_withdraw_fee = parseFloat(document.getElementById(`luno_withdraw_fees`).value);

    // Capital investement * exchange rate padded
    var eur = cap / window.rate_padded
    // Kraken's trade fees (0.26%)
    var krak_fees = eur * (kraken_trade_fees / 100)
    var eur_less_kraken_fees = eur - krak_fees
    // buy BTC for remainder
    var btc = eur_less_kraken_fees / krakene

    // BTC arrives in Luno wallet
    // they charge 1% to sell for ZAR
    var luno_trading_fees = btc * (luno_trade_fees / 100)
    var btc_less_luno_fees = btc - luno_trading_fees
    // sell the remaining BTC for ZAR @ Luno price
    var zar = btc_less_luno_fees * luno
    // moving from Luno to bank incurs an R8.50 fee
    var zar_less_withdraw_fee = zar - luno_withdraw_fee
    // finally account for initial bank charges
    var ret = zar_less_withdraw_fee - cap - local_charges - swift_fees - remote_charges
    var arb_adj = (ret / cap) * 100

    document.getElementById(`arb_realised`).innerHTML = arb_adj.toFixed(2) + "%";
    document.getElementById(`remote_btc`).innerHTML = btc_formatter.format(btc);
    document.getElementById(`return`).innerHTML = rand_formatter.format(ret);

    return(arb_adj)
};		