# App de Gestão de Clientes e Negócios 3D

Uma solução completa para profissionais e pequenas empresas de impressão 3D, este aplicativo web centraliza o gerenciamento de clientes, orçamentos e operações do dia a dia em uma interface moderna e responsiva.

## ✨ Funcionalidades Principais

### Gestão de Clientes (CRM)
- **📝 Cadastro Completo:** Um formulário inteligente para registrar clientes, com preenchimento automático de endereço via busca de CEP.
- **👤 Atalho de Contato:** Preencha o nome do contato principal com apenas um clique, usando o nome do cliente.
- **📊 Banco de Dados Interativo:** Visualize, edite, delete e busque seus clientes com filtros, paginação e links rápidos para **iniciar conversas no WhatsApp** diretamente da tabela.
- **⬇️ Exportação de Dados:** Exporte a visualização atual da tabela ou o resultado completo de uma busca para um arquivo CSV.

### Business Intelligence
- **🏠 Dashboard Dinâmico:** Acompanhe métricas importantes como total de clientes, novos registros por período e a distribuição geográfica dos seus clientes em gráficos interativos.
- **💡 Ações Rápidas:** A partir de uma busca sem resultados, cadastre um novo cliente instantaneamente.

### Ferramentas de Negócio
- **💰 Calculadora de Preços para Impressão 3D:**
    - Crie orçamentos detalhados baseados em múltiplos fatores (mão de obra, material, tempo de impressão, taxas, etc.).
    - Salve e carregue **predefinições** de cálculo para diferentes tipos de projeto, agilizando o processo.
    - Botão para **Limpar** o formulário e começar um novo cálculo rapidamente.
- **💸 Atalho para Emissão de NFS-e:** Um link direto para o portal nacional de emissão de Nota Fiscal de Serviço, facilitando o acesso ao sistema do governo.

### Segurança e Manutenção
- **💾 Backup e Restauração:**
    - Crie e baixe um **backup completo** do seu banco de dados de clientes com um único clique.
    - Restaure seus dados a partir de um arquivo de backup, garantindo total segurança contra perda de dados.
- **✅ Testes Automatizados:** O projeto conta com uma suíte de testes unitários para garantir a confiabilidade das regras de negócio.

## 🚀 Como Instalar e Rodar o Projeto

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/felipegatoloko10/streamlit-customer-app.git
    cd streamlit-customer-app
    ```

2.  **Crie e Ative um Ambiente Virtual:**
    ```bash
    # No Windows
    python -m venv venv
    .\venv\Scripts\activate

    # No macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Rode o Aplicativo Streamlit:**
    ```bash
    streamlit run app.py
    ```
O aplicativo abrirá automaticamente no seu navegador.

## 💻 Tecnologias Utilizadas

- **Front-end:** [Streamlit](https://streamlit.io/)
- **Banco de Dados:** [SQLite](https://www.sqlite.org/index.html)
- **Validação de Dados:** [validate-docbr](https://github.com/canassa/validate-docbr) & [email-validator](https://github.com/JoshData/python-email-validator)
- **Testes:** [Pytest](https://docs.pytest.org/)
- **Análise e Manipulação de Dados:** [Pandas](https://pandas.pydata.org/)
- **Requisições HTTP:** [Requests](https://requests.readthedocs.io/en/latest/)
