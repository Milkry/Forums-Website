"use strict";

var mutex = null;
var box = null;
var notificationInterval = 3000; // milliseconds
var disabledButtonsColor = disabledButtonsColor;

function load() {
    mutex = false;
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

    let button = document.getElementById("proceedButton");
    let originalButtonColor = button.style.background;
    button.disabled = true;
    button.style.background = disabledButtonsColor;
    let data =
    {
        username: $("#registerUsername").val(),
        password: $("#registerPassword").val()
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
        button.disabled = false;
        button.style.background = originalButtonColor; // Restores the original color
        overlayOff("overlayRegister"); // Close the form
        mutex = false;
    }
    request.send();
}

function login(e) {
    e.preventDefault();

    if (mutex) return;
    mutex = true;

    let button = document.getElementById("proceedButton");
    let originalButtonColor = button.style.background;
    button.disabled = true;
    button.style.background = disabledButtonsColor;
    let data =
    {
        username: $("#loginUsername").val(),
        password: $("#loginPassword").val()
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
        button.disabled = false;
        button.style.background = originalButtonColor; // Restores the original color
        overlayOff("overlayLogin"); // Close the form
        mutex = false;
    }
    request.send();
}

function createTopic(e) {
    e.preventDefault();

    if (mutex) return;
    mutex = true;

    let button = document.getElementById("proceedButton");
    let originalButtonColor = button.style.background;
    button.disabled = true;
    button.style.background = disabledButtonsColor;
    let data =
    {
        topicName: $("#topicName").val(),
    };

    var request = new XMLHttpRequest();
    request.open("POST", "/new/topic/" + data.topicName, true);
    request.onload = () => {
        switch (request.response) {
            case 'TOPIC_CREATED':
                //box = document.getElementById("loginSuccessfulBox").style;
                //box.display = "block";
                location.href = '/';
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
        document.getElementById("createTopic").reset(); // use a jquery instead here
        button.disabled = false;
        button.style.background = originalButtonColor; // Restores the original color
        overlayOff("overlayTopic"); // Close the form
        mutex = false;
    }
    request.send();
}

function createClaim(e, topicId, userId) {
    e.preventDefault();

    if (mutex) return;
    mutex = true;

    let button = document.getElementById("proceedButton");
    let originalButtonColor = button.style.background;
    button.disabled = true;
    button.style.background = disabledButtonsColor;
    let data =
    {
        claimText: $("#claimText").val(),
        topicId: topicId,
        userId: userId
    };

    console.log(data.claimText);

    var request = new XMLHttpRequest();
    request.open("POST", "/" + data.topicId + "/" + data.userId + "/" + data.claimText, true);
    request.onload = () => {
        let result = JSON.parse(request.response);
        button.disabled = false;
        button.style.background = originalButtonColor; // Restores the original color
        mutex = false;
        location.href = '/' + result.topicId + '/' + result.claimId;
    }
    request.send();
}