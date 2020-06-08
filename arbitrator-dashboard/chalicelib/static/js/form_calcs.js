function rate_change(){
    kraken_zar_update();
    remote_charges_update();
    returns_update();
}

function capital_investment_update(){
    local_charges_update();
    returns_update();
}

function local_charges_change(){
    returns_update();
}


window.onload = function() {
    local_charges_update();
    remote_charges_update();
    returns_update();
    };

function kraken_zar_update()
{
    //Get vals from the form
    var rate = parseFloat(document.getElementById(`rate`).value);
    var krakene = parseFloat(document.getElementById(`krakene`).value);
    document.getElementById(`krakenz`).value = krakene * rate;
};

function local_charges_update()
{
    var cap = parseFloat(document.getElementById(`capital_investment`).value);
    var fee = cap *.0055;
    if (fee < 160.00) {
        fee = 160.00;
    } else if (fee > 675.00) {
        fee = 675.00;
    }
    document.getElementById(`local_charges`).value = fee;
};

function remote_charges_update()
{
    var rate = parseFloat(document.getElementById(`rate`).value);
    rem_charges = 10.00 * rate
    document.getElementById(`remote_charges`).value = rem_charges;
};

function returns_update()
{
    var cap = parseFloat(document.getElementById(`capital_investment`).value);
    var rate = parseFloat(document.getElementById(`rate`).value);
    var kraken = parseFloat(document.getElementById(`krakene`).value);
    var luno = parseFloat(document.getElementById(`luno`).value);
    var local_charges = parseFloat(document.getElementById(`local_charges`).value);
    var swift_fees = parseFloat(document.getElementById(`swift_fees`).value);

    var eur = cap / rate
    console.log(eur)

    var btc = eur/kraken
    console.log(btc)

    var zar = btc * luno

    var ret = zar - cap - local_charges - swift_fees
    var arb_adj = (ret/cap)*100
    
    document.getElementById(`arb_adj`).value = arb_adj.toFixed(2);
    document.getElementById(`remote_btc`).value = btc.toFixed(2);
    document.getElementById(`ret`).value = ret.toFixed(2);
};

