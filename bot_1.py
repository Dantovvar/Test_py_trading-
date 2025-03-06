import ccxt
import pandas as pd
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configura el exchange (por ejemplo, Binance)
exchange = ccxt.binance()

# Define el par de criptomonedas y el intervalo de tiempo
symbol = 'BTC/USDT'
timeframe = '1h'  # Intervalo de tiempo (1 hora en este caso)

def fetch_ohlcv(symbol, timeframe, limit=100):
    # Obtiene datos OHLCV (Open, High, Low, Close, Volume)
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def check_for_cross(df):
    ema7 = calculate_ema(df, 7)
    ema40 = calculate_ema(df, 40)
    df['ema7'] = ema7
    df['ema40'] = ema40

    # Verifica si las EMAs están cerca de cruzarse
    if (df['ema7'].iloc[-1] > df['ema40'].iloc[-1] and df['ema7'].iloc[-2] < df['ema40'].iloc[-2]) or \
       (df['ema7'].iloc[-1] < df['ema40'].iloc[-1] and df['ema7'].iloc[-2] > df['ema40'].iloc[-2]):
        return True
    return False

def send_notification(message):
    # Configura el servidor SMTP para Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "parapruebaspy2024@gmail.com"  # Cambia esto por tu dirección de correo de Gmail
    smtp_password = "Prueba2024"  # Cambia esto por tu contraseña de Gmail

    # Configura el correo electrónico
    from_email = smtp_user
    to_email = "parapruebaspy2024@gmail.com"  # Cambia esto por tu dirección de correo de destino
    subject = "Alerta de cruce de EMAs"
    body = message

    # Crea el mensaje MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Envía el correo electrónico
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Correo enviado a {to_email}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")

def main():
    while True:
        df = fetch_ohlcv(symbol, timeframe)
        if check_for_cross(df):
            send_notification(f"Las EMAs de 7 y 40 periodos están cerca de cruzarse en {symbol}!")
        time.sleep(3600)  # Espera una hora antes de verificar nuevamente (ajusta según el timeframe)

if __name__ == "__main__":
    main()