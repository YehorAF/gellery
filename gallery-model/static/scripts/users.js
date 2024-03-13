window.addEventListener("DOMContentLoaded", () => {
    const followBtns = document.querySelectorAll(".follow-btn")

    followBtns.forEach(element => {
        element.addEventListener("click", () => {
            const btnId = element.id
            const [action, username] = btnId.split("-")
            let method = ""
            let btnAct = ""

            if (action == "follow") {
                method = "POST"
                btnAct = "unfollow"
            } else if (action == "unfollow") {
                method = "DELETE"
                btnAct = "follow"
            } else {
                console.error("Not such action")
                return
            }

            console.log(btnAct, method)

            fetch(
                element.value,
                {
                    method: method,
                    headers: {"X-CSRFToken": csrftoken},
                    mode: "same-origin"
                }
            ).then(response => {
                if (response.ok) {
                    const username = element.id.split("-")[1]
                    const btn = document.querySelector(`#${btnAct}-${username}`)
    
                    element.setAttribute("hidden", "hidden")
                    btn.removeAttribute("hidden")
                }
            })
        })
    })
})