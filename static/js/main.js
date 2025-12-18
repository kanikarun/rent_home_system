const loginForm = document.getElementById("loginForm");
const errorMsg = document.getElementById("errorMsg");

// Success popup dynamically
const successPopup = document.createElement("div");
successPopup.classList.add("success-msg");
successPopup.textContent = "Login Successful!";
successPopup.style.display = "none";
document.querySelector(".login-box").prepend(successPopup);

loginForm.addEventListener("submit", function(e) {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    // CLIENT-SIDE VALIDATION
    if (!username || !password) {
        e.preventDefault();
        errorMsg.textContent = "Username and password are required.";
        errorMsg.style.display = "block";
        successPopup.style.display = "none";
        return;
    }

    if (username.length < 3 || password.length < 3) {
        e.preventDefault();
        errorMsg.textContent = "Username and password must be at least 3 characters.";
        errorMsg.style.display = "block";
        successPopup.style.display = "none";
        return;
    }

    // Hide error for valid input
    errorMsg.style.display = "none";

    // Optional: AJAX login for smooth success popup
    e.preventDefault(); // prevent default submit

    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            successPopup.style.display = "block";
            setTimeout(() => {
                window.location.href = "/dashboard";
            }, 700);
        } else {
            errorMsg.textContent = data.error;
            errorMsg.style.display = "block";
        }
    })
    .catch(err => {
        errorMsg.textContent = "Server error. Please try again.";
        errorMsg.style.display = "block";
    });
});
