
$(document).ready(function() {
    // Получаем токен из <meta name="csrf-token" content="{{ csrf_token }}">
    var csrftoken = $('meta[name="csrf-token"]').attr('content');

    // Обработка клика по кнопке
    $('.mark-correct-btn').click(function() {
        var btn = $(this);
        var answerId = btn.data('answer-id');

        $.ajax({
            url: '/answer/' + answerId + '/mark-correct/',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            success: function(data) {
                if (data.success) {
                    // Переключаем классы кнопки
                    btn.toggleClass('btn-success btn-outline-secondary');
                    btn.data('is-correct', data.is_correct);

                    // Обновляем текст кнопки
                    if (data.is_correct) {
                        btn.html('✓');
                    } else {
                        btn.html('✓');
                    }
                }
            },
            error: function(xhr) {
                console.error('Ошибка:', xhr.responseText);
                alert('Ошибка: ' + (xhr.responseJSON?.error || 'Неизвестная ошибка'));
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', function () {
    const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    document.querySelectorAll('.like-answer-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const answerId = btn.getAttribute('data-answer-id');

            fetch(`/like/answer/${answerId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    btn.querySelector('.likes-count').textContent = data.likes_count;
                    btn.classList.toggle('liked');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Ошибка при отправке лайка');
            });
        });
    });

    document.querySelectorAll('.like-question-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const questionId = btn.getAttribute('data-question-id');

            fetch(`/like/question/${questionId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    btn.querySelector('.likes-count').textContent = data.likes_count;
                    btn.classList.toggle('liked');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Ошибка при отправке лайка');
            });
        });
    });
});

