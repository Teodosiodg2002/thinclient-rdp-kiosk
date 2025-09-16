
# Guía de Instalación: ThinClient RDP Kiosk en Ubuntu 24.04

## Objetivo
Preparar una máquina con **Ubuntu Desktop 24.04** para que arranque automáticamente como usuario *kiosko*, muestre una pantalla de login mínima (IP / usuario / contraseña / dominio) y lance **Remmina** en pantalla completa para conectarse por RDP. Al cerrar la sesión RDP, volverá a mostrarse el formulario.

> Esta guía asume un nivel básico de Linux/Ubuntu. Copia y pega los comandos con cuidado y revisa permisos y rutas antes de ejecutar.

---

## Resumen de pasos
1. Instalar Ubuntu Desktop 24.04.
2. Crear usuario `kiosko` y habilitar autologin.
3. Forzar Xorg (desactivar Wayland).
4. Instalar dependencias (python3-gi, remmina, yad, feh, openbox, etc.).
5. Colocar `rdp-login.py` y configurar permisos.
6. Configurar autostart para ejecutar el script al iniciar sesión.
7. Ajustes de escritorio para modo kiosko (ocultar dock, desactivar atajos).
8. Seguridad mínima y pruebas.

---

## 1. Configuración inicial
Actualiza el sistema:
```bash
sudo apt update && sudo apt upgrade -y
```

Crear el usuario kiosko (si no lo creaste durante la instalación):
```bash
sudo adduser kiosko
# asigna contraseña y deja campos en blanco si quieres
sudo usermod -aG sudo kiosko   # opcional: si quieres que tenga sudo
```

Forzar Xorg (recomendado):
```bash
sudo nano /etc/gdm3/custom.conf
```
Descomenta/añade:
```
WaylandEnable=false
AutomaticLoginEnable=true
AutomaticLogin=kiosko
```
Guarda y reinicia:
```bash
sudo reboot
```

---

## 2. Instalar dependencias
```bash
sudo apt update
sudo apt install -y python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gdkpixbuf-2.0 remmina remmina-plugin-rdp remmina-plugin-secret yad feh openbox unclutter x11-xserver-utils xserver-xorg-core xinit
```

---

## 3. Copiar y configurar el script Python
Como usuario con permisos root:
```bash
sudo mkdir -p /home/kiosko/bin
sudo cp /ruta/del/script/rdp-login.py /home/kiosko/bin/rdp-login.py
sudo chown kiosko:kiosko /home/kiosko/bin/rdp-login.py
sudo chmod 700 /home/kiosko/bin/rdp-login.py
```
Verifica que Remmina tiene un directorio para perfiles temporales:
```bash
sudo -u kiosko mkdir -p /home/kiosko/.local/share/remmina
sudo chmod 700 /home/kiosko/.local/share/remmina
```

Prueba manualmente (como kiosko):
```bash
sudo -u kiosko /usr/bin/python3 /home/kiosko/bin/rdp-login.py
```

---

## 4. Autostart para iniciar la aplicación automáticamente
Crea la carpeta autostart y el fichero `.desktop`:
```bash
sudo -u kiosko mkdir -p /home/kiosko/.config/autostart
sudo tee /home/kiosko/.config/autostart/rdp-kiosk.desktop > /dev/null <<'EOF'
[Desktop Entry]
Type=Application
Exec=/usr/bin/python3 /home/kiosko/bin/rdp-login.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=RDP Kiosk
Comment=Arranca el cliente RDP en modo kiosk
EOF
sudo chown kiosko:kiosko /home/kiosko/.config/autostart/rdp-kiosk.desktop
```

---

## 5. Ajustes de escritorio (modo kiosko)
Crea y usa un script para ajustar GNOME al modo kiosko:
```bash
sudo -u kiosko tee /home/kiosko/kiosk-gnome-tweaks.sh > /dev/null <<'EOF'
#!/bin/bash
gsettings set org.gnome.shell.extensions.dash-to-dock autohide true
gsettings set org.gnome.shell.extensions.dash-to-dock dock-fixed false
gsettings set org.gnome.shell.extensions.dash-to-dock intellihide true
gsettings set org.gnome.shell favorite-apps "[]"
gsettings set org.gnome.desktop.notifications show-in-lock-screen false
gsettings set org.gnome.desktop.notifications show-banners false
gsettings set org.gnome.shell.extensions.apps-menu enable-apps-menu false
EOF
sudo chmod +x /home/kiosko/kiosk-gnome-tweaks.sh
sudo chown kiosko:kiosko /home/kiosko/kiosk-gnome-tweaks.sh

# Autostart for tweaks
sudo tee /home/kiosko/.config/autostart/kiosk-gnome-tweaks.desktop > /dev/null <<'EOF'
[Desktop Entry]
Type=Application
Exec=/home/kiosko/kiosk-gnome-tweaks.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Kiosk GNOME Tweaks
Comment=Ajustes automáticos para modo kiosko
EOF
sudo chown kiosko:kiosko /home/kiosko/.config/autostart/kiosk-gnome-tweaks.desktop
```

---

## 6. Seguridad y limpieza
Asegura permisos:
```bash
sudo chown -R kiosko:kiosko /home/kiosko/.local/share/remmina
sudo chmod 700 /home/kiosko/.local/share/remmina
```

Evita dejar contraseñas en ficheros y revisa el script para no guardar datos sensibles permanentemente.

---

## 7. Troubleshooting
- Si Gtk no arranca: asegúrate de que estás en sesión gráfica Xorg.
- Revisa logs del sistema y del usuario en `~/.cache` o `journalctl -b`.
- Ejecuta el script en terminal para ver errores `python3 /home/kiosko/bin/rdp-login.py`.

---

## Checklist final
- [ ] Usuario `kiosko` creado y autologin configurado.
- [ ] Dependencias instaladas.
- [ ] Script copiado a `/home/kiosko/bin/` con permisos correctos.
- [ ] Autostart configurado y probado.
- [ ] Ajustes GNOME aplicados.
- [ ] Prueba de conexión RDP correcta y limpieza de archivos temporales.

---
