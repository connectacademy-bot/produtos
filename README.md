# Auto Post Bot para Telegram com Google Drive
Este bot faz postagens automáticas no seu canal do Telegram, puxando imagens organizadas em pastas no Google Drive.

## Como funciona:
- Cada pasta no Google Drive representa um produto.
- O nome da pasta segue o padrão: Nome do Produto ¥Valor
- As imagens são postadas em carrossel com legenda automática.
- Após postagem, a pasta é movida para a pasta 'POSTADO' no Drive.

## Configuração:
- Adicione as credenciais da Google (JSON) na raiz do projeto como `credentials.json`.
- Configure variáveis no Railway:
  - TOKEN
  - CANAL_ID
  - YUAN_PARA_REAL
  - YUAN_PARA_EURO
  - DRIVE_FOLDER_ID