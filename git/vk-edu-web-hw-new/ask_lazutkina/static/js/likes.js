function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

$(document).ready(function() {
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
                    btn.toggleClass('btn-success btn-outline-secondary');
                    btn.data('is-correct', data.is_correct);

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

// аватарки
$(document).ready(function() {
    $('#id_avatar').on('change', function() {
        var fileInput = this;
        if (fileInput.files && fileInput.files[0]) {
            var formData = new FormData();
            formData.append('avatar', fileInput.files[0]);

            $('.text-danger.mt-2').remove();

            $.ajax({
                url: '{% url "ajax_update_avatar" %}', 
                type: 'POST',
                data: formData,
                processData: false, 
                contentType: false,
                headers: {
                    'X-CSRFToken': csrftoken
                },
                success: function(data) {
                    if (data.avatar_url) {
                        $('#avatar_preview').attr('src', data.avatar_url + '?t=' + new Date().getTime());
                    } else {
                        $('#avatar_preview').after(
                            <div class="text-danger mt-2">Что-то пошло не так</div>
                        );
                    }
                },
                error: function(xhr) {
                    const errorMessage = xhr.responseJSON?.error || 'Ошибка при загрузке аватара';
                    $('#avatar_preview').after(
                        '<div class="text-danger mt-2">${errorMessage}</div>'
                    );
                }
            });
        }
    });
});