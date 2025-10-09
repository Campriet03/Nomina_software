import tkinter as tk
from tkinter import messagebox, ttk

SMMLV = 1423500
Auxilio_Transporte = 200000

class SoftwareNomina:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema de Nómina")
        self.ventana.geometry("1200x650")
        self.ventana.configure(bg="black")

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="black", borderwidth=0)
        style.configure("TNotebook.Tab", background="gray20", foreground="white", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "orange")], foreground=[("selected", "black")])
        style.configure("Treeview", background="gray15", foreground="white", rowheight=25,
                        fieldbackground="gray15", borderwidth=0)
        style.map("Treeview", background=[("selected", "orange")], foreground=[("selected", "black")])

        self.notebook = ttk.Notebook(self.ventana)
        self.notebook.pack(fill='both', expand=True)

        self.pestana1 = tk.Frame(self.notebook, bg="black")
        self.pestana2 = tk.Frame(self.notebook, bg="black")
        self.pestana3 = tk.Frame(self.notebook, bg="black")

        self.notebook.add(self.pestana1, text="Nómina Básica")
        self.notebook.add(self.pestana2, text="Aportes y Prestaciones")
        self.notebook.add(self.pestana3, text="Contabilizaciones")

        self.crear_pestana1()
        self.crear_pestana2()
        self.crear_pestana3()

        self.contabilizaciones = {}

    def crear_pestana1(self):
        frame = self.pestana1
        campos = [("Nombre del empleado", "nombre_empleado"),
                  ("Documento", "documento"),
                  ("Sueldo básico", "salario_base"),
                  ("Días laborados", "dias_laborados"),
                  ("Horas extras diurnas", "horas_extras_d"),
                  ("Horas extras nocturnas", "horas_extras_n"),
                  ("Nivel de ARL (1-5)", "nivel_arl")]
        self.entradas = {}

        for i, (texto, nombre_var) in enumerate(campos):
            tk.Label(frame, text=texto, bg="black", fg="white").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = tk.Entry(frame, bg="gray20", fg="white", insertbackground="white")
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entradas[nombre_var] = entry

        tk.Button(frame, text="Agregar", command=self.agregar_nombre,
                  bg="orange", fg="black").grid(row=7, column=0, padx=10, pady=10)
        tk.Button(frame, text="Eliminar", command=self.eliminar_nombre,
                  bg="red", fg="white").grid(row=7, column=1, padx=10, pady=10)

        columnas = ("nombre", "documento", "salario", "dias", "sueldo", "auxilio",
                    "hed", "hen", "devengado", "salud", "pension", "deducciones", "neto")
        self.tabla1 = ttk.Treeview(frame, columns=columnas, show="headings", height=10)
        for col in columnas:
            self.tabla1.heading(col, text=col.capitalize())
            self.tabla1.column(col, width=100)

        self.tabla1.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
        self.tabla1.bind('<Double-1>', self.editar_celda)

    def crear_pestana2(self):
        frame = self.pestana2
        columnas = ("Salud Empl. (8.5%)", "Pensión Empl. (12%)", "ARL (%)",
                    "Caja Comp. (4%)", "SENA (2%)", "ICBF (3%)",
                    "Cesantías (8.33%)", "Intereses (12%)", "Prima (8.33%)", "Vacaciones (4.17%)")
        self.tabla2 = ttk.Treeview(frame, columns=columnas, show="headings", height=10)
        for col in columnas:
            self.tabla2.heading(col, text=col)
            self.tabla2.column(col, width=120)
        self.tabla2.grid(row=0, column=0, padx=10, pady=10)

    def crear_pestana3(self):
        frame = self.pestana3
        columnas = ("Cuenta", "Descripción", "Débito", "Crédito")
        self.tabla3 = ttk.Treeview(frame, columns=columnas, show="headings", height=15)
        for col in columnas:
            self.tabla3.heading(col, text=col)
            self.tabla3.column(col, width=200)
        self.tabla3.grid(row=0, column=0, padx=10, pady=10)

    def actualizar_contabilizacion(self, cuenta, descripcion, valor, tipo):
        clave = (cuenta, descripcion)
        if clave not in self.contabilizaciones:
            self.contabilizaciones[clave] = {"debito": 0, "credito": 0}
        self.contabilizaciones[clave][tipo] += valor
        self.redibujar_tabla3()

    def redibujar_tabla3(self):
        for item in self.tabla3.get_children():
            self.tabla3.delete(item)
        for (cuenta, descripcion), valores in self.contabilizaciones.items():
            debito = valores["debito"]
            credito = valores["credito"]
            self.tabla3.insert("", tk.END, values=(cuenta, descripcion,
                                                   f"${debito:,.0f}" if debito else "",
                                                   f"${credito:,.0f}" if credito else ""))

    def agregar_nombre(self):
        try:
            nombre = self.entradas["nombre_empleado"].get().strip()
            documento = self.entradas["documento"].get().strip()
            salario = int(self.entradas["salario_base"].get().strip())
            dias = int(self.entradas["dias_laborados"].get().strip())
            hed = int(self.entradas["horas_extras_d"].get().strip())
            hen = int(self.entradas["horas_extras_n"].get().strip())
            nivel_arl = int(self.entradas["nivel_arl"].get().strip())

            if not nombre or not documento.isdigit() or nivel_arl not in [1, 2, 3, 4, 5]:
                messagebox.showerror("Error", "Datos inválidos. Complete todos los campos correctamente.")
                return

            sueldo = (salario / 30) * dias
            valor_hora = salario / 230
            pago_hed = valor_hora * 1.25 * hed
            pago_hen = valor_hora * 1.75 * hen
            auxilio = Auxilio_Transporte if salario <= 2 * SMMLV else 0
            devengado = sueldo + auxilio + pago_hed + pago_hen

            salud = (sueldo + pago_hed + pago_hen) * 0.04
            pension = (sueldo + pago_hed + pago_hen) * 0.04
            deducciones = salud + pension
            neto = devengado - deducciones

            salud_emp = devengado * 0.085
            pension_emp = devengado * 0.12
            porcentajes_arl = {1: 0.00522, 2: 0.01044, 3: 0.02436, 4: 0.04350, 5: 0.06960}
            porcentaje_arl = porcentajes_arl[nivel_arl]
            arl = devengado * porcentaje_arl

            caja = devengado * 0.04
            sena = devengado * 0.02
            icbf = devengado * 0.03
            cesantias = devengado * 0.0833
            intereses = cesantias * 0.12
            prima = devengado * 0.0833
            vacaciones = sueldo * 0.0417
            pagoh = pago_hed + pago_hen

            self.tabla1.insert("", tk.END, values=(
                nombre, documento, f"${salario:,.0f}", dias,
                f"${sueldo:,.0f}", f"${auxilio:,.0f}",
                f"${pago_hed:,.0f}", f"${pago_hen:,.0f}",
                f"${devengado:,.0f}", f"${salud:,.0f}", f"${pension:,.0f}",
                f"${deducciones:,.0f}", f"${neto:,.0f}"
            ))

            self.tabla2.insert("", tk.END, values=(
                f"${salud_emp:,.0f}", f"${pension_emp:,.0f}",
                f"${arl:,.0f} ({porcentaje_arl*100:.2f}%)",
                f"${caja:,.0f}", f"${sena:,.0f}", f"${icbf:,.0f}",
                f"${cesantias:,.0f}", f"${intereses:,.0f}",
                f"${prima:,.0f}", f"${vacaciones:,.0f}"
            ))

            self.actualizar_contabilizacion("510506", "Sueldo", sueldo, "debito")
            self.actualizar_contabilizacion("510527", "Auxilio Transporte", auxilio, "debito")
            self.actualizar_contabilizacion("510515", "Horas Extra", pagoh, "debito")
            self.actualizar_contabilizacion("237005", "Aportes a EPS", salud, "credito")
            self.actualizar_contabilizacion("238030", "Aportes a pensión", pension, "credito")
            self.actualizar_contabilizacion("237010", "Aportes Salud Empleador", salud_emp, "credito")
            self.actualizar_contabilizacion("238035", "Aportes Pensión Empleador", pension_emp, "credito")
            self.actualizar_contabilizacion("237015", "ARL", arl, "credito")
            self.actualizar_contabilizacion("237020", "Caja de Compensación", caja, "credito")
            self.actualizar_contabilizacion("237025", "SENA", sena, "credito")
            self.actualizar_contabilizacion("237030", "ICBF", icbf, "credito")
            self.actualizar_contabilizacion("251005", "Cesantías", cesantias, "credito")
            self.actualizar_contabilizacion("251010", "Intereses Cesantías", intereses, "credito")
            self.actualizar_contabilizacion("251015", "Prima de Servicios", prima, "credito")
            self.actualizar_contabilizacion("251020", "Vacaciones", vacaciones, "credito")

            self.limpiar_campos()
        except ValueError:
            messagebox.showerror("Error", "Verifique los campos: deben ser valores numéricos válidos.")

    def editar_celda(self, event):
        item = self.tabla1.identify_row(event.y)
        columna = self.tabla1.identify_column(event.x)
        col_num = int(columna[1:]) - 1

        if not item:
            return

        x, y, width, height = self.tabla1.bbox(item, columna)
        valor_actual = self.tabla1.item(item, "values")[col_num]

        entry = tk.Entry(self.tabla1)
        entry.insert(0, valor_actual.replace("$", "").replace(",", ""))
        entry.place(x=x, y=y, width=width, height=height)
        entry.focus()

        def guardar(evento):
            nuevo_valor = entry.get()
            if nuevo_valor.replace(".", "").isdigit():
                valores = list(self.tabla1.item(item, "values"))
                valores[col_num] = f"${int(nuevo_valor):,}"
                self.tabla1.item(item, values=valores)
            entry.destroy()

        entry.bind("<Return>", guardar)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def limpiar_campos(self):
        for campo in self.entradas.values():
            campo.delete(0, tk.END)

    def eliminar_nombre(self):
        for tabla in [self.tabla1, self.tabla2, self.tabla3]:
            seleccion = tabla.selection()
            for item in seleccion:
                tabla.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = SoftwareNomina(root)
    root.mainloop()
