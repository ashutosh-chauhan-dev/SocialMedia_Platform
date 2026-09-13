function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return decodeURIComponent(parts.pop().split(";").shift());
    }
    return null;
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".like-btn").forEach((btn) => {
        btn.addEventListener("click", async (event) => {
            event.preventDefault();
            if (btn.disabled) return;

            const postId = btn.dataset.postId;
            const csrfToken = getCookie("csrftoken");
            if (!csrfToken) return;

            btn.disabled = true;
            try {
                const response = await fetch(`/post/${encodeURIComponent(postId)}/like/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    credentials: "same-origin",
                });

                if (!response.ok) return;

                const data = await response.json();
                btn.classList.toggle("liked", data.liked);
                const count = btn.querySelector(".like-count");
                if (count) count.textContent = data.likes_count;
            } catch (error) {
                console.error("Unable to update like.", error);
            } finally {
                btn.disabled = false;
            }
        });
    });
});
