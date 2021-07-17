function init_processing() {
    $("#modal-close").prop('disabled', true);
    $("#btn-close").prop('disabled', true);
    $("#result-box").hide();
    $('#loader').show();

}

function finish_processing() {
    $('#loader').hide();
    $("#btn-close").prop('disabled', false);
    $("#modal-close").prop('disabled', false);
    $("#result-box").show();
}

$(document).ready(function () {
    // professor submit
    $('#btn-submit').click(function (e) {
        e.preventDefault();

        const code = $("#code").val();
        if (!code) {
            alert("Campo de codigo vazio!");
            return;
        }
        const question_pk = $(this).attr("data-question-pk");

        init_processing();

        const token = Cookies.get('csrftoken');
        const postData = {csrfmiddlewaretoken: token, code: code, question_pk: question_pk};

        $.ajax({
            method: 'POST',
            url: $(this).attr("data-href"),
            data: postData,
            success: function (response) {
                $("#result-box").text(response.result + ": " + response.error_message);
                finish_processing();
            },
            error: function (response) {
                finish_processing();
                alert("Erro ao julgar submissão.");
            },
        });
    });
});