"use strict";

var mutex = null;

function load() {
    mutex = false;
}

function OverlayOn(id) {
    document.getElementById(id).style.display = "block";
}

function OverlayOff(id) {
    document.getElementById(id).style.display = "none";
}

function createAccount() {
    if (mutex) return;
    mutex = true;
    let data =
    {
        username: document.getElementById('registerUsername').value,
        password: document.getElementById('registerPassword').value
    };
    var request = new XMLHttpRequest();
    request.open("POST", "/register/account/" + data.username + "/" + data.password, true);
    request.onload = () => {
        let response = JSON.parse(request.responseText)
        if (response.SUCCESS === 'USER_CREATED') {
            document.getElementById("accountSuccessBox").style.display = "block";
            // need a timer to remove the green bar later
        }
        mutex = false;
    }
    request.send();
}