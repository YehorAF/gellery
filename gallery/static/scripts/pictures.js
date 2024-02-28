window.addEventListener("DOMContentLoaded", () => {
    const reactBtns = document.querySelectorAll(".react")

    reactBtns.forEach(element => {
        element.addEventListener("click", () => {
            fetch(
                element.value,
                {
                    method: "POST",
                    headers: {"X-CSRFToken": csrftoken},
                    mode: "same-origin"
                }
            ).then(response => {
                response.json().then(data => {
                    const reactions = data["reactions"]
                    element.textContent = `👍 ${reactions}`
                })
            })
        })
    });
})