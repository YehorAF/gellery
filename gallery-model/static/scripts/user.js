window.addEventListener("DOMContentLoaded", () => {
    const followBtn = document.querySelector("#follow")
    const unfollowBtn = document.querySelector("#unfollow")
    const followers = document.querySelector("#followers")

    followBtn.addEventListener("click", () => {
        fetch(
            followBtn.value,
            {
                method: "POST",
                headers: {"X-CSRFToken": csrftoken},
                mode: "same-origin"
            }
        ).then(response => {
            response.json().then(data => {
                followers.textContent = data["followers"]
            })
        })
        followBtn.setAttribute("hidden", "hidden")
        unfollowBtn.removeAttribute("hidden")
    })

    unfollowBtn.addEventListener("click", () => {
        fetch(
            unfollowBtn.value,
            {
                method: "DELETE",
                headers: {"X-CSRFToken": csrftoken},
                mode: "same-origin"
            }
        ).then(response => {
            response.json().then(data => {
                followers.textContent = data["followers"]
            })
        })
        unfollowBtn.setAttribute("hidden", "hidden")
        followBtn.removeAttribute("hidden")  
    })
})