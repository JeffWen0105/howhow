$(`#logout`).hide();
$(document).ready(() => {
    if ($("#my-status").data().name != 200){
        $("#loginFailed").toast('show');
    }
});