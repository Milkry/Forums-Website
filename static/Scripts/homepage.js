"use strict";

var mutex = null;

function load() {
    mutex = false;
}

function overlayOn(id) {
    document.getElementById(id).style.display = "block";
}

function overlayOff(id) {
    document.getElementById(id).style.display = "none";
}

function register(e) {
    e.preventDefault(); // Prevents the site from refreshing after form submission

    if (mutex) return;
    mutex = true;

    let createAccountButton = document.getElementById("createAccountButton");
    let createAccountButtonColor = createAccountButton.style.background;
    createAccountButton.disabled = true;
    createAccountButton.style.background = "gray";
    let data =
    {
        username: document.getElementById("registerUsername").value,
        password: document.getElementById("registerPassword").value
    };

    var request = new XMLHttpRequest();
    request.open("POST", "/register/" + data.username + "/" + data.password, true);
    request.onload = () => {
        switch (request.response) {
            case 'USER_CREATED':
                document.getElementById("accountSuccessBox").style.display = "block";
                // need a timer to remove the green bar later
                break;

            case 'USER_EXISTS':
                document.getElementById("accountExistsBox").style.display = "block";
                break;

            case 'MISSING_DATA':
                document.getElementById("missingDataBox").style.display = "block";
                break;

            default:
                document.getElementById("unknownErrorBox").style.display = "block";
                break;
        }
        document.getElementById("registerForm").reset(); // use a jquery instead here
        createAccountButton.disabled = false;
        createAccountButton.style.background = createAccountButtonColor; // Restores the original color
        overlayOff("overlayRegister"); // Close the form
        mutex = false;
    }
    request.send();
}

function login(e) {
    e.preventDefault();

    if (mutex) return;
    mutex = true;

    let loginButton = document.getElementById("loginButton");
    let loginButtonColor = loginButton.style.background;
    loginButton.disabled = true;
    loginButton.style.background = "gray";
    let data =
    {
        username: document.getElementById("loginUsername").value,
        password: document.getElementById("loginPassword").value
    };

    var request = new XMLHttpRequest();
    request.open("POST", "/login/" + data.username + "/" + data.password, true);
    request.onload = () => {
        switch (request.response) {
            case 'LOGIN_SUCCESSFUL':
                document.getElementById("loginSuccessfulBox").style.display = "block";
                // need a timer to remove the green bar later
                break;

            case 'MISSING_DATA':
                document.getElementById("missingDataBox").style.display = "block";
                break;

            default:
                document.getElementById("unknownErrorBox").style.display = "block";
                break;
        }
        document.getElementById("loginForm").reset(); // use a jquery instead here
        loginButton.disabled = false;
        loginButton.style.background = loginButtonColor; // Restores the original color
        overlayOff("overlayLogin"); // Close the form
        mutex = false;
    }
    request.send();
}