; (function () {
    const toastOptions = { delay: 2000 }

    function createToast(message) {
        const element = htmx.find("[data-toast-template]").cloneNode(true)

        delete element.dataset.toastTemplate
        element.classList.remove("d-none")

        element.className += " " + message.tags

        htmx.find(element, "[data-toast-body]").innerText = message.message

        htmx.find("[data-toast-container]").appendChild(element)

        const toast = new bootstrap.Toast(element, toastOptions)
        toast.show()
        setTimeout(() => {
            toast.hide()
            setTimeout(() => {
                element.remove()
            }, 500)
        }, 2000)
    }

    htmx.on("messages", (event) => {
        event.detail.value.forEach(createToast)
    })
    htmx.findAll(".toast:not([data-toast-template])").forEach((element) => {
        const toast = new bootstrap.Toast(element, toastOptions)
        toast.show()
    })
})()