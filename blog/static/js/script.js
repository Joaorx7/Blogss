document.addEventListener('DOMContentLoaded', function () {
    const botaoCurtir = document.getElementById('curtir-btn');

    if (botaoCurtir) {
        botaoCurtir.addEventListener('click', function () {
            const postId = this.dataset.id;

            fetch(`/curtir/${postId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => response.json())
            .then(data => {
                this.innerText = data.curtido ? '💔 Descurtir' : '❤️ Curtir';
                document.getElementById('total-curtidas').innerText = data.total_curtidas;
            });
        });
    }

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
});