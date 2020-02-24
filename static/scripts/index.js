$(function () {
  $('.navbar-brand').click(function(){
    document.location.href = 'index.html';
  });
  $('button.submit').click(function () {
    $.ajax(
      {
        url: `http://0.0.0.0:5000/api/v1/${$('#hb_proj').val()}`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
          hbtn_email: $('#hb_id').val(),
          hbtn_password: $('#hb_pwd').val(),
          hbtn_api_key: $('#api_id').val(),
          github_password: $('#g_pwd').val()
        }),
        success: function (response) {
          window.location.href = "done.html" + response.body;
        },
        error: function (error) {
          window.location.href = "404.html";
        }
      }
    );
  });
});
