# Referência visual (não é código do frontend novo)

Este material era o antigo frontend server-rendered (Jinja2), removido do
backend em `feature/split-backend-frontend`. Ele **não roda mais** — o
FastAPI não serve mais `templates/` nem esses assets estáticos.

Está aqui só para servir de referência ao construir o novo frontend em
React/Tailwind:

- `templates/` — telas HTML existentes (login, dashboard, criação e edição
  de campanha, cadastro, recuperação de senha, etc). Útil para ver que
  campos, textos e fluxos cada tela precisa reproduzir.
- `static-assets/css` — estilos usados nessas telas.
- `static-assets/icons` — ícones usados nessas telas.
- `static-assets/folders` — exemplo de crachá/folder gerado pela API
  (não confundir com `media/`, que é onde a API grava esse tipo de arquivo
  em runtime).

Quando a página React equivalente estiver pronta, o arquivo correspondente
aqui pode ser apagado. Quando tudo estiver migrado, esta pasta inteira pode
sair do repositório.
