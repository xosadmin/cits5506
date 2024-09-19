document.addEventListener("DOMContentLoaded", function() {
    var regNewPetButton = document.getElementById("regNewPet");
    if (regNewPetButton) {
        regNewPetButton.addEventListener("click", function() {
            window.location.href = "/addpet";
        });
    }

    var deleteLinks = document.querySelectorAll(".delete-link");
    deleteLinks.forEach(function(link) {
        link.addEventListener("click", function(event) {
            var confirmation = confirm("Are you sure to de-register this pet? All info related to this pet will be deleted. This is not undoable. Press OK to continue.");
            if (!confirmation) {
                event.preventDefault();
            }
        });
    });
});
