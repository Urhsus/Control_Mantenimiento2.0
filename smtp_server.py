import asyncio
from aiosmtpd.controller import Controller

class CustomHandler:
    async def handle_DATA(self, server, session, envelope):
        print('\n=== Nuevo mensaje recibido ===')
        print(f'De: {envelope.mail_from}')
        print(f'Para: {envelope.rcpt_tos}')
        print(f'Mensaje:\n{envelope.content.decode("utf8", errors="replace")}')
        print('=' * 50)
        return '250 Message accepted for delivery'

def run_smtp_server():
    handler = CustomHandler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    controller.start()
    print('Servidor SMTP iniciado en localhost:1025')
    print('Presiona Ctrl+C para detener el servidor')
    
    try:
        while True:
            input()
    except KeyboardInterrupt:
        print("\nServidor SMTP detenido.")
        controller.stop()

if __name__ == '__main__':
    run_smtp_server()
