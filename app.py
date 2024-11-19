from flask import Flask, render_template, request, redirect, url_for, session
import os

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones"  # Cambia esto a una clave segura

# Base de datos simulada para usuarios y cartillas
usuarios = {}

# Clase Cartilla
class BingoCard:
    def __init__(self, identifier, numbers):
        self.identifier = identifier
        self.numbers = numbers  # Se asume que "numbers" es un diccionario con las letras BINGO
        self.marked_numbers = {letter: [] for letter in "BINGO"}

    def mark_number(self, number):
        """Marca un número si está presente en la cartilla."""
        for letter in "BINGO":
            if number in self.numbers[letter] and number not in self.marked_numbers[letter]:
                self.marked_numbers[letter].append(number)
                return True
        return False

    def check_figure(self, figure):
        """Verifica si la cartilla cumple con la figura dada."""
        if figure == "full":
            return (
                len(self.marked_numbers["B"]) == 5 and 
                len(self.marked_numbers["I"]) == 5 and 
                len(self.marked_numbers["N"]) == 4 and
                len(self.marked_numbers["G"]) == 5 and
                len(self.marked_numbers["O"]) == 5
            )
        
        elif figure == "i":
            return len(self.marked_numbers["N"]) == 4

        elif figure == "o":
            return (
                len(self.marked_numbers["B"]) == 5 and
                len(self.marked_numbers["O"]) == 5 and
                self.numbers["I"][0] in self.marked_numbers["I"] and
                self.numbers["I"][-1] in self.marked_numbers["I"] and
                self.numbers["N"][0] in self.marked_numbers["N"] and
                self.numbers["N"][-1] in self.marked_numbers["N"] and
                self.numbers["G"][0] in self.marked_numbers["G"] and
                self.numbers["G"][-1] in self.marked_numbers["G"]
            )
        
        elif figure == "u":
            return (
                len(self.marked_numbers["B"]) == 5 and
                len(self.marked_numbers["O"]) == 5 and
                self.numbers["I"][-1] in self.marked_numbers["I"] and
                self.numbers["N"][-1] in self.marked_numbers["N"] and
                self.numbers["G"][-1] in self.marked_numbers["G"]
            )

        elif figure == "l":
            return (
                len(self.marked_numbers["B"]) == 5 and
                self.numbers["I"][-1] in self.marked_numbers["I"] and
                self.numbers["N"][-1] in self.marked_numbers["N"] and
                self.numbers["G"][-1] in self.marked_numbers["G"] and
                self.numbers["O"][-1] in self.marked_numbers["O"]
            )

        return False

    def reset_marks(self):
        """Reinicia las marcas de la cartilla."""
        self.marked_numbers = {letter: [] for letter in "BINGO"}

# Función para crear un usuario
def crear_usuario(usuario, contraseña, cartillas):
    """Función para crear un usuario con su contraseña y asociarle cartillas."""
    if usuario in usuarios:
        print("El usuario ya existe.")
    else:
        usuarios[usuario] = {"contraseña": contraseña, "cartillas": cartillas}
        print(f"Usuario {usuario} creado con éxito.")

# Función para crear una cartilla
def crear_cartilla(identifier, numbers):
    """Crea una cartilla con identificador y números."""
    return BingoCard(identifier, numbers)

# Ruta de inicio de sesión
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]
        if usuario in usuarios and usuarios[usuario]["contraseña"] == contraseña:
            session["usuario"] = usuario
            session["numeros_llamados"] = []  # Inicializamos la lista de números llamados
            return redirect(url_for("select_figure"))
        else:
            mensaje = """Contraseña o Usuario incorrecto. 
            Si quieres crear una cuenta, por favor escribe al +51 960065015."""
            return render_template("login.html", mensaje=mensaje)
    return render_template("login.html")

# Ruta para seleccionar la figura
@app.route("/select_figure", methods=["GET", "POST"])
def select_figure():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        session["figura"] = request.form["figura"]
        return redirect(url_for("bingo"))
    return render_template("select_figure.html")

# Ruta principal del juego
@app.route("/bingo", methods=["GET", "POST"])
def bingo():
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    usuario = session["usuario"]
    figura = session.get("figura", "full")
    mensaje = None
    mostrar_formulario = True
    mostrar_boton_reinicio = True
    numeros_llamados = session.get("numeros_llamados", [])
    cartilla_ganadora = None  # Variable para identificar la cartilla ganadora
    
    if request.method == "POST":
        try:
            numero = int(request.form["numero"])
        except ValueError:
            mensaje = "Por favor, ingresa un número válido."
        else:
            if numero > 75:
                mensaje = "El número debe ser entre 1 y 75."
            elif numero < 1:
                mensaje = "El número debe ser mayor a 0."
            elif numero not in numeros_llamados:
                numeros_llamados.append(numero)
                session["numeros_llamados"] = numeros_llamados
                for cartilla in usuarios[usuario]["cartillas"]:
                    if cartilla.mark_number(numero):
                        if cartilla.check_figure(figura):
                            mensaje = f"¡BINGO! La cartilla {cartilla.identifier} completó la figura {figura.upper()}."
                            cartilla_ganadora = cartilla.identifier  # Identificar la cartilla ganadora
                            mostrar_formulario = False
                            mostrar_boton_reinicio = True
            else:
                mensaje = "Este número ya ha sido llamado."

    # Ordenar los números llamados en B-I-N-G-O
    orden_bingo = {
        "B": [],
        "I": [],
        "N": [],
        "G": [],
        "O": []
    }
    for numero in numeros_llamados:
        for letter in "BINGO":
            if numero in usuarios[usuario]["cartillas"][0].numbers[letter]:
                orden_bingo[letter].append(numero)
                break

    return render_template("bingo.html", 
                           mensaje=mensaje, 
                           mostrar_formulario=mostrar_formulario,
                           mostrar_boton_reinicio=mostrar_boton_reinicio, 
                           numeros_llamados=numeros_llamados,
                           cartillas=usuarios[usuario]["cartillas"], 
                           figura=figura, 
                           cartilla_ganadora=cartilla_ganadora,  # Enviar la cartilla ganadora
                           orden_bingo=orden_bingo)

# Ruta para reiniciar las cartillas
@app.route("/reiniciar", methods=["POST"])
def reiniciar():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario = session["usuario"]
    for cartilla in usuarios[usuario]["cartillas"]:
        cartilla.reset_marks()

    # Limpiamos la lista de números llamados y la figura seleccionada
    session["numeros_llamados"] = []
    session["figura"] = None  # Limpiamos la figura seleccionada actual
    return redirect(url_for("select_figure"))

if __name__ == "__main__":

#--------------------------------------------------------------------------------------------------------------------
#                                                    CREAR CARTILLAS
#--------------------------------------------------------------------------------------------------------------------

    # EJEMPLO: el de abajo: (me da flojera explicarlo)

    """ 
    N_ = crear_cartilla("N° ", {
        "B": [],
        "I": [],
        "N": [],
        "G": [],
        "O": []
    })
    
"""

#Cartillas Usuario Admin:
    N_1596 = crear_cartilla("N° 1596", {
        "B": [5,1,4,12,14],
        "I": [20,23,21,30,25],
        "N": [43,33,45,31],
        "G": [52,58,48,47,53],
        "O": [75,70,62,67,72]
    })

    N_1597 = crear_cartilla("N° 1597", {
        "B": [1,3,12,9,4],
        "I": [23,24,30,22,21],
        "N": [33,44,37,45],
        "G": [48,56,58,59,47],
        "O": [62,71,70,64,67]
    })

    N_1598 = crear_cartilla("N° 1598", {
        "B": [12,7,3,11,9],
        "I": [24,18,22,27,30],
        "N": [44,36,42,37],
        "G": [58,54,56,51,59],
        "O": [71,65,64,66,70]
    })

    N_1599 = crear_cartilla("N° 1599", {
        "B": [7,13,11,6,3],
        "I": [22,26,18,16,27],
        "N": [36,39,38,42],
        "G": [56,60,54,57,51],
        "O": [65,69,66,63,64]
    })

    N_1600 = crear_cartilla("N° 1600", {
        "B": [13,2,6,15,11],
        "I": [18,19,16,26,29],
        "N": [39,41,35,38],
        "G": [60,46,57,55,54],
        "O": [66,68,69,61,63]
    })

    N_1601 = crear_cartilla("N° 1601", {
        "B": [6,14,2,4,15],
        "I": [19,25,29,21,26],
        "N": [41,34,43,35],
        "G": [46,53,55,47,57],
        "O": [69,72,68,67,61]
    })

    N_1602 = crear_cartilla("N° 1602", {
        "B": [4,3,9,6,10],
        "I": [17,23,28,30,22],
        "N": [44,39,41,42],
        "G": [46,49,54,53,50],
        "O": [67,74,62,61,65]
    })

    N_1603 = crear_cartilla("N° 1603", {
        "B": [9,5,3,14,6],
        "I": [28,20,23,27,30],
        "N": [39,38,34,41],
        "G": [49,56,53,60,54],
        "O": [74,64,61,71,62]
    })

    N_1604 = crear_cartilla("N° 1604", {
        "B": [5,1,14,8,3],
        "I": [20,24,27,16,23],
        "N": [38,36,31,34],
        "G": [53,58,56,59,60],
        "O": [61,68,64,72,71]
    })

    N_1605 = crear_cartilla("N° 1605", {
        "B": [2,14,1,15,8],
        "I": [24,26,16,18,27],
        "N": [36,40,32,31],
        "G": [56,47,58,48,59],
        "O": [68,63,72,66,64]
    })


#--------------------------------------------------------------------------------------------------------------------
#                                                      CREAR USUARIOS
#--------------------------------------------------------------------------------------------------------------------

    # EJEMPLO: crear_usuario("nombre_usuario", "contraseña_usuario", [nombre_cartilla_1, nombre_cartilla_2, ...])
    crear_usuario("admin", "JDVL0509.", [N_1596,N_1597,N_1598,N_1599,N_1600,N_1601,N_1602,N_1603,N_1604,N_1605])


#  Ejecutar Bingo-Web
    app.run(debug=True)