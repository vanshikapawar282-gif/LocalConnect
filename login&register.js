const API_URL = "https://localconnect-u070.onrender.com";

// ================= REGISTER =================
async function register() {
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!name || !email || !password) {
        alert("Please fill all fields");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (data.success) {
            alert("Registration successful!");
            window.location.href = "login.html";
        } else {
            alert(data.message || "Registration failed");
        }

    } catch (error) {
        console.error("Registration error:", error);
        alert("Connection error: " + error.message);
    }
}


// ================= LOGIN =================
async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    if (!email || !password) {
        alert("Please enter email and password");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            alert("Server error (" + response.status + "): " +
                  (data.message || "Please check the server logs."));
            return;
        }

        if (data.success) {
            alert("Login successful!");

            localStorage.setItem("userId", data.user.id);
            localStorage.setItem("userName", data.user.name);
            localStorage.setItem("userEmail", data.user.email);

            window.location.href = "ty.html";
        } else {
            alert(data.message || "Login failed");
        }

    } catch (error) {
        console.error("Login error:", error);
        alert("Connection error: " + error.message);
    }
}