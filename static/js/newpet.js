function checkInput() {
    var petID = document.getElementById("petID").value;
    var petWeight = document.getElementById("petWeight").value;
    
    if (petID.length > 9 && petWeight > 0) {
        return true;
    } else {
        alert("PetID cannot be less than 10 digits. Pet Weight cannot lower than or equal to 0");
        return false;
    }
}
