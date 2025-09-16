#!/usr/bin/env python3
import gi
import subprocess
import os
import tempfile
import textwrap
from pathlib import Path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk # Importamos Gdk para el modo quiosco

class RDPLogin(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Conexión RDP")
        self.set_border_width(20)
        self.set_default_size(500, 300)
        self.set_deletable(False) 
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # --- MEJORA 2: Modo Quiosco (Bloqueo de input) ---
        # Obtenemos el "asiento" (conjunto de teclado/ratón) para poder bloquearlo
        display = Gdk.Display.get_default()
        self.seat = display.get_default_seat()
        # ----------------------------------------------------

        grid = Gtk.Grid(column_spacing=10, row_spacing=10, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        self.add(grid)
        self.ip_entry = Gtk.Entry(hexpand=True)
        self.user_entry = Gtk.Entry(hexpand=True)
        self.pass_entry = Gtk.Entry(visibility=False, hexpand=True)
        self.domain_entry = Gtk.Entry(hexpand=True)
        grid.attach(Gtk.Label(label="IP o Host:", xalign=0), 0, 0, 1, 1)
        grid.attach(self.ip_entry, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label="Usuario:", xalign=0), 0, 1, 1, 1)
        grid.attach(self.user_entry, 1, 1, 1, 1)
        grid.attach(Gtk.Label(label="Contraseña:", xalign=0), 0, 2, 1, 1)
        grid.attach(self.pass_entry, 1, 2, 1, 1)
        grid.attach(Gtk.Label(label="Dominio (opcional):", xalign=0), 0, 3, 1, 1)
        grid.attach(self.domain_entry, 1, 3, 1, 1)
        connect_button = Gtk.Button(label="Conectar")
        connect_button.connect("clicked", self.on_connect_clicked)
        grid.attach(connect_button, 1, 4, 1, 1)

    def on_connect_clicked(self, widget):
        ip = self.ip_entry.get_text().strip()
        user = self.user_entry.get_text().strip()
        password = self.pass_entry.get_text().strip()
        domain = self.domain_entry.get_text().strip()

        if not ip or not user or not password:
            self.show_error("Los campos 'IP', 'Usuario' y 'Contraseña' son obligatorios.")
            return

        if domain.lower() == "azuread":
            full_user = f"AzureAD\\{user}"
        elif domain:
            full_user = f"{domain}\\{user}"
        else:
            full_user = user

        remmina_content = textwrap.dedent(f"""
            [remmina]
            password={password}
            gateway_username=
            notes_text=
            vc=
            preferipv6=0
            ssh_tunnel_loopback=0
            serialname=
            sound=off
            printer_overrides=
            name=RDP
            console=0
            colordepth=99
            security=tls
            precommand=
            disable_fastpath=0
            left-handed=0
            postcommand=
            multitransport=0
            group=
            server={ip}
            ssh_tunnel_certfile=
            glyph-cache=0
            ssh_tunnel_enabled=0
            disableclipboard=0
            audio-output=
            parallelpath=
            monitorids=
            cert_ignore=0
            gateway_server=
            serialpermissive=0
            protocol=RDP
            old-license=0
            ssh_tunnel_password=
            resolution_mode=2
            pth=
            loadbalanceinfo=
            disableautoreconnect=0
            clientname=
            clientbuild=
            resolution_width=0
            drive=
            relax-order-checks=0
            username={user}
            base-cred-for-gw=0
            gateway_domain=
            network=none
            rdp2tcp=
            gateway_password=
            serialdriver=
            domain={domain}
            profile-lock=0
            rdp_reconnect_attempts=
            restricted-admin=0
            multimon=1
            exec=
            smartcardname=
            serialpath=
            enable-autostart=0
            usb=
            shareprinter=0
            ssh_tunnel_passphrase=
            shareparallel=0
            disablepasswordstoring=0
            quality=0
            span=0
            parallelname=
            ssh_tunnel_auth=0
            keymap=
            ssh_tunnel_username=
            execpath=
            shareserial=0
            resolution_height=0
            timeout=
            useproxyenv=0
            sharesmartcard=0
            freerdp_log_filters=
            microphone=
            dvc=
            ssh_tunnel_privatekey=
            gwtransp=http
            ssh_tunnel_server=
            ignore-tls-errors=1
            disable-smooth-scrolling=0
            gateway_usage=0
            websockets=0
            freerdp_log_level=INFO
            viewmode=4
            disable-toolbar=1
            fullscreen=1
            disable-grab-keyboard=0        
            """)

        file_path = None # Inicializamos por si falla la creación
        try:
            # Creamos el directorio de perfiles de Remmina si no existe
            temp_dir = Path.home() / ".local" / "share" / "remmina"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Creamos un archivo temporal dentro de ese directorio
            tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.remmina', delete=False, dir=str(temp_dir))
            tmp_file.write(remmina_content)
            tmp_file.close()
            file_path = tmp_file.name

            self.seat.ungrab()
            self.hide() # Ocultamos la ventana de login
            
            # Lanzamos Remmina y ESPERAMOS a que termine
            proc = subprocess.Popen(["remmina", "-c", file_path])
            proc.wait()

        except Exception as e:
            self.show_error(f"Error al generar el archivo o ejecutar Remmina: {e}")
        finally:
            
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            # Borramos la contraseña por seguridad
            self.pass_entry.set_text("")
            
            # Re-mostramos la ventana y volvemos a bloquear el input para la siguiente conexión
            self.show_all()
            self.grab_input()

    def show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self, flags=0, message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK, text="Error de Conexión")
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()

    def grab_input(self):
        # Espera a que la ventana exista para obtener Gdk.Window
        gdk_window = self.get_window()
        if gdk_window:
            self.seat.grab(
                gdk_window,
                Gdk.SeatCapabilities.ALL_POINTING | Gdk.SeatCapabilities.ALL,
                True,
                None,
                None,
                None
            )

if __name__ == "__main__":
    win = RDPLogin()
    win.connect("destroy", Gtk.main_quit)
    win.fullscreen()
    win.show_all()
    win.grab_input()
    Gtk.main()