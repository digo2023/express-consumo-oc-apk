# EXPRESS CONSUMO OC — V1.4 Premium

Aplicativo Android para cálculo de consumo semanal e conferência de Ordem de Compra.

## Melhorias da V1.4

- Correção do erro `preadv/pwritev` no Buildozer usando `android.minapi = 28` e `android.ndk_api = 28`.
- Workflow GitHub Actions com limpeza de cache antigo e log completo em caso de falha.
- Visual do app reformulado com aparência mais moderna e profissional.
- Relatórios em PDF com cabeçalho premium, rodapé, tabela profissional e texto padrão `Criado em`.
- Excel de conferência com abas formatadas, cabeçalho, filtro, congelamento de painel e estilo profissional.
- Mantida a correção de segurança para Android: o app copia arquivos `content://` para cache interno antes de processar.

## Arquivos principais

- `main.py`: aplicativo Kivy.
- `buildozer.spec`: configuração Android.
- `.github/workflows/build-apk.yml`: geração do APK no GitHub Actions.
- `assets/icon.png`: ícone.
- `assets/presplash.png`: tela inicial.

## APK

Após subir no GitHub, acesse:

`Actions > Gerar APK Android > Run workflow`

Quando finalizar com sucesso, baixe o APK em `Artifacts`.
