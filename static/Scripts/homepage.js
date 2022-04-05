"use strict";

var mutex = null;
var notificationInterval = 3000; // milliseconds

function load() {
    mutex = false;
    loadSampleTopics();
    loadSampleTopics();
    loadSampleTopics();
    loadSampleTopics();
    loadSampleTopics();
    loadSampleTopics();
}

function loadSampleTopics() {
    var temp = document.getElementsByTagName("template")[0];
    var clon = temp.content.cloneNode(true);

    document.getElementById("topicsContainer").appendChild(clon);
}

function overlayOn(id) {
    document.getElementById(id).style.display = "block";
}

function overlayOff(id) {
    document.getElementById(id).style.display = "none";
}

function validation() {
    let psw = document.getElementById("registerPassword");
    let confirmpsw = document.getElementById("confirmPassword");
    let statusMsg = document.getElementById("statusMessage");

    if (psw.value !== "" && confirmpsw.value !== "" && psw.value !== confirmpsw.value) {
        statusMsg.style.display = "block";
        return false;
    }
    else {
        statusMsg.style.display = "none";
        return true;
    }
}

function register(e) {
    e.preventDefault(); // Prevents the site from refreshing after form submission

    if (!validation()) return;

    if (mutex) return;
    mutex = true;

    var box;
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
                //box = document.getElementById("accountSuccessBox").style;
                //box.display = "block";
                //setTimeout(() => box.display = "none", notificationInterval);
                location.href = '/';
                break;

            case 'USER_EXISTS':
                box = document.getElementById("accountExistsBox").style;
                box.display = "block";
                setTimeout(() => box.display = "none", notificationInterval);
                break;

            case 'MISSING_DATA':
                box = document.getElementById("missingDataBox").style;
                box.display = "block";
                setTimeout(() => box.display = "none", notificationInterval);
                break;

            default:
                box = document.getElementById("unknownErrorBox").style;
                box.display = "block";
                setTimeout(() => box.display = "none", notificationInterval);
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

    var box;
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
                //box = document.getElementById("loginSuccessfulBox").style;
                //box.display = "block";
                location.href = '/';
                break;

            case 'LOGIN_FAILED_PASSWORD':
                box = document.getElementById("loginFailedPasswordBox").style;
                box.display = "block";
                setTimeout(() => box.display = "none", notificationInterval);
                break;

            case 'LOGIN_FAILED_USERNAME':
                box = document.getElementById("loginFailedUsernameBox").style;
                box.display = "block";
                setTimeout(() => box.display = "none", notificationInterval);
                break;

            case 'MISSING_DATA':
                box = document.getElementById("missingDataBox").style;
                box.display = "block";
                setTimeout(() => box.display = "none", notificationInterval);
                break;

            default:
                box = document.getElementById("unknownErrorBox").style;
                box.display = "block";
                setTimeout(() => box.display = "none", notificationInterval);
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