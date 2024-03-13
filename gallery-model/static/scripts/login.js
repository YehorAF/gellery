window.addEventListener("DOMContentLoaded", () => {
    const signinBtn = document.querySelector("#signin-toggle")
    const loginBtn = document.querySelector("#login-toggle")

    const signinForm = document.querySelector("#signin-form")
    const authForm = document.querySelector("#auth-form")

    signinBtn.addEventListener("click", () => {
        loginBtn.classList.remove("active")
        signinBtn.classList.add("active")

        authForm.setAttribute("hidden", "hidden")
        signinForm.removeAttribute("hidden")
    })

    loginBtn.addEventListener("click", () => {
        signinBtn.classList.remove("active")
        loginBtn.classList.add("active")

        signinForm.setAttribute("hidden", "hidden")
        authForm.removeAttribute("hidden")
    })
})