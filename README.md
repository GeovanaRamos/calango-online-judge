<p align="center">
    <img src="https://raw.githubusercontent.com/GeovanaRamos/calango-online-judge/master/web/static/core/images/calango.png" alt="Parsifal logo" height="128">
</p>

<h3 align="center">Calango Online Judge (COJ)</h3>

<p align="center">
  O COJ é uma plataforma web para correção automática de algoritmos feitos na pseudolinguagem
    <a href="https://github.com/GeovanaRamos/calango">Calango</a>.
  <br>
</p>

## Arquitetura e Tecnologias

Para o funcionamento completo da solução, são necessários os seguintes serviços:

**Serviço** | **Linguagem** | **Framework** | **Repositório**
---|---|---------------|---
Plataforma Web | Python | Django        | Aqui
Microserviço Julgador | Java | Spring        | [GitHub](https://github.com/GeovanaRamos/calango-judge-service)

Outros repositórios importantes para este projeto:

**Serviço** | **Linguagem** | **Framework** | **Repositório**
---|---|---------------|---
Calango IDE | Java | Swing   | [GitHub](https://github.com/GeovanaRamos/calango)
Calango Interpretador | Java | *Puro*        | [GitHub](https://github.com/GeovanaRamos/calango-interpreter)


## Rodando Localmente

Primeiramente, clone este repositório:

```
git clone https://github.com/GeovanaRamos/calango-online-judge.git
```

Crie uma márquina virtual:

```
virtualenv venv -p python3
```

Instale os pacotes necessários:

```
pip install -r web/requirements.txt
```

Para prosseguir, você deve ter disponível localmente o PostgreSQL ou o SQLite dentro da pasta _web_. Por default, o _settings.py_ utiliza
o PostgreSQL em produção (DEBUG=False) e o SQLite em desenvolvimento (DEBUG=True). Se desejar, altere essas configurações
no arquivo _settings.py_. Para desenvolvimento, todas as variáveis já possuem valores defaults, então não é necessário
configurar nenhuma variável se seguir os passos descritos aqui. Para configuração em produção, veja a seção _Deploy_.

Agora execute as migrações do banco de dados:

```
python manage.py migrate
```

Se não desejar popular o banco de dados, siga para o próximo passo.
Caso contrário, execute o comando abaixo para popular o banco com dados
falsos e ter uma visão de como a aplicação se comporta em situações reais.

```
python manage.py seed
```

Por fim, execute a aplicação:

```
python manage.py runserver
```

Acesse _localhost:8000_ e verá a aplicação em execução. Para ter acesso
ao site de administração, acesse _localhost:8000/admin_.

Se você executou o comando _seed_, já existem dois perfis 
de usuário que também são administradores. As credencias são as seguintes:

```
Perfil de Aluno
Usuário: aluno@email.com
Senha: admin
```

```
Perfil de Professor
Usuário: professor@email.com
Senha: admin
```

## Serviços Complementares

Para realizar o julgamento dos códigos, é necessário ter uma 
instância do microserviço em execução. Acesse o 
[repositório](https://github.com/GeovanaRamos/calango-judge-service)
para ter acesso as instruções de execução. Após garantir que o
microserviço está em execução na porta 8080, execute obrigatoriamente 
o qcluster em um outro terminal
para lidar com as submissões assincronamente:
```
python manage.py qcluster
```

Para testar o envio de emails, execute o seguinte comando
em um outro terminal:
```
python -m smtpd -n -c DebuggingServer localhost:1025
```
Esse comando irá executar um servidor SMTP de testes, assim
o COJ conseguirá enviar os emails com sucesso e você poderá
ver o resultado no terminal.

## Deploy

Este repositório possui um workflow de deploy contínuo na branch master.
A cada commit, é gerada uma imagem docker nova para este repositório e 
é feito o pull da imagem no servidor. 

Para colocar a aplicação em produção incialmente, sem o deploy contínuo,
as ações necessárias são:

1. Adicionar o _docker-compose-prod.yml_ no servidor;
2. Adicionar a pasta _nginx_ no servidor;
3. Garantir as credenciais de acesso às imagens docker no servidor;
4. Ter um domínio com certificado SSL da Let's Encrypt já no servidor;
5. Ter um email para o site;
6. Criar um arquivo _.env.prod_ com as seguintes variáveis:

```
POSTGRES_USER=(usuário do banco)
POSTGRES_PASSWORD=(senha do banco)
POSTGRES_DB=(nome do banco)

DEBUG=False
SECRET_KEY=(chave aleatória do Django)
DJANGO_ALLOWED_HOSTS=(domínio ou domínios separado por espaços)
EMAIL_HOST_USER=(email do site)
EMAIL_HOST_PASSWORD=(senha do email do site)
COJ_SERVICE_URL=http://judge:8080/judge

DATABASE=postgres
SQL_HOST=db
SQL_PORT=5432
```
6. Executar os seguintes comandos:
```
docker login docker.pkg.github.com -u $GITHUB_USERNAME -p $GITHUB_TOKEN
docker-compose -f docker-compose-prod.yml pull
docker-compose -f docker-compose-prod.yml up -d
docker-compose -f docker-compose-prod.yml exec -d web python manage.py qcluster
```

<small>Imagem do Calango por <a href="https://www.freepik.com" title="Freepik">Freepik</a> em <a href="https://www.flaticon.com/" title="Flaticon">Flaticon</a></small>