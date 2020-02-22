$(document).ready(function () {
    $('.navbar-brand').click(function(){
        document.location.href = 'index.html'
        });

    $('button.btn_submit').click(function () {
        $.ajax(
            {
                url: `http://0.0.0.0:5000/api/v1/${ $('#hbnb_pro_in').val() }`,
                type: 'POST',
                dataType: 'json',
                contentType: 'application/json',
                data: JSON.stringify({
                    holberton_user: $('hbnb_id_in').val(),
                    holberton_pass: $('hbnb_pwd_in').val(),
                    holberton_api_key: $('hbnb_api_in').val(),
                    github_pass: $('git_pwd_in').val(),
                }),
                success: function (response) {
                    window.location.href = "/done/" + response.body;
                },
                error: function (error) {
                    window.location.href = "/404/";
                }
            });
        });
});
