import paramiko
import os

def deploy():
    hostname = '192.168.3.56'
    username = 'bellowill'
    password = 'meunomeWILL89#'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Novo conteúdo do docker-compose com 'shared' propagation
    # Isso garante que montagens feitas no host DEPOIS do container iniciar
    # ficam visíveis dentro do container automaticamente — sem precisar reiniciar.
    new_compose = """services:
  db:
    image: mariadb:10.5
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    restart: always
    volumes:
      - ./mariadb:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root_db_pass321
      - MYSQL_PASSWORD=nextcloud_db_pass321
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud

  redis:
    image: redis:alpine
    restart: always
    volumes:
      - ./redis:/data

  app:
    image: nextcloud:stable
    restart: always
    ports:
      - 8080:80
    volumes:
      - ./data:/var/www/html
      - type: bind
        source: /media
        target: /media
        bind:
          propagation: shared
    depends_on:
      - db
      - redis
"""
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # 1. Backup do compose atual
        print("Fazendo backup do docker-compose.yml...")
        _in, _out, _err = client.exec_command(
            f"echo '{password}' | sudo -S cp /home/bellowill/nextcloud/docker-compose.yml "
            f"/home/bellowill/nextcloud/docker-compose.yml.bak"
        )
        _out.channel.recv_exit_status()
        
        # 2. Gravar novo compose
        print("Escrevendo novo docker-compose.yml com propagação 'shared'...")
        with sftp.open('/tmp/docker-compose-new.yml', 'w') as f:
            f.write(new_compose)
        
        _in, _out, _err = client.exec_command(
            f"echo '{password}' | sudo -S mv /tmp/docker-compose-new.yml /home/bellowill/nextcloud/docker-compose.yml"
        )
        _out.channel.recv_exit_status()
        
        # 3. Copiar o ssd_guard.py atualizado
        print("Atualizando ssd_guard.py no Pi...")
        local_script = r'C:\Users\William\.gemini\antigravity\scratch\ssd_guard.py'
        sftp.put(local_script, '/tmp/ssd_guard.py')
        _in, _out, _err = client.exec_command(f"echo '{password}' | sudo -S mv /tmp/ssd_guard.py /usr/local/bin/ssd_guard.py")
        _out.channel.recv_exit_status()
        _in, _out, _err = client.exec_command(f"echo '{password}' | sudo -S chmod +x /usr/local/bin/ssd_guard.py")
        _out.channel.recv_exit_status()
        
        # 4. Garantir que /media seja um mountpoint compartilhado no host
        print("Configurando propagação shared no /media do host...")
        _in, _out, _err = client.exec_command(
            f"echo '{password}' | sudo -S mount --make-shared /media"
        )
        _out.channel.recv_exit_status()

        # 5. Recriar o container com as novas configurações
        print("Recriando container Nextcloud (app apenas)...")
        _in, _out, _err = client.exec_command(
            f"cd /home/bellowill/nextcloud && echo '{password}' | sudo -S docker compose up -d --force-recreate app"
        )
        status = _out.channel.recv_exit_status()
        out_text = _out.read().decode()
        err_text = _err.read().decode()
        print(f"Saída: {out_text}{err_text}")
        
        # 6. Reiniciar o ssd_guard
        print("Reiniciando serviço ssd_guard...")
        _in, _out, _err = client.exec_command(f"echo '{password}' | sudo -S systemctl restart ssd_guard.service")
        _out.channel.recv_exit_status()

        # 7. Verificar resultado final
        print("\n--- Verificação Final ---")
        _in, _out, _err = client.exec_command("docker exec nextcloud-app-1 ls -la /media/ssd_externo 2>&1 || echo 'Aguardando container reiniciar...'")
        _out.channel.recv_exit_status()
        print(f"Conteúdo /media/ssd_externo no container: {_out.read().decode()}")
        
        _in, _out, _err = client.exec_command("systemctl is-active ssd_guard.service")
        print(f"Status ssd_guard: {_out.read().decode().strip()}")
        
        sftp.close()
        print("\nDeploy concluído!")
        
    except Exception as e:
        print(f"Erro no deploy: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
