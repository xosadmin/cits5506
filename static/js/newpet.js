function checkInput() {
    var petID = document.getElementById("petID").value;
    
    if (petID.length > 9) {
        return true;
    } else {
        alert("PetID cannot be less than 9 digits.");
        return false;
    }
}
