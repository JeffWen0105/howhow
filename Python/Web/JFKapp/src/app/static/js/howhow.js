let domain = $('#my-domain').data().name;
const url = `http://${domain}/info/`

function renderProducts(products) {
    let pid = 1;
    $("#productRow").text("");
    products.forEach(function (product) {
        // 建立一個產品卡片的HTML範本
        const card = createProductCardElement(product, pid);
        // 把一張卡片加到row裡面
        $("#productRow").append(card);
        pid += 1;
    });
}

// 設計建立單一卡片HTML標籤的函數
function createProductCardElement(product, pid) {
    const cardElement = `
        <div class="col-md-4">
            <div class="card">
                <img src="${product.img}" class="card-img-top">
                <form data-product-id="${pid}" data-product-uid="${product.hashId}" class="card-body">
                    <h6 class="card-title mb-0">${product.title}</h6>
                    <!-- <p class="card-text">hash: ${product.hashId}</p> -->
                    <div class="form-group">
                        <!--  <label>標籤</label>
                        <input id="Input${pid}"  required class="form-control" type="text" min="1" max="20"> -->
                    </div>
                    <div class="form-group">
                        <button class="btn btn-danger" type="submit">點我看妹 ～</button>
                        <!--   <button class="btn btn-danger" name="deleteTag" type="submit" value="delete">移除標籤</button> -->
                    </div>
                </form>
            </div>
        </div>
    `;
    // 回傳cardElement讓使用這個函數的位置可接受這筆資料
    return cardElement;
}
let pages = 0;
$(document).ready(() => {
    getProducts = products => {
        axios
            .get(url + pages)
            .then(res => {
                products = res.data.Info.output;
                allProducts = products;
                $(`#idsList`).text(`美女圖列表，每一頁計有： ${allProducts.length} 位`);
                $(`#logout`).show();
                renderProducts(products);
                if (pages - 10 < 0) {
                    $("#subtractME").hide();
                } else {
                    $("#subtractME").show();
                }
                $("#productRow form").submit(function (e) {
                    e.preventDefault();
                    const pid = $(this).attr("data-product-id");
                    const uid = $(this).attr("data-product-uid");
                    showToast(pid, uid);
                });
            }).catch(err => {
                console.log(err)
                $("#productRow").text("");
                $(`#idsList`).text(`美女圖列表`);
                const cardElement = `
                <div class="col-md-12">
                  <img src="static/image/main.png" class="card-img-top">
                </div>
                `;
                $("#productRow").append("<div></div><h1>已經沒有美女圖了，請點擊刷新回首頁~~ 囧rz...</h1>");
                $("#productRow").append(cardElement);
            });
    }
    getProducts();
});

// renderProducts(products);
$("#productRow form").submit(function (e) {
    e.preventDefault();
    const pid = $(this).attr("data-product-id");
    const uid = $(this).attr("data-product-uid");
    showToast(pid, uid);
});
let allProducts;
$('#flexSwitchCheckChecked').click(function () {
    renderProducts(allProducts.reverse());
    $("#productRow form").submit(function (e) {
        e.preventDefault();
        const pid = $(this).attr("data-product-id");
        const uid = $(this).attr("data-product-uid");
        showToast(pid, uid);
    });
});

function showToast(pid, uid) {
    let tag = $(`#Input${pid}`).val();
    $("#liveToast").toast('show');
    postInfo(uid);
}

function postInfo(uid) {
    let infos = {
        hashId: uid,
    };
    $("#validBtn").attr("disabled", true);
    $("#validBtn").text('Validating..');
    axios
        .post(url + '10', infos)
        .then(() => {
            console.log("ok...");
        }).catch(err => {
            console.log(err)
            console.log(err.response.data.Info.Message);
            $("#liveToast").toast('hide');
            $("#liveToastFailed").toast('show');
        });
}

(function () {
    'use strict'
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl)
    })
})()

$('#HowHowBar').scroll(function () {
    $('#FixedDiv').css('top', $(this).scrollTop());
});

function subtract() {
    pages = pages - 26;
    if (pages >= 0) {
        getProducts();
    } else {
        pages = 0;
    }
}

function add() {
    pages = pages + 26;
    getProducts();
}

function reload() {
    pages = 0;
    getProducts();
}
