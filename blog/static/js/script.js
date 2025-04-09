// Referente à página: detalhes_post.html (funcionalidade Curtir/Descurtir)
document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("curtir-btn");
    if (btn) {
        btn.addEventListener("click", function () {
            fetch(`/curtir/${btn.dataset.id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken, // variável csrf deve estar definida no script ou via meta tag
                }
            })
            .then(res => res.json())
            .then(data => {
                btn.textContent = data.curtido ? '💔 Descurtir' : '❤️ Curtir';
                document.getElementById("total-curtidas").textContent = data.total;
            });
        });
    }
});