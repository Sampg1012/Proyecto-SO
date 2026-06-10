import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

# ─── Configuración de tema ───────────────────────────────────────────────────
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# ─── Algoritmos de Reemplazo de Páginas ──────────────────────────────────────

def fifo(referencias, num_marcos):
    marcos = []
    fallos = 0
    historial = []
    cola = []

    for pagina in referencias:
        fallo = False
        reemplazada = None

        if pagina not in marcos:
            fallos += 1
            fallo = True
            if len(marcos) < num_marcos:
                marcos.append(pagina)
                cola.append(pagina)
            else:
                reemplazada = cola.pop(0)
                marcos[marcos.index(reemplazada)] = pagina
                cola.append(pagina)

        historial.append({
            "pagina": pagina,
            "marcos": list(marcos),
            "fallo": fallo,
            "reemplazada": reemplazada
        })

    return historial, fallos


def optimo(referencias, num_marcos):
    marcos = []
    fallos = 0
    historial = []

    for i, pagina in enumerate(referencias):
        fallo = False
        reemplazada = None

        if pagina not in marcos:
            fallos += 1
            fallo = True
            if len(marcos) < num_marcos:
                marcos.append(pagina)
            else:
                # Buscar cuál página se usará más tarde (o nunca)
                futuros = {}
                for m in marcos:
                    try:
                        futuros[m] = referencias[i + 1:].index(m)
                    except ValueError:
                        futuros[m] = float("inf")  # No se usará → candidata ideal

                victima = max(futuros, key=lambda x: futuros[x])
                reemplazada = victima
                marcos[marcos.index(victima)] = pagina

        historial.append({
            "pagina": pagina,
            "marcos": list(marcos),
            "fallo": fallo,
            "reemplazada": reemplazada
        })

    return historial, fallos


def lru(referencias, num_marcos):
    marcos = []
    fallos = 0
    historial = []
    reciente = []  # orden de uso: índice 0 = menos reciente

    for pagina in referencias:
        fallo = False
        reemplazada = None

        if pagina in marcos:
            # Actualizar orden de uso
            reciente.remove(pagina)
            reciente.append(pagina)
        else:
            fallos += 1
            fallo = True
            if len(marcos) < num_marcos:
                marcos.append(pagina)
                reciente.append(pagina)
            else:
                victima = reciente.pop(0)  # menos recientemente usado
                reemplazada = victima
                marcos[marcos.index(victima)] = pagina
                reciente.append(pagina)

        historial.append({
            "pagina": pagina,
            "marcos": list(marcos),
            "fallo": fallo,
            "reemplazada": reemplazada
        })

    return historial, fallos


# ─── Interfaz Gráfica ─────────────────────────────────────────────────────────

class SimuladorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Algoritmos de Reemplazo de Páginas")
        self.geometry("1100x750")
        self.resizable(True, True)
        self.minsize(900, 650)

        self._build_ui()

    # ── Construcción de la UI ─────────────────────────────────────────────────

    def _build_ui(self):
        # Título
        titulo = ctk.CTkLabel(
            self,
            text="Simulador de Algoritmos de Reemplazo de Páginas",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        titulo.pack(pady=(20, 5))

        subtitulo = ctk.CTkLabel(
            self,
            text="FIFO  ·  Óptimo  ·  LRU",
            font=ctk.CTkFont(size=13),
            text_color="#3B91ED",
        )
        subtitulo.pack(pady=(0, 15))

        # ── Panel de configuración
        config_frame = ctk.CTkFrame(self, corner_radius=12)
        config_frame.pack(fill="x", padx=30, pady=(0, 15))

        # Fila 1: entradas
        row1 = ctk.CTkFrame(config_frame, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=(15, 5))

        # Referencias
        ctk.CTkLabel(row1, text="Cadena de referencias\n(números separados por espacios o comas):",
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.entry_refs = ctk.CTkEntry(row1, width=420, placeholder_text="Ej: 1 2 3 4 1 2 5 1 2 3 4 5")
        self.entry_refs.grid(row=0, column=1, padx=(0, 20))

        # Marcos
        ctk.CTkLabel(row1, text="Número de marcos:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=2, sticky="w", padx=(0, 10))
        self.entry_marcos = ctk.CTkEntry(row1, width=70, placeholder_text="3")
        self.entry_marcos.grid(row=0, column=3, padx=(0, 20))

        # Fila 2: algoritmo y botón
        row2 = ctk.CTkFrame(config_frame, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(row2, text="Algoritmo:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, sticky="w", padx=(0, 10))

        self.algoritmo_var = ctk.StringVar(value="Todos")
        self.combo_algo = ctk.CTkOptionMenu(
            row2,
            values=["Todos", "FIFO", "Óptimo", "LRU"],
            variable=self.algoritmo_var,
            width=150,
        )
        self.combo_algo.grid(row=0, column=1, padx=(0, 20))

        btn_simular = ctk.CTkButton(
            row2,
            text="▶  Simular",
            command=self.simular,
            width=130,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1F6AA5",
            hover_color="#144E7B",
        )
        btn_simular.grid(row=0, column=2, padx=(0, 10))

        btn_limpiar = ctk.CTkButton(
            row2,
            text="✕  Limpiar",
            command=self.limpiar,
            width=110,
            height=36,
            font=ctk.CTkFont(size=13),
            fg_color="#555",
            hover_color="#333",
        )
        btn_limpiar.grid(row=0, column=3)

        # ── Pestañas de resultados
        self.tabview = ctk.CTkTabview(self, corner_radius=12)
        self.tabview.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        for tab in ["FIFO", "Óptimo", "LRU", "Comparación"]:
            self.tabview.add(tab)

        # Construir contenido de cada pestaña
        self.frames_algo = {}
        for tab in ["FIFO", "Óptimo", "LRU"]:
            self.frames_algo[tab] = self._build_result_tab(self.tabview.tab(tab))

        self.frame_comparacion = self._build_comparacion_tab(self.tabview.tab("Comparación"))

    def _build_result_tab(self, parent):
        """Crea el canvas de tabla + resumen para un algoritmo."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        # Resumen (arriba)
        resumen_frame = ctk.CTkFrame(frame, corner_radius=8, height=55)
        resumen_frame.pack(fill="x", padx=10, pady=(10, 5))
        resumen_frame.pack_propagate(False)

        lbl_resumen = ctk.CTkLabel(
            resumen_frame,
            text="Sin resultados aún.",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        lbl_resumen.pack(side="left", padx=15, pady=5)

        # Tabla (canvas con scroll)
        tabla_frame = ctk.CTkFrame(frame, corner_radius=8)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        canvas = tk.Canvas(tabla_frame, bg="#1E1E2E", highlightthickness=0)
        scroll_x = ctk.CTkScrollbar(tabla_frame, orientation="horizontal", command=canvas.xview)
        scroll_y = ctk.CTkScrollbar(tabla_frame, orientation="vertical", command=canvas.yview)

        canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg="#1E1E2E")
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width if inner.winfo_reqwidth() < event.width else inner.winfo_reqwidth())

        inner.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        return {
            "lbl_resumen": lbl_resumen,
            "inner": inner,
            "canvas": canvas,
        }

    def _build_comparacion_tab(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True)

        lbl = ctk.CTkLabel(
            frame,
            text="Simula primero para ver la comparación.",
            font=ctk.CTkFont(size=14),
        )
        lbl.pack(expand=True)
        return {"lbl": lbl, "frame": frame}

    # ── Lógica de simulación ──────────────────────────────────────────────────

    def simular(self):
        # Validar entradas
        raw = self.entry_refs.get().strip()
        if not raw:
            messagebox.showerror("Error", "Ingresa la cadena de referencias.")
            return

        raw = raw.replace(",", " ")
        try:
            referencias = [int(x) for x in raw.split()]
        except ValueError:
            messagebox.showerror("Error", "La cadena de referencias solo debe contener números.")
            return

        try:
            num_marcos = int(self.entry_marcos.get())
            if num_marcos < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El número de marcos debe ser un entero positivo.")
            return

        seleccion = self.algoritmo_var.get()

        resultados = {}
        if seleccion in ("Todos", "FIFO"):
            resultados["FIFO"] = fifo(referencias, num_marcos)
        if seleccion in ("Todos", "Óptimo"):
            resultados["Óptimo"] = optimo(referencias, num_marcos)
        if seleccion in ("Todos", "LRU"):
            resultados["LRU"] = lru(referencias, num_marcos)

        for nombre, (historial, fallos) in resultados.items():
            self._renderizar_tabla(nombre, historial, fallos, num_marcos, len(referencias))

        if len(resultados) > 1:
            self._renderizar_comparacion(resultados, len(referencias))
            self.tabview.set("Comparación")
        else:
            self.tabview.set(list(resultados.keys())[0])

    def _renderizar_tabla(self, nombre, historial, fallos, num_marcos, total_refs):
        widgets = self.frames_algo[nombre]
        inner = widgets["inner"]
        canvas = widgets["canvas"]

        # Limpiar
        for w in inner.winfo_children():
            w.destroy()

        aciertos = total_refs - fallos
        tasa_fallos = fallos / total_refs * 100

        widgets["lbl_resumen"].configure(
            text=f"  Referencias: {total_refs}   |   Fallos de página: {fallos}   "
                 f"|   Aciertos: {aciertos}   |   Tasa de fallos: {tasa_fallos:.1f}%"
        )

        # Colores
        COLOR_HEADER   = "#2B4E7E"
        COLOR_FALLO    = "#7B1E1E"
        COLOR_ACIERTO  = "#1A3A1A"
        COLOR_MARCO    = "#1E3A5F"
        COLOR_TEXT     = "#E0E0E0"
        COLOR_PAGINA   = "#7EB8F7"
        COLOR_REMP     = "#F7A07E"

        CELL_W = 55
        CELL_H = 32
        PAD    = 1

        def cell(parent, text, bg, fg=COLOR_TEXT, bold=False, w=CELL_W, h=CELL_H):
            f = tk.Frame(parent, bg=bg, width=w, height=h)
            f.pack_propagate(False)
            font = ("Consolas", 10, "bold" if bold else "normal")
            tk.Label(f, text=text, bg=bg, fg=fg, font=font).pack(expand=True)
            return f

        # Encabezados
        header_row = tk.Frame(inner, bg="#1E1E2E")
        header_row.pack(side="top", fill="x", pady=(0, PAD))

        cell(header_row, "Ref →", COLOR_HEADER, bold=True, w=70).pack(side="left", padx=PAD)
        for paso in historial:
            cell(header_row, str(paso["pagina"]), COLOR_HEADER, fg=COLOR_PAGINA, bold=True).pack(side="left", padx=PAD)

        # Filas de marcos
        for i in range(num_marcos):
            row = tk.Frame(inner, bg="#1E1E2E")
            row.pack(side="top", fill="x", pady=(0, PAD))
            cell(row, f"Marco {i}", COLOR_MARCO, bold=True, w=70).pack(side="left", padx=PAD)
            for paso in historial:
                valor = paso["marcos"][i] if i < len(paso["marcos"]) else ""
                bg = COLOR_MARCO
                if paso["fallo"] and valor == paso["pagina"]:
                    bg = "#1F5E8A"
                cell(row, str(valor), bg).pack(side="left", padx=PAD)

        # Fila de estado (F/✓)
        status_row = tk.Frame(inner, bg="#1E1E2E")
        status_row.pack(side="top", fill="x", pady=(PAD * 2, 0))
        cell(status_row, "Estado", COLOR_HEADER, bold=True, w=70).pack(side="left", padx=PAD)
        for paso in historial:
            if paso["fallo"]:
                cell(status_row, "F", COLOR_FALLO, fg="#FF6B6B", bold=True).pack(side="left", padx=PAD)
            else:
                cell(status_row, "✓", COLOR_ACIERTO, fg="#6BFF6B", bold=True).pack(side="left", padx=PAD)

        # Fila de reemplazada
        remp_row = tk.Frame(inner, bg="#1E1E2E")
        remp_row.pack(side="top", fill="x", pady=(PAD, 0))
        cell(remp_row, "Reemplaz.", COLOR_HEADER, bold=True, w=70).pack(side="left", padx=PAD)
        for paso in historial:
            valor = str(paso["reemplazada"]) if paso["reemplazada"] is not None else ""
            fg = COLOR_REMP if valor else COLOR_TEXT
            cell(remp_row, valor, "#1E1E2E", fg=fg, bold=bool(valor)).pack(side="left", padx=PAD)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _renderizar_comparacion(self, resultados, total_refs):
        # Limpiar pestaña
        for w in self.frame_comparacion["frame"].winfo_children():
            w.destroy()

        frame = self.frame_comparacion["frame"]

        ctk.CTkLabel(
            frame,
            text="Comparación de Algoritmos",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(20, 15))

        # Tabla comparativa
        tabla = ctk.CTkFrame(frame, corner_radius=10)
        tabla.pack(padx=40, pady=5)

        headers = ["Algoritmo", "Fallos de página", "Aciertos", "Tasa de fallos", "Tasa de aciertos"]
        col_widths = [160, 160, 120, 160, 160]
        header_colors = ["#1F4E79"] * 5

        for col, (h, w) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(
                tabla, text=h, width=w, height=36,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#1F4E79", corner_radius=0,
                text_color="white",
            ).grid(row=0, column=col, padx=1, pady=1)

        mejor_fallos = min(v[1] for v in resultados.values())

        for row_idx, (nombre, (_, fallos)) in enumerate(resultados.items(), start=1):
            aciertos = total_refs - fallos
            tasa_f = fallos / total_refs * 100
            tasa_a = aciertos / total_refs * 100
            es_mejor = fallos == mejor_fallos

            row_color = "#163040" if row_idx % 2 == 0 else "#1A2535"
            nombre_color = "#FFD700" if es_mejor else "white"
            tag = f" ★" if es_mejor else ""

            valores = [f"{nombre}{tag}", str(fallos), str(aciertos),
                       f"{tasa_f:.1f}%", f"{tasa_a:.1f}%"]

            for col, (val, w) in enumerate(zip(valores, col_widths)):
                tc = nombre_color if col == 0 else ("white")
                ctk.CTkLabel(
                    tabla, text=val, width=w, height=34,
                    font=ctk.CTkFont(size=12, weight="bold" if col == 0 else "normal"),
                    fg_color=row_color, corner_radius=0,
                    text_color=tc,
                ).grid(row=row_idx, column=col, padx=1, pady=1)

        # Leyenda
        ctk.CTkLabel(
            frame,
            text="★  Mejor algoritmo (menos fallos de página)",
            font=ctk.CTkFont(size=11),
            text_color="#FFD700",
        ).pack(pady=(10, 5))

        # Barra visual de fallos
        self._barra_fallos(frame, resultados, total_refs)

    def _barra_fallos(self, parent, resultados, total_refs):
        ctk.CTkLabel(
            parent,
            text="Fallos de página por algoritmo",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(pady=(20, 8))

        bar_frame = ctk.CTkFrame(parent, corner_radius=10)
        bar_frame.pack(padx=40, pady=5, fill="x")

        max_fallos = max(v[1] for v in resultados.values()) or 1
        COLORES = {"FIFO": "#E05252", "Óptimo": "#52B0E0", "LRU": "#52E07A"}

        for nombre, (_, fallos) in resultados.items():
            row = ctk.CTkFrame(bar_frame, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)

            ctk.CTkLabel(row, text=f"{nombre:10}", width=80,
                         font=ctk.CTkFont(size=12)).pack(side="left")

            bw = max(int((fallos / max_fallos) * 420), 10)
            color = COLORES.get(nombre, "#7EB8F7")
            barra = ctk.CTkFrame(row, width=bw, height=26, fg_color=color, corner_radius=5)
            barra.pack(side="left", padx=(5, 8))
            barra.pack_propagate(False)

            ctk.CTkLabel(row, text=f"{fallos} fallos",
                         font=ctk.CTkFont(size=12)).pack(side="left")

    # ── Limpiar ───────────────────────────────────────────────────────────────

    def limpiar(self):
        self.entry_refs.delete(0, "end")
        self.entry_marcos.delete(0, "end")

        for nombre, widgets in self.frames_algo.items():
            for w in widgets["inner"].winfo_children():
                w.destroy()
            widgets["lbl_resumen"].configure(text="Sin resultados aún.")

        for w in self.frame_comparacion["frame"].winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.frame_comparacion["frame"],
            text="Simula primero para ver la comparación.",
            font=ctk.CTkFont(size=14),
        ).pack(expand=True)
        self.frame_comparacion["lbl"] = None


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = SimuladorApp()
    app.mainloop()
