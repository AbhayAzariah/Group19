document.addEventListener("DOMContentLoaded", function () {
    // Profile Toggle and Dropdown Menu
    const profileToggle = document.querySelector("#profileToggle");
    const dropdownMenu = document.querySelector("#profileDropdown");

    if (profileToggle && dropdownMenu) {
        profileToggle.addEventListener("click", function (event) {
            event.preventDefault();
            dropdownMenu.classList.toggle("show");
        });

        document.addEventListener("click", function (event) {
            if (!profileToggle.contains(event.target) && !dropdownMenu.contains(event.target)) {
                dropdownMenu.classList.remove("show");
            }
        });
    }
});