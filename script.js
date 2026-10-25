function register() {
    let name = document.getElementById("name").value;
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    if (name == "" || email == "" || password == "") {
        alert("Please fill all fields");
    } else {
        localStorage.setItem("email", email);
        localStorage.setItem("password", password);

        alert("Registration successful!");
        window.location.href = "login.html";
    }
}

function login() {
    let email = document.getElementById("email").value;
    let password = document.getElementById("password").value;

    if (email == localStorage.getItem("email") &&
        password == localStorage.getItem("password")) {

        alert("Login successful!");
        window.location.href = "ty.html";
    } else {
        alert("Invalid email or password");
    }
}

async function register() {

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!name || !email || !password) {
        alert("Please fill all fields");
        return;
    }

    try {

        const response = await fetch("http://localhost:5000/register", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (data.success) {

            alert("Registration successful!");

            window.location.href = "login.html";

        } else {

            alert(data.message);
        }

    } catch (error) {

        console.error(error);
        alert("Unable to connect to server");
    }
}


async function login() {

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please enter email and password");
        return;
    }

    try {

        const response = await fetch("http://localhost:5000/login", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (data.success) {

            alert("Login successful!");

            // Store basic user information
            localStorage.setItem("userId", data.user.id);
            localStorage.setItem("userName", data.user.name);
            localStorage.setItem("userEmail", data.user.email);

            // Redirect
            window.location.href = "ty.html";

        } else {

            alert(data.message);
        }

    } catch (error) {

        console.error("Login error:", error);
        alert("Unable to connect to server");

    }
}
