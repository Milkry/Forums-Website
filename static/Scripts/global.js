"use strict";

var mutex = null;
var box = null;
var notificationInterval = 3000; // milliseconds
var disabledButtonsColor = disabledButtonsColor;

function load(register, login, messageBoxes) {
    mutex = false;
    $(function () {
        $("#registerContainer").load(register);
    });
    $(function () {
        $("#loginContainer").load(login);
    });
    $(function () {
        $("#messageBoxContainer").load(messageBoxes);
    });
}

function overlayOn(id) {
    $('#' + id).show();
}

function overlayOff(id) {
    $('#' + id).hide();
}

// Returns true if password to confirmPassword matches, false if not
function validatePassword() {
    let psw = $('#registerPassword').val();
    let confirmpsw = $('#confirmPassword').val();
    let statusMsg = $('#statusMessage_PasswordMismatch');

    if (psw !== "" && confirmpsw !== "" && psw !== confirmpsw) {
        statusMsg.show();
        return false;
    }
    statusMsg.hide();
    return true;
}

// Returns true if username is valid, false if not
function validateUsername() {
    let usernameRestriction = /^[a-zA-Z0-9\_]+$/;
    let username = $('#registerUsername').val();
    let statusMsg = $('#statusMessage_InvalidUsername');

    if (username === "" || usernameRestriction.test(username)) {
        statusMsg.hide();
        return true;
    }
    statusMsg.show();
    return false;
}

function register(e) {
    e.preventDefault(); // Prevents the site from refreshing after form submission

    if (!validatePassword()) return;
    if (!validateUsername()) return;

    if (mutex) return;
    mutex = true;

    let button = document.getElementById("formBtn");
    let originalButtonColor = button.style.background;
    button.disabled = true;
    button.style.background = disabledButtonsColor;
    let data =
    {
        username: $("#registerUsername").val(),
        password: $("#registerPassword").val()
    };

    var request = new XMLHttpRequest();
    request.open("POST", "/register", true);
    request.setRequestHeader("Content-type", "application/json");
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
    request.send(JSON.stringify({ "Username": data.username, "Password": data.password }));
}

function login(e) {
    e.preventDefault();

    if (mutex) return;
    mutex = true;

    let button = document.getElementById("formBtn");
    let originalButtonColor = button.style.background;
    button.disabled = true;
    button.style.background = disabledButtonsColor;
    let data =
    {
        username: $("#loginUsername").val(),
        password: $("#loginPassword").val()
    };

    var request = new XMLHttpRequest();
    request.open("POST", "/login", true);
    request.setRequestHeader("Content-type", "application/json");
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
        document.getElementById("loginForm").reset();
        button.disabled = false;
        button.style.background = originalButtonColor; // Restores the original color
        overlayOff("overlayLogin"); // Close the form
        mutex = false;
    }
    request.send(JSON.stringify({ "Username": data.username, "Password": data.password }));
}

function createTopic(e) {
    e.preventDefault();

    if (mutex) return;
    mutex = true;

    let button = document.getElementById("formBtn");
    let originalButtonColor = button.style.background;
    button.disabled = true;
    button.style.background = disabledButtonsColor;
    let data =
    {
        topicName: $("#topicName").val(),
    };

    var request = new XMLHttpRequest();
    request.open("POST", "/new/topic", true);
    request.setRequestHeader("Content-type", "application/json");
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
    request.send(JSON.stringify(data.topicName));
}

function loadRelatedClaims(claimId, topicId) {
    if (mutex) return;
    mutex = true;

    let button = document.getElementById("relatedClaimsBtn");
    let originalButtonColor = button.style.background;
    button.disabled = true;
    button.style.background = disabledButtonsColor;
    let data =
    {
        claimId: claimId,
    };

    var request = new XMLHttpRequest();
    request.open("GET", "/claims/related/get/" + data.claimId, true);
    request.onload = () => {
        let claims = JSON.parse(request.response).relations;
        if (claims.length == 0) {
            let claim =
                `
                <div style="margin 10px">
                    <p style="word-break: break-all; padding: 20px; font-size: 20px; color: var(--text);">No relations for this claim</p>
                </div>
                `;
            $('#overlayRelatedClaims-opposed').append(claim);
            $('#overlayRelatedClaims-equivalent').append(claim);
        }
        for (const relation of claims) {
            let claim =
                `
                <div onclick="window.open('/${topicId}/${relation.relatedToId}', '_blank')" class="claimContainer" style="margin 10px">
                    <p style="word-break: break-all; padding: 20px; font-size: 20px; color: var(--text);"><i class="fa fa-comment fa-lg claimIcon" aria-hidden="true"></i>${relation.relatedToText}</p>
                </div>
                `;
            if (relation.relationType == "Opposed") {
                $('#overlayRelatedClaims-opposed').append(claim);
            }
            else {
                $('#overlayRelatedClaims-equivalent').append(claim);
            }
        }
        button.disabled = false;
        button.style.background = originalButtonColor; // Restores the original color
        mutex = false;
    }
    request.send();
}

function clearRelations() {
    $('#overlayRelatedClaims-opposed').empty();
    $('#overlayRelatedClaims-equivalent').empty();
}

function search() {
    let data =
    {
        searchQuery: $('#search').val(),
    };

    $('#results').empty();
    $('#results').css('border', 'none');
    $('#results').css('background-color', 'transparent');

    if (data.searchQuery == "") return;

    $('#results').css('border', '1px solid black');
    $('#results').css('background-color', 'var(--background2)');

    var request = new XMLHttpRequest();
    request.open("POST", "/search", true);
    request.setRequestHeader("Content-type", "application/json");
    request.onload = () => {
        let results = JSON.parse(request.response).results;
        if (results.length == 0) {
            let element =
                `
                    <div style="padding: 5px;">
                        <span><i class="fa fa-times fa-lg resultsIcon" aria-hidden="true" style="color: var(--remove);"></i>No Results Found...</span>
                    </div>
                `;
            $('#results').append(element);
        }
        if (results.length > 0) {
            for (const result of results) {
                if (result.type == "TOPIC") {
                    let element =
                        `
                    <div title="View Topic" onclick="location.href='/${result.topicId}'" style="padding: 5px;"
                        class="resultsContainer">
                        <span><i class="fa fa-book fa-lg resultsIcon" aria-hidden="true"></i>${result.topicName}</span>
                    </div>
                    `;
                    $('#results').append(element);
                }
                else if (result.type == "CLAIM") {
                    let element =
                        `
                    <div title="View Claim" onclick="location.href='/${result.topicId}/${result.claimId}'" style="padding: 5px;"
                        class="resultsContainer">
                        <span><i class="fa fa-comment fa-lg resultsIcon" aria-hidden="true"></i>${result.text}</span>
                    </div>
                    `;
                    $('#results').append(element);
                }
            }
        }
    }
    request.send(JSON.stringify(data.searchQuery));
}