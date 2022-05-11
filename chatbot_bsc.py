# Bibliotecas utilizadas:
# requests para obter o conteudo da pagina do contrato na bscscan.com
# BeautifulSoup para manipular e obter os dados que obtivemos com o requests
# PancakeSwapAPI utilizada para obter o valor do token e outras informações
# time para criar um loop e manter o programa rodando
# Telepot para fazer toda a manipulação do bot com o telegram
import requests
from bs4 import BeautifulSoup
from pythonpancakes import PancakeSwapAPI
import time
import telepot
from telepot import glance

# contrato do token
contract = '0x........'


def get_from_bscscan():
    """
    Essa função faz webscraping da pagina do token na bscscan usando requests e bs4, retornando algumas informações.

        supply (int) - quantidade de moedas em circulação
        num_holders (int) - quantidade de carteiras detentoras do token

    Não é necessário passar nenhum parâmetro para a função
    """
    r = requests.get("https://bscscan.com/token/" + contract)
    soup = BeautifulSoup(r.content, 'html.parser')

    supply = int(str(soup.find("div", {"class": "col-md-8 font-weight-medium"})).split(">")[2][:-13].replace(',', ''))
    num_holders = int(str(soup.find("div", {"class": "mr-3"})).split(">")[1][1:7].replace(',', ''))
    return supply, num_holders


def get_from_pancakeswap():
    """
    Essa outra função faz o uso de uma API para obter algumas outras informações.
    Link para a homepage da API: https://github.com/scottburlovich/pythonpancakes

        token_price (float) - preço atual do token em usd
        token_price_bnb (float) - preço atual do token em bnb
        num_tokens_per_bnb (float) - apenas para saber quantos tokens uma bnb compra
        name_and_simbol (str) - uma concatenação do nome do token com o simbolo

    Não é necessário passar nenhum parâmetro para a função
    """

    # Instanciando o objeto
    ps = PancakeSwapAPI()

    # Criando o objeto
    # Quando criado, temos um dicionário que contem a timestamp atual e outro dicionário com os demais dados
    token = ps.tokens(contract)

    # Obtendo os dados do dicionário
    token_price = float(token['data']['price'])
    token_price_bnb = float(token['data']['price_BNB'])
    name_and_simbol = token['data']['name'] + ' (' + str(token['data']['symbol']) + ')'
    num_tokens_per_bnb = 1 / float(token['data']['price_BNB'])

    return token_price, token_price_bnb, num_tokens_per_bnb, name_and_simbol

# Token do bot que criou no botfather
token_telegram = "seu token do telegram aqui"
# ID do grupo
chat_id = "seu chat id aqui"


# Essa função recebe o comando e cria a mensagem para ser enviada
def make_message(received_command, username):
    """
    Essa função cria a mensagem a ser enviada de acordo com o comando recebido.

        Basicamente, se for um comando especifico, a mensagem é salva em uma variável
        para que seja passada para uma outra função que ira envia-la.

    Recebe duas strings, sendo elas o comando recebido e o username de quem enviou
    """

    if received_command == "/help":
        mensagem = """*Lista de comandos:*

*/price* - Preço atual
*/contrato* - Consultar o contrato do token
*/como_comprar* - Como realizar a compra pela Poocoin
*/site* - Site do token
*/outra_informacao* - outra_informacao
*/outra_informacao2* - outra_informacao2"""

    elif received_command == "/price":
        supply, num_holders = get_from_bscscan()
        token_price, token_price_bnb, num_tokens_per_bnb, name_and_simbol = get_from_pancakeswap()
        marketcap = supply * token_price

        mensagem = f"""Token: *{name_and_simbol}*
Token Price: *${token_price:.7f}*
Token/BNB: *{"{:0,.0f}".format(num_tokens_per_bnb)}*
Market Cap: *${"{:0,.2f}".format(marketcap)}*
Total Supply: *{"{:0,.0f}".format(supply)}*
Holders: *${"{:0,.0f}".format(num_holders)}*""".format(name_and_simbol, token_price,
                                                        token_price_bnb,num_tokens_per_bnb,
                                                        supply, marketcap, num_holders)

    elif received_command == "/contrato":
        mensagem = "*token_contract*"

    elif received_command == "/como_comprar":
        mensagem = """*informação de como comprar:*"""

    elif received_command == "/site":
        mensagem = """*Website o website:*"""

    elif received_command == "/outra_informacao":
        mensagem = """*outra informação aqui*"""

    elif received_command == "/outra_informacao2":
        mensagem = """*outra informação aqui*"""

    else:
        mensagem = f"Desculpe {username}, ainda não conheço esse comando. :(".format(username)
    send_message(mensagem)


# Criando o bot
bot = telepot.Bot(token_telegram)


# Essa função apenas faz o envio da mensagem
def send_message(mensagem):
    bot.sendMessage(chat_id, mensagem, parse_mode='Markdown')


# A função handle fica "ouvindo" as conversas no grupo, quando um comando é enviado no grupo ele é identificado
def handle(msg):
    user_name = msg["from"]["first_name"]
    content_type, chat_type, chat_id = glance(msg)
    # print(content_type, chat_type, chat_id)

    if content_type == 'text':
        if msg["text"][0] == '/':
            make_message(msg["text"].lower(), user_name)


bot.message_loop(handle)

#print('Listening ...')

# Cria um loop para manter em execução
while 1:
    time.sleep(5)
