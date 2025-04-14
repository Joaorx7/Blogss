document.addEventListener('DOMContentLoaded', function () {
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

    function adicionarEventosCurtirSeguir(contexto=document) {
        contexto.querySelectorAll('.curtir-btn').forEach(btn => {
            btn.removeEventListener('click', curtirHandler); // evita múltiplos handlers
            btn.addEventListener('click', curtirHandler);
        });

        contexto.querySelectorAll('.seguir-form').forEach(form => {
            form.removeEventListener('submit', seguirHandler);
            form.addEventListener('submit', seguirHandler);
        });
    }

    function curtirHandler(event) {
        const postId = this.dataset.id;
        fetch(`/curtir/${postId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(res => res.json())
        .then(data => {
            const curtidasSpan = document.getElementById(`total-curtidas-${postId}`);
            curtidasSpan.innerText = data.total_curtidas;
            this.innerText = data.curtido ? '💔 Descurtir' : '❤️ Curtir';
        });
    }

    function seguirHandler(e) {
        e.preventDefault();
        const username = this.dataset.username;
        const btn = this.querySelector('.seguir-btn');

        fetch(`/seguir_ou_nao/${username}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(res => res.json())
        .then(data => {
            btn.innerText = data.seguindo ? '✔️ Seguindo' : '➕ Seguir';
        });
    }

    // Aplica os eventos inicialmente
    adicionarEventosCurtirSeguir();

    // Scroll infinito
    let page = 2;
    let carregando = false;
    let temMais = true;

    window.addEventListener('scroll', function () {
        if (carregando || !temMais) return;

        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100) {
            carregando = true;
            document.getElementById('loader').style.display = 'block';

            const url = new URL(window.location.href);
            url.searchParams.set('page', page);

            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById('posts-container');
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.posts_html;
                container.append(...tempDiv.children);

                // Aplica eventos nos novos elementos
                adicionarEventosCurtirSeguir(container);

                page += 1;
                temMais = data.tem_mais;
                carregando = false;
                document.getElementById('loader').style.display = 'none';
            })
            .catch(error => {
                console.error('Erro ao carregar mais posts:', error);
                carregando = false;
                document.getElementById('loader').style.display = 'none';
            });
        }
    });
});

const trilho = document.querySelector('.trilho');
const body = document.body;

trilho.addEventListener('click', () => {
    trilho.classList.toggle('dark');
    body.classList.toggle('dark');

    // Adiciona ou remove a classe "dark" nos componentes que precisam
    document.querySelectorAll('.navbar, .post-resumo, .comentario, aside, a').forEach(el => {
        el.classList.toggle('dark');
    });

    // Salvar a preferência no localStorage
    if (body.classList.contains('dark')) {
        localStorage.setItem('tema', 'dark');
    } else {
        localStorage.setItem('tema', 'light');
    }
});

// Aplica o tema salvo ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    const temaSalvo = localStorage.getItem('tema');
    if (temaSalvo === 'dark') {
        body.classList.add('dark');
        trilho.classList.add('dark');
        document.querySelectorAll('.navbar, .post-resumo, .comentario, aside, a').forEach(el => {
            el.classList.add('dark');
        });
    }
});