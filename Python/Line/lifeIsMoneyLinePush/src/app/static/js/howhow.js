let domain = $('#my-domain').data().name;
let url = `//${domain}/run`;
startRunning = () => {
    $('#run').attr("disabled", true);
    $('#run').text("程式執行中請稍等...");
    axios
        .get(url)
        .then(() => {
            location.reload();
            $('#run').text("run");
            $('#run').attr("disabled", false);
            toastShowLogin(context = "手動執行程序成功，請至Line 上查看~~");
        }).catch(
            () => {
                $('#run').text("Err -> 請先設定Token..");
                $("#run").addClass("btn btn-danger h4");
            }
        );
}
let info_url = `//${domain}/info`;
getInfo = () => {
    axios
        .get(info_url)
        .then(res => {
            let infos = res.data.Info.output;
            $("#exampleInputToken1").val(infos.Token);
            $("#exampleInputUID1").val(infos.Uid);

        }).catch(
            () => {
                $("#exampleInputToken1").attr("placeholder", "請先設定 Line Bot Token");
                $("#exampleInputUID1").attr("placeholder", "請先設定 Line push id");
            }
        );
}
postScheduler = () => {
    let hour = $("#inputHour").val();
    let minute = $("#inputMinute").val();
    if (hour != '' && minute != '') {
        let schedulers = {
            minute: minute,
            hour: hour,
            "trigger": "cron"
        };
        let schedulers_url = `//${domain}/scheduler/jobs/life_money`;
        axios
            .patch(schedulers_url, schedulers)
            .then(() => {
                toastShowLogin(context = "設定自動執行排程成功～～");
            }).catch(err => console.log(err));

    };
}
postInfo = () => {
    let Token = $("#exampleInputToken1").val();
    let Uid = $("#exampleInputUID1").val();
    if (Token != '' && Uid != '') {
        let infos = {
            Token: Token,
            uid: Uid,
        };
        axios
            .post(info_url, infos)
            .then(() => {
                toastShowLogin(context = "設定 Line Bot Token 及 Uid 成功 ~~");
            }).catch(err => console.log(err));
    }
}
let settingModal = new bootstrap.Modal(document.getElementById('settingModal'));
let schedulerModal = new bootstrap.Modal(document.getElementById('schedulerModal'));
function settingModalToggle() {
    settingModal.toggle();
    getInfo();
}
let scheduler_url = `//${domain}/scheduler/jobs/life_money`;
getScheduler = () => {
    axios
        .get(scheduler_url)
        .then(res => {
            let scheduler_infos = res.data;
            const $tbody = $('#schedulerBody');
            const tr1 = `<tr>
                        <td class="text-center"> ${scheduler_infos.hour} </td>
                        <td class="text-center"> ${scheduler_infos.minute} </td>
                        <td class="text-center">
                            ${scheduler_infos.next_run_time}
                        </td>
                    </tr>`;
            $tbody.html(tr1);
        }).catch(
            err => {
                console.log("ERR:", err);
            })
};
function schedulerModalToggle() {
    schedulerModal.toggle();
    getScheduler();
}
function toastShowLogin(context) {
    $("#liveToastV").text(context);
    $("#liveToast").toast('show');
}