#!/usr/bin/env python3
import pyudev
import subprocess
import time
import os
import signal
import sys

# CONFIGURAÇÕES
TARGET_UUID = "01DAA91D85CDBE50"
MOUNT_POINT = "/media/ssd_externo"
FS_TYPE = "ntfs-3g"
MOUNT_OPTIONS = "defaults,nofail,uid=1000,gid=1000"

def get_device_node(uuid):
    """Busca o nó do dispositivo (/dev/sdX1) baseado no UUID."""
    try:
        output = subprocess.check_output(["blkid", "-U", uuid]).decode().strip()
        return output
    except Exception:
        return None

def is_mounted(mount_point):
    """Verifica se o ponto de montagem está ativo."""
    return os.path.ismount(mount_point)

def mount_ssd(device_node):
    """Realiza a montagem do SSD."""
    if not os.path.exists(MOUNT_POINT):
        os.makedirs(MOUNT_POINT, exist_ok=True)
    
    print(f"Tentando montar {device_node} em {MOUNT_POINT}...")
    try:
        # Tenta desmontar primeiro se estiver montado em outro lugar ou estiver com erro
        subprocess.call(["umount", "-l", MOUNT_POINT], stderr=subprocess.DEVNULL)
        
        cmd = ["mount", "-t", FS_TYPE, device_node, MOUNT_POINT, "-o", MOUNT_OPTIONS]
        subprocess.check_call(cmd)
        print("Montagem bem-sucedida!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao montar: {e}")
        return False

def check_and_fix():
    """Verifica o estado atual e corrige se necessário."""
    device_node = get_device_node(TARGET_UUID)
    
    if not device_node:
        # print("SSD não encontrado (UUID não detectado).")
        return

    if not is_mounted(MOUNT_POINT):
        print("SSD detectado mas não montado. Corrigindo...")
        mount_ssd(device_node)
    else:
        # Opcional: Verificar se está no nó correto
        # (Em caso de mudança de sda1 para sdb1 no meio do caminho)
        pass

def monitor():
    """Monitora eventos de udev e também roda um check periódico."""
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block')

    print(f"Iniciando monitoramento para o SSD {TARGET_UUID}...")
    
    # Check inicial
    check_and_fix()

    # Define o monitor para não bloquear para sempre, permitindo o check periódico
    monitor.start()
    
    last_check = time.time()
    
    while True:
        # Espera por evento por no máximo 2 segundos
        device = monitor.poll(timeout=2)
        
        if device:
            action = device.action
            dev_uuid = device.get('ID_FS_UUID')
            
            if dev_uuid == TARGET_UUID:
                print(f"Evento detectado: {action} no SSD.")
                if action in ['add', 'change']:
                    check_and_fix()
                elif action == 'remove':
                    print("SSD removido.")
                    subprocess.call(["umount", "-l", MOUNT_POINT], stderr=subprocess.DEVNULL)

        # Check periódico a cada 30 segundos mesmo sem eventos
        if time.time() - last_check > 30:
            check_and_fix()
            last_check = time.time()

def signal_handler(sig, frame):
    print('Finalizando SSD Guard...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Garantir que roda como root
    if os.geteuid() != 0:
        print("Este script precisa ser executado como ROOT.")
        sys.exit(1)
        
    try:
        monitor()
    except Exception as e:
        print(f"Erro fatal: {e}")
        time.sleep(10)
        sys.exit(1)
