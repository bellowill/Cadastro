# App de Gerenciamento de Clientes

Este é um aplicativo web completo para cadastrar, visualizar, editar e deletar clientes, construído com as melhores práticas de desenvolvimento e uma interface de usuário moderna e responsiva.

## ✨ Features Principais

- **📝 Cadastro Completo de Clientes:** Formulário intuitivo para registrar dados pessoais e de endereço dos clientes.
- **🏠 Dashboard Inteligente:** Visualize métricas importantes como total de clientes, novos registros no mês, e distribuição geográfica dos clientes em gráficos interativos.
- **📊 Banco de Dados Interativo:** Uma interface poderosa para visualizar, editar, deletar e buscar clientes com paginação e filtros dinâmicos.
- **🤖 Busca de Endereço por CEP:** Preenchimento automático de endereço ao digitar o CEP, utilizando a API ViaCEP para agilizar o cadastro e reduzir erros.
- **🔒 Validação de Dados:** Validação robusta de dados tanto na criação quanto na edição de clientes, garantindo a integridade e a qualidade das informações.
- **⬇️ Exportação de Dados Avançada:** Exporte a visualização atual da tabela ou o resultado completo de uma busca para um arquivo CSV.
- **✅ Testes Automatizados:** O projeto conta com uma suíte de testes unitários para garantir a confiabilidade das regras de negócio e validações.

## 🚀 Como Instalar e Rodar o Projeto

1.  **Clone o Repositório:**
    ```bash
    git clone https://github.com/felipegatoloko10/streamlit-customer-app.git
    cd streamlit-customer-app
    ```

2.  **Crie e Ative um Ambiente Virtual:**
    É uma boa prática para isolar as dependências do projeto.
    ```bash
    # No Windows
    python -m venv venv
    .\venv\Scripts\activate

    # No macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as Dependências:**
    O projeto utiliza `pip-tools` para gerenciar as dependências. Instale-as com o `requirements.txt` gerado.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Rode o Aplicativo Streamlit:**
    ```bash
    streamlit run app.py
    ```

Seu navegador deve abrir automaticamente com a aplicação rodando!

## 🛠️ Para Desenvolvedores

Se desejar contribuir com o projeto ou modificar as dependências:

1.  Edite o arquivo `requirements.in` para adicionar ou remover pacotes.
2.  Compile o novo `requirements.txt` com o seguinte comando:
    ```bash
    pip-compile requirements.in
    ```
3.  Rode os testes para garantir que nada foi quebrado:
    ```bash
    pytest
    ```

## 💻 Tecnologias Utilizadas

- **Front-end:** [Streamlit](https://streamlit.io/)
- **Banco de Dados:** [SQLite](https://www.sqlite.org/index.html)
- **Validação de Dados:** [Pydantic (via `email-validator`)](https://pydantic-docs.helpmanual.io/) e [validate-docbr](https://github.com/canassa/validate-docbr)
- **Testes:** [Pytest](https://docs.pytest.org/)
- **Análise e Manipulação de Dados:** [Pandas](https://pandas.pydata.org/)
- **Requisições HTTP:** [Requests](https://requests.readthedocs.io/en/latest/)