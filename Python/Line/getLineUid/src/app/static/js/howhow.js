let domain = $('#my-domain').data().name;
let settingModal = new bootstrap.Modal(document.getElementById('settingModal'));
let detailModal = new bootstrap.Modal(document.getElementById('detailModal'));
function settingModalToggle() {
    getInfo();
    settingModal.toggle();
}
function detailModalToggle() {
    getInfo();
    detailModal.toggle();
}
$("#howhow").submit(function (e) {
    e.preventDefault();
    postInfo();
});
$("#validationCustom01").change(function () {
    $(this).removeClass("is-invalid");
});
$("#validationCustom02").change(function () {
    $(this).removeClass("is-invalid");
});
$("#validationCustom03").change(function () {
    $(this).removeClass("is-invalid");
});
let info_url = `//${domain}/info`;
getInfo = () => {
    axios
        .get(info_url)
        .then(res => {
            if ($.isEmptyObject(res.data)) {
                $("#detailTable").hide();
                $("#detailDiv").removeClass("alert-danger");
                $("#detailDiv").addClass("alert-success");
                $("#detailNavLinkNumber").text('');
                $("#detailDiv").text("Free Resource Can Use ..");
            } else {
                $("#detailDiv").removeClass("alert-success");
                $("#detailDiv").addClass("alert-danger")
                $("#detailDiv").text("Be Occupied With， Please Wait ..");
                $("#detailNavLinkNumber").text('1');
                let name = res.data.Info.output.name;
                let startTime = res.data.Info.output.datatime;
                let endTime = res.data.Info.output.endtime;
                $("#detailTable").show();
                const $tbody = $('#detailBody');
                const tr1 = `<tr>
                <td class="text-center"> ${name} </td>
                <td class="text-center"> ${startTime} </td>
                <td class="text-center">
                    ${endTime}
                </td>
            </tr>`;
                $tbody.html(tr1);

            }
        }).catch(
            (err) => console.log(err));
}
postInfo = () => {
    getInfo();
    let Token = $("#validationCustom01").val();
    let Secret = $("#validationCustom02").val();
    let name = $("#validationCustom03").val();
    let infos = {
        Token: Token,
        secret: Secret,
        name: name
    };
    $("#validBtn").attr("disabled", true);
    $("#validBtn").text('Validating..');
    axios
        .post(info_url, infos)
        .then(() => {
            console.log("ok...");
            $("#howhow").addClass('was-validated');
            $("#detailNavLinkNumber").text('1');
            $("#validBtn").text('Valid');
            $("#validationCustom01").removeClass("is-invalid");
            $("#detailDiv").text("Be Occupied With， Please Wait ..");
        }).catch(err => {
            $("#validationCustom01").addClass("is-invalid");
            $("#validationCustom02").removeClass("is-invalid");
            $("#validationCustom03").removeClass("is-invalid");
            $("#validBtn").attr("disabled", false);
            $("#validBtn").text('Valid Data');
            if (err.response.data.Info.Message === "Waiting...") {
                $("#validationCustom02").removeClass("is-invalid");
                $("#validationCustom01").removeClass("is-invalid");
                $("#validationCustom03").removeClass("is-invalid");
                settingModal.toggle();
                detailModal.toggle();
            }
            console.log(err.response.data.Info.Message);
        });

}
getInfo();
function onSignIn(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;
    var profile = googleUser.getBasicProfile();
    console.log('ID: ' + profile.getId());
    console.log('Name: ' + profile.getName());
    console.log('Image URL: ' + profile.getImageUrl());
    console.log('Email: ' + profile.getEmail());
    $.ajax({
        type: "POST",
        url: '/google_sign_in',
        data: JSON.stringify({ 'id_token': id_token }),
        success: function () {
            console.log('login success')
        },
        dataType: 'json',
        contentType: "application/json",
    });
}