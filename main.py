from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import mysql.connector
import os


####### CÁLCULO CASHBACK
CASH_BASE_P = 0.05
CASH_VIP_P = 0.10

def calc_cashback(valor_compra, desconto=0, vip=False):
    desconto = desconto / 100  # Transformar em float
    valor_compra -= valor_compra * desconto
    cash_base = valor_compra * CASH_BASE_P

    if vip:
        bonus = cash_base * CASH_VIP_P
        cash_total = cash_base + bonus
    else:
        cash_total = cash_base

    if valor_compra > 500.00:
        cash_total *= 2

    return round(cash_total, 2)


####### API - Middleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


####### API - Cashback
@app.get("/cashback")
def get_cashback(request: Request, valor: float, desconto: float = 0, vip:bool = False):
    
    ip = request.client.host

    cashback = calc_cashback(valor, desconto, vip)

    # Tipo de cliente
    if vip:
        tp_cliente = "VIP"
    else: 
        tp_cliente = "NORMAL"

    # Conexão
    conn = get_connection()
    cursor = conn.cursor()

    # Valor real com desconto
    valor_final = valor - (valor * (desconto / 100))

    # Query
    query = """
    INSERT INTO consultas (ip, tp_cliente, valor, cashback)
    VALUES (%s, %s, %s, %s) 
    """

    cursor.execute(query, (ip, tp_cliente, valor_final, cashback))
    conn.commit()

    cursor.close()
    conn.close()

    return {
        "ip": ip,
        "valor_compra": valor,
        "desconto": desconto,
        "vip": vip,
        "cashback": cashback
    }


####### API - Histórico de consultas
@app.get("/historico")
def get_historico(request:Request):
    ip = request.client.host
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT ip, tp_cliente, valor, cashback, dt_insert FROM consultas 
    WHERE ip = %s
    ORDER BY dt_insert desc
    """

    cursor.execute(query, (ip,)) # Precisa ser "(ip,)" para definir como tupla
    resultado_consulta = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "ip": ip,
        "historico": resultado_consulta
    }



####### CONEXÃO BD
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=os.getenv("DB_PORT")
    )


