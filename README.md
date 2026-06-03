# EXPRESS CONSUMO OC — APK Android

Aplicativo Android em Kivy para:

- Selecionar PDF Analítico
- Selecionar PDF de Ordem de Compra
- Gerar consumo semanal
- Conferir Consumo Necessário x Ordem de Compra
- Gerar PDF de faltantes, PDF de sobras e Excel de conferência

## Correção principal desta versão

Esta versão corrige o erro:

```text
Invalid URI: content://com.android.externalstorage.documents/tree/...
```

O app não tenta mais salvar relatório diretamente em URI `content://tree`. Agora ele:

1. Copia PDFs escolhidos via Android para o cache interno do aplicativo.
2. Gera relatórios em pasta interna segura do app.
3. Evita usar `content://` como caminho de arquivo comum.
4. Mostra mensagens de erro mais claras.

## Pasta de saída

No Android, os relatórios são salvos automaticamente na pasta interna do aplicativo:

```text
/data/user/0/org.maicon.expressconsumooc/files/relatorios
```

A tela mostra o caminho gerado. Para compartilhar/exportar, pode ser adicionada futuramente uma função com Android Share Sheet.

## Como gerar o APK pelo GitHub Actions

1. Crie um repositório no GitHub.
2. Envie todos os arquivos deste projeto.
3. Abra a aba **Actions**.
4. Execute o workflow **Build APK Android**.
5. Baixe o APK em **Artifacts**.

## Comandos pelo Termux

```bash
pkg update -y
pkg install git -y

git config --global user.name "Maicon Rodrigo Pimentel"
git config --global user.email "digomaicon2023@gmail.com"

git init
git add .
git commit -m "Versao corrigida Express Consumo OC APK"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```
