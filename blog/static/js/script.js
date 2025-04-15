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

    function adicionarEventosCurtirSeguir(contexto = document) {
        contexto.querySelectorAll('.curtir-btn').forEach(btn => {
            btn.removeEventListener('click', curtirHandler);
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
            if (curtidasSpan) {
                curtidasSpan.innerText = data.total_curtidas;
            }

            const imagemCurtiu = this.querySelector('img');
            if (imagemCurtiu) {
                // Atualiza a imagem para o estado atual, diretamente com o caminho estático
                const imagem = data.curtido ? '/media/Icones/vermelho.png' : '/media/Icones/like.png';
                imagemCurtiu.src = imagem;
                imagemCurtiu.alt = data.curtido ? 'Descurtir' : 'Curtir';
            }
        })
        .catch(error => {
            console.error('Erro ao curtir o post:', error);
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
            btn.innerText = data.seguindo ? '✔️ Seguindo' : 'Seguir +';
        });
    }

    // Aplica os eventos inicialmente
    adicionarEventosCurtirSeguir();
});

    // (Resto do código, como scroll infinito e tema, permanece inalterado)

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

                const novosPosts = tempDiv.children;
                const existingPosts = container.querySelectorAll('.post-resumo');
                const existingPostIds = Array.from(existingPosts).map(post => post.dataset.id);

                Array.from(novosPosts).forEach(post => {
                    const postId = post.dataset.id;
                    if (!existingPostIds.includes(postId)) {
                        container.appendChild(post);
                    }
                });

                // Se tiver função para curtir e seguir, chama aqui
                if (typeof adicionarEventosCurtirSeguir === "function") {
                    adicionarEventosCurtirSeguir(container);
                }

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

    // Tema escuro/claro
    const trilho = document.querySelector('.trilho');
    const body = document.body;

    trilho?.addEventListener('click', () => {
        trilho.classList.toggle('dark');
        body.classList.toggle('dark');

        document.querySelectorAll('.navbar, .post-resumo, .comentario, aside, a').forEach(el => {
            el.classList.toggle('dark');
        });

        localStorage.setItem('tema', body.classList.contains('dark') ? 'dark' : 'light');
    });

    const temaSalvo = localStorage.getItem('tema');
    if (temaSalvo === 'dark') {
        body.classList.add('dark');
        trilho?.classList.add('dark');
        document.querySelectorAll('.navbar, .post-resumo, .comentario, aside, a').forEach(el => {
            el.classList.add('dark');
        });
    }

    // Preview de imagem
    const inputImagem = document.getElementById('{{ form.imagem.id_for_label }}');
    const preview = document.getElementById('preview-image');

    if (inputImagem && preview) {
        inputImagem.addEventListener('change', function (event) {
            const file = event.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            } else {
                preview.src = '#';
                preview.style.display = 'none';
            }
        });
    }

