function init_processing() {
    $("#modal-close").prop('disabled', true);
    $('#loader').show();

}

function finish_processing() {
    $('#loader').hide();
    $("#modal-close").prop('disabled', false);
}

$(document).ready(function () {
    $('#questionsModal').on('show.bs.modal', function (event) {
        $("#questions-table tbody").empty();

        init_processing();


        var button = $(event.relatedTarget) // Button that triggered the modal
        var name = button.data('name')
        var student_pk = button.data('student-pk') // Extract info from data-* attributes
        var class_pk = button.data('class-pk')

        var modal = $(this)
        modal.find('#student-name').text(name + " concluiu as seguintes questões:")

        const token = Cookies.get('csrftoken');
        const data = {csrfmiddlewaretoken: token, student_pk: student_pk, class_pk: class_pk};

        $.ajax({
            method: 'POST',
            url: button.data("href"),
            data: data,
            success: function (response) {
                finish_processing();
                $.each(response.questions, function (key, item) {
                    $('<tr>', {html: '<td>' + item.question__name + '</td>'}).appendTo($("#questions-table"));
                });
            },
            error: function (response) {
                finish_processing();
                alert("Erro ao carregar resultados do aluno.");
            },
        });

    })
});