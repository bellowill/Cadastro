import paramiko
import os

def deploy():
    hostname = '192.168.3.56'
    username = 'bellowill'
    password = 'meunomeWILL89#'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        print("Instalando dependências (pyudev, ntfs-3g)...")
        _in, _out, _err = client.exec_command(f"echo '{password}' | sudo -S apt-get update && sudo apt-get install -y python3-pyudev ntfs-3g")
        _out.channel.recv_exit_status()

        print("Enviando script ssd_guard.py...")
        local_script = r'C:\Users\William\.gemini\antigravity\scratch\ssd_guard.py'
        remote_script = '/usr/local/bin/ssd_guard.py'
        sftp.put(local_script, '/tmp/ssd_guard.py')
        client.exec_command(f"echo '{password}' | sudo -S mv /tmp/ssd_guard.py {remote_script}")
        client.exec_command(f"echo '{password}' | sudo -S chmod +x {remote_script}")

        print("Enviando serviço ssd_guard.service...")
        local_service = r'C:\Users\William\.gemini\antigravity\scratch\ssd_guard.service'
        remote_service = '/etc/systemd/system/ssd_guard.service'
        sftp.put(local_service, '/tmp/ssd_guard.service')
        client.exec_command(f"echo '{password}' | sudo -S mv /tmp/ssd_guard.service {remote_service}")

        print("Desativando regra antiga colidente (apenas para o SSD)...")
        # Vamos apenas renomear para backup se existir
        client.exec_command(f"echo '{password}' | sudo -S mv /etc/udev/rules.d/99-usb-automount.rules /etc/udev/rules.d/99-usb-automount.rules.bak")

        print("Ativando serviço...")
        client.exec_command(f"echo '{password}' | sudo -S systemctl daemon-reload")
        client.exec_command(f"echo '{password}' | sudo -S systemctl enable ssd_guard.service")
        client.exec_command(f"echo '{password}' | sudo -S systemctl restart ssd_guard.service")
        
        # Check status
        _in, _out, _err = client.exec_command("systemctl is-active ssd_guard.service")
        status = _out.read().decode().strip()
        print(f"Status do Serviço: {status}")
        
        if status == 'active':
            print("Implantação CONCLUÍDA com sucesso!")
        else:
            print("O serviço não iniciou corretamente. Verificando logs...")
            _in, _out, _err = client.exec_command("tail -n 20 /var/log/ssd_guard.log")
            print(_out.read().decode())

        sftp.close()
    except Exception as e:
        print(f"Erro no deploy: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
