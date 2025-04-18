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
                const imagem = data.curtido ? '/media/Icones/vermelho.png' : '/media/Icones/like.png';
                imagemCurtiu.src = imagem;
                imagemCurtiu.alt = data.curtido ? 'Descurtir' : 'Curtir';

                if (data.curtido) {
                    // Adiciona a classe de animação se curtiu
                    this.classList.add('pulsar');
                    setTimeout(() => {
                        this.classList.remove('pulsar');
                    }, 300);
                } else {
                    // Adiciona animação de descurtir
                    this.classList.add('descurtir');
                    setTimeout(() => {
                        this.classList.remove('descurtir');
                    }, 300);
                }
            }
        })
        .catch(error => {
            console.error('Erro ao curtir o post:', error);
        });
    }

    function seguirHandler(e) {
        e.preventDefault();
        const username = this.dataset.username;

        fetch(`/seguir_ou_nao/${username}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(res => res.json())
        .then(data => {
            // Atualiza TODOS os botões do mesmo autor
            document.querySelectorAll(`.seguir-btn[data-username="${username}"]`).forEach(btn => {
                btn.innerText = data.seguindo ? 'Seguindo' : 'Seguir +';
            });
        })
        .catch(error => {
            console.error('Erro ao seguir/desseguir:', error);
        });
    }

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
    // Tema escuro/claro
const trilho = document.querySelector('.trilho');
const body = document.body;

trilho?.addEventListener('click', () => {
    // Alterna a classe 'dark' no corpo e no trilho
    trilho.classList.toggle('dark');
    body.classList.toggle('dark');

    // Alterna a classe 'dark' nos outros elementos necessários
    document.querySelectorAll('.navbar, .post-resumo, .comentario, aside, a').forEach(el => {
        el.classList.toggle('dark');
    });

    // Salva o tema escolhido no localStorage
    localStorage.setItem('tema', body.classList.contains('dark') ? 'dark' : 'light');
});

// Recupera o tema salvo no localStorage e aplica
const temaSalvo = localStorage.getItem('tema');
if (temaSalvo === 'dark') {
    body.classList.add('dark');
    trilho?.classList.add('dark');
    document.querySelectorAll('.navbar, .post-resumo, .comentario, aside, a').forEach(el => {
        el.classList.add('dark');
    });
}


    // Preview de imagem
    document.getElementById('id_imagem').addEventListener('change', function(event) {
        const preview = document.getElementById('preview-image');
        const file = event.target.files[0];
        const reader = new FileReader();
    
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
    
        if (file) {
            reader.readAsDataURL(file);
        }
    });

