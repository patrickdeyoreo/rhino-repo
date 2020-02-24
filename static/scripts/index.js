$(document).ready(function () {
    $('.navbar-brand').click(function(){
        document.location.href = 'index.html'
    });
    $('button.btn.submit').submit(function () {
        $.ajax(
            {
                url: `http://0.0.0.0:5000/api/v1/${$('#hb_proj').val()}`,
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({
                    hbtn_user: $('#hb_id').val(),
                    hbtn_pass: $('#hb_pwd').val(),
                    hbtn_api_key: $('#api_id').val(),
                    github_pass: $('#g_pwd').val()
                }),
                success: function (response) {
                    window.location.href = "/done/" + response.body;
                },
                error: function (error) {
                    window.location.href = "/404/";
                }
            }
        );
    });
});
