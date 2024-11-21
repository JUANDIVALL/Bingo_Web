from flask import Flask, render_template, request, redirect, url_for, session
import os
def crear_app():

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

        usuario = session["usuario"]
        
        # Asegurarse de que cada usuario tenga sus configuraciones
        if usuario not in session:
            session[usuario] = {"figura": None}

        if request.method == "POST":
            figura_seleccionada = request.form["figura"]
            session[usuario]["figura"] = figura_seleccionada  # Guardar la figura seleccionada por el usuario
            return redirect(url_for("bingo"))

        return render_template("select_figure.html")


    # Ruta principal del juego
    @app.route("/bingo", methods=["GET", "POST"])
    def bingo():
        if "usuario" not in session:
            return redirect(url_for("login"))

        usuario = session["usuario"]
        
        # Obtener figura específica de la sesión del usuario
        figura = session.get(usuario, {}).get("figura", "full")
        
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
                if numero > 75 or numero < 1:
                    mensaje = "El número debe ser entre 1 y 75."
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
        orden_bingo = {letter: [] for letter in "BINGO"}
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

#Cartillas usuario Sori2024

    N_3468 = crear_cartilla("N° 3468", {
        "B": [11,3,10,2,8],
        "I": [23,17,30,22,29],
        "N": [42,35,41,34],
        "G": [49,55,54,48,46],
        "O": [61,69,75,68,74]
    })

    N_3469 = crear_cartilla("N° 3469", {
        "B": [14,7,13,6,5],
        "I": [20,27,19,26,18],
        "N": [40,38,32,45],
        "G": [52,60,59,51,58],
        "O": [73,72,65,71,64]
    })

    N_3470 = crear_cartilla("N° 3470", {
        "B": [4,10,9,3,1],
        "I": [16,24,29,23,22],
        "N": [37,43,36,35],
        "G": [56,48,47,55,53],
        "O": [68,62,61,67,74]
    })

    N_3471 = crear_cartilla("N° 3471", {
        "B": [14,6,13,12,5],
        "I": [20,26,25,19,24],
        "N": [39,33,31,45],
        "G": [58,51,50,57,49],
        "O": [62,70,68,61,67]
    })

    N_3472 = crear_cartilla("N° 3472", {
        "B": [7,14,6,13,12],
        "I": [27,20,26,25,19],
        "N": [34,39,33,31],
        "G": [59,52,58,51,50],
        "O": [69,72,68,61,67]
    })

    N_3473 = crear_cartilla("N° 3473", {
        "B": [10,4,9,3,2],
        "I": [17,24,30,23,29],
        "N": [36,35,42,34],
        "G": [47,55,54,53,46],
        "O": [61,67,74,66,73]
    })

    N_3474 = crear_cartilla("N° 3474", {
        "B": [13,12,5,11,10],
        "I": [25,19,24,18,17],
        "N": [32,39,45,38],
        "G": [51,50,57,49,48],
        "O": [74,67,66,73,72]
    })

    N_3475 = crear_cartilla("N° 3475", {
        "B": [7,13,6,5,4],
        "I": [19,27,18,26,25],
        "N": [40,39,32,38],
        "G": [53,46,52,59,51],
        "O": [66,73,72,71,65]
    })

    N_3476 = crear_cartilla("N° 3476", {
        "B": [5,10,4,9,3],
        "I": [18,17,24,30,23],
        "N": [38,44,37,43],
        "G": [58,51,50,49,57],
        "O": [72,63,71,62,70]
    })

    N_3477 = crear_cartilla("N° 3477", {
        "B": [10,9,2,8,1],
        "I": [16,22,29,21,27],
        "N": [42,36,41,35],
        "G": [50,55,49,48,47],
        "O": [62,69,75,68,74]
    })

    N_3478 = crear_cartilla("N° 3478", {
        "B": [14,7,13,5,4],
        "I": [25,24,17,23,16],
        "N": [36,44,42,41],
        "G": [56,50,55,49,48],
        "O": [63,62,69,75,68]
    })

    N_3479 = crear_cartilla("N° 3479", {
        "B": [8,14,7,13,6],
        "I": [21,20,28,19,27],
        "N": [42,33,41,40],
        "G": [55,54,47,53,46],
        "O": [61,67,75,66,74]
    })

    N_3480 = crear_cartilla("N° 3480", {
        "B": [14,12,6,11,5],
        "I": [23,29,22,28,20],
        "N": [35,43,34,42],
        "G": [57,49,56,48,55],
        "O": [67,69,62,68,61]
    })

    N_3481 = crear_cartilla("N° 3481", {
        "B": [1,7,14,6,12],
        "I": [27,21,26,20,19],
        "N": [40,34,33,32],
        "G": [47,54,60,53,59],
        "O": [74,67,73,65,64]
    })

    N_3482 = crear_cartilla("N° 3482", {
        "B": [4,12,11,3,10],
        "I": [16,22,30,21,29],
        "N": [44,42,36,35],
        "G": [50,56,49,55,48],
        "O": [63,62,69,61,68]
    })

#--------------------------------------------------------------------------------------------------------------------
#                                                      CREAR USUARIOS
#--------------------------------------------------------------------------------------------------------------------

    # EJEMPLO: crear_usuario("nombre_usuario", "contraseña_usuario", [nombre_cartilla_1, nombre_cartilla_2, ...])
    crear_usuario("admin", "JDVL0509.", [N_1596,N_1597,N_1598,N_1599,N_1600,N_1601,N_1602,N_1603,N_1604,N_1605])

    crear_usuario("Sori2024", "Sori2024",[N_3468,N_3469,N_3470,N_3471,N_3472,N_3473,N_3474,N_3475,N_3476,N_3477,N_3478,N_3479,N_3480,N_3481,N_3482])

    return app
    

if __name__ == "__main__":

    app=crear_app()

#  Ejecutar Bingo-Web
    app.run(debug=True)