# EXPRESS CONSUMO OC — V1.5 Premium FinalFix

Aplicativo Android para cálculo de consumo semanal e conferência de Ordem de Compra.

## Correção principal desta versão

O log enviado mostrou que o Buildozer estava clonando o `python-for-android` da branch `master`. Essa branch passou a usar Python 3.14, enquanto o Kivy 2.3.0 ainda apresentava falha de compilação nativa com `_PyLong_AsByteArray`.

A V1.5 corrige isso com uma pilha estável:

- `p4a.branch = v2024.01.21`
- `kivy==2.2.1`
- `Cython==0.29.36`
- `sh==1.14.3`
- `buildozer==1.5.0`
- limpeza completa de `.buildozer`, `~/.buildozer` e `bin` antes da compilação

## Melhorias mantidas

- Visual moderno e profissional.
- Relatórios PDF com aparência premium.
- Rodapé com `Criado em`.
- Relatórios sem textos do tipo `gerado por`.
- Excel de conferência formatado.
- Tratamento seguro de arquivos `content://` no Android.
- Log completo salvo automaticamente se o GitHub Actions falhar.

## Como criar o APK

Suba o projeto no GitHub e execute:

`Actions > Gerar APK Android > Run workflow`

Quando finalizar com sucesso, baixe em:

`Artifacts > express-consumo-oc-v1-5-premium-finalfix-apk`
