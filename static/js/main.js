const loginForm = document.getElementById("loginForm");
const errorMsg = document.getElementById("errorMsg");

// Success popup
const successPopup = document.createElement("div");
successPopup.classList.add("success-msg");
successPopup.innerHTML = "Login Successful!";
successPopup.style.display = "none";
document.querySelector(".login-box").prepend(successPopup);

// Hide popup & error when page loads (prevent "stuck" effect)
window.onload = () => {
    loginForm.reset();
    errorMsg.style.display = "none";
    successPopup.style.display = "none";
};
window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
        window.location.reload();
    }
});


if (loginForm) {
    loginForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value.trim();

        if (username === "admin" && password === "123") {
            errorMsg.style.display = "none";
            successPopup.style.display = "block";

            // Redirect fast
            setTimeout(() => {
                window.location.href = "/dashboard";
            }, 700);
        } else {
            errorMsg.textContent = "The username or password you entered is incorrect.";
            errorMsg.style.display = "block";
        }
    });
}




