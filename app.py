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
                return len(self.marked_numbers["B"]) == 5

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

# Cartillas usuario Elena

    N_0720 = crear_cartilla("N° 0720", {
        "B": [12,11,5,10,6],
        "I": [26,30,17,16,24],
        "N": [33,31,36,42],
        "G": [52,49,60,54,47],
        "O": [61,64,62,68,63]
    })

    N_0721 = crear_cartilla("N° 0721", {
        "B": [1,7,2,10,6],
        "I": [17,18,27,16,24],
        "N": [45,38,37,31],
        "G": [54,48,50,47,52],
        "O": [66,75,72,62,67]
    })

    N_0722 = crear_cartilla("N° 0722", {
        "B": [11,2,4,8,9],
        "I": [30,25,23,27,20],
        "N": [36,39,32,38],
        "G": [49,55,53,57,46],
        "O": [64,70,69,66,67]
    })

    N_0723 = crear_cartilla("N° 0723", {
        "B": [11,12,13,10,14],
        "I": [26,20,28,24,30],
        "N": [34,41,37,32],
        "G": [50,56,51,60,52],
        "O": [64,72,71,63,67]
    })

    N_0724 = crear_cartilla("N° 0724", {
        "B": [7,6,8,11,2],
        "I": [23,24,27,17,30],
        "N": [45,44,37,35],
        "G": [52,47,53,60,51],
        "O": [66,63,65,64,61]
    })

    N_0725 = crear_cartilla("N° 0725", {
        "B": [13,5,14,11,10],
        "I": [29,25,30,18,27],
        "N": [31,39,44,41],
        "G": [53,59,58,57,56],
        "O": [63,62,72,67,71]
    })

    N_0726 = crear_cartilla("N° 0726", {
        "B": [9,6,8,10,11],
        "I": [25,18,20,17,22],
        "N": [32,45,37,42],
        "G": [60,57,46,52,48],
        "O": [65,73,64,62,70]
    })

    N_0727 = crear_cartilla("N° 0727", {
        "B": [5,15,13,11,2],
        "I": [24,19,23,26,28],
        "N": [33,38,42,39],
        "G": [57,60,54,56,55],
        "O": [69,75,72,65,63]
    })

    N_0729 = crear_cartilla("N° 0729", {
        "B": [4,11,7,12,14],
        "I": [29,17,25,28,27],
        "N": [41,34,37,40],
        "G": [47,50,59,46,58],
        "O": [73,72,61,67,70]
    })

    N_0731 = crear_cartilla("N° 0731", {
        "B": [15,11,10,3,5],
        "I": [19,29,17,28,18],
        "N": [31,34,33,45],
        "G": [59,46,60,55,50],
        "O": [63,72,69,65,62]
    })

    N_0732 = crear_cartilla("N° 0732", {
        "B": [14,6,1,5,11],
        "I": [28,18,30,20,29],
        "N": [40,32,33,39],
        "G": [56,52,54,51,46],
        "O": [63,70,72,73,61]
    })

    N_0733 = crear_cartilla("N° 0733", {
        "B": [8,13,2,10,15],
        "I": [22,19,27,23,25],
        "N": [39,37,34,40],
        "G": [51,59,53,56,50],
        "O": [67,66,72,74,61]
    })

    N_0734 = crear_cartilla("N° 0734", {
        "B": [8,10,12,14,13],
        "I": [24,21,16,28,23],
        "N": [34,35,43,31],
        "G": [50,60,49,46,58],
        "O": [70,71,68,61,75]
    })


# Cartillas usuario Ariana

    N_2899 = crear_cartilla("N° 2899", {
        "B": [4,13,3,1,9],
        "I": [30,23,22,21,19],
        "N": [34,41,33,38],
        "G": [49,47,56,53,60],
        "O": [64,71,74,67,75]
    })

    N_2900 = crear_cartilla("N° 2900", {
        "B": [2,14,10,7,11],
        "I": [24,21,23,28,16],
        "N": [36,37,39,33],
        "G": [58,54,53,48,49],
        "O": [63,74,64,73,61]
    })

    N_2901 = crear_cartilla("N° 2901", {
        "B": [1,4,10,11,12],
        "I": [27,18,23,29,17],
        "N": [33,36,43,42],
        "G": [46,49,47,53,56],
        "O": [75,64,69,68,71]
    })

    N_2902 = crear_cartilla("N° 2902", {
        "B": [12,9,15,2,10],
        "I": [17,23,18,30,27],
        "N": [43,40,39,37],
        "G": [57,49,46,52,47],
        "O": [70,72,71,68,64]
    })

    N_2903 = crear_cartilla("N° 2903", {
        "B": [1,4,6,9,8],
        "I": [16,25,29,24,20],
        "N": [34,44,37,39],
        "G": [60,57,56,48,49],
        "O": [61,71,67,63,62]
    })

    N_2904 = crear_cartilla("N° 2904", {
        "B": [7,15,3,4,2],
        "I": [26,28,22,23,18],
        "N": [45,35,44,41],
        "G": [56,46,54,59,49],
        "O": [62,75,63,73,74]
    })

    N_2905 = crear_cartilla("N° 2905", {
        "B": [3,12,15,13,4],
        "I": [22,19,28,21,23],
        "N": [35,32,36,44],
        "G": [46,58,49,53,54],
        "O": [75,70,73,72,63]
    })

    N_2906 = crear_cartilla("N° 2906", {
        "B": [12,1,13,5,15],
        "I": [19,17,21,29,28],
        "N": [32,42,34,36],
        "G": [49,59,58,47,53],
        "O": [73,61,70,64,72]
    })

    N_2907 = crear_cartilla("N° 2907", {
        "B": [13,10,1,11,5],
        "I": [17,30,29,16,21],
        "N": [42,40,38,34],
        "G": [58,60,59,55,47],
        "O": [61,66,64,71,70]
    })

    N_2908 = crear_cartilla("N° 2908", {
        "B": [10,8,11,14,1],
        "I": [29,25,30,20,16],
        "N": [40,37,39,38],
        "G": [59,50,60,48,55],
        "O": [66,69,71,65,64]
    })

    N_2909 = crear_cartilla("N° 2909", {
        "B": [8,9,14,6,11],
        "I": [30,27,25,24,20],
        "N": [37,43,33,39],
        "G": [50,52,48,51,60],
        "O": [71,67,69,68,65]
    })

    N_2910 = crear_cartilla("N° 2910", {
        "B": [2,4,1,15,14],
        "I": [21,18,23,29,19],
        "N": [39,38,44,35],
        "G": [57,54,58,47,53],
        "O": [61,73,69,68,72]
    })

    N_2911 = crear_cartilla("N° 2911", {
        "B": [12,3,6,11,13],
        "I": [30,27,19,17,25],
        "N": [43,45,31,39],
        "G": [53,55,56,54,50],
        "O": [68,61,71,70,72]
    })

    N_2912 = crear_cartilla("N° 2912", {
        "B": [14,7,15,12,1],
        "I": [25,29,26,19,28],
        "N": [31,35,38,44],
        "G": [54,46,55,53,49],
        "O": [61,70,73,75,68]
    })

    N_2913 = crear_cartilla("N° 2913", {
        "B": [7,15,1,6,2],
        "I": [18,21,27,24,19],
        "N": [38,31,39,40],
        "G": [47,55,54,53,59],
        "O": [75,73,61,71,68]
    })

#Cartillas usuario fernando solis

    N_0090 = crear_cartilla("N° 0090", {
        "B": [15,5,7,10,11],
        "I": [16,28,19,17,22],
        "N": [43,36,34,31],
        "G": [56,50,55,46,60],
        "O": [67,73,69,71,66]
    })
    
    N_0091 = crear_cartilla("N° 0091", {
        "B": [2,14,7,10,15],
        "I": [26,29,28,21,17],
        "N": [35,39,31,42],
        "G": [48,52,57,51,54],
        "O": [61,64,68,66,73]
    })
    
    N_0092 = crear_cartilla("N° 0092", {
        "B": [7,12,8,10,6],
        "I": [23,29,22,17,26],
        "N": [36,32,44,35],
        "G": [60,54,57,46,51],
        "O": [67,63,73,69,68]
    })

    N_0093 = crear_cartilla("N° 0093", {
        "B": [15,5,8,6,9],
        "I": [27,18,20,24,19],
        "N": [35,32,37,36],
        "G": [55,56,57,52,49],
        "O": [74,62,66,67,72]
    })

    N_0094 = crear_cartilla("N° 0094", {
        "B": [7,3,10,5,2],
        "I": [24,25,18,26,16],
        "N": [38,42,34,37],
        "G": [50,46,48,56,47],
        "O": [75,63,62,71,72]
    })

    N_0095 = crear_cartilla("N° 0095", {
        "B": [12,8,10,15,13],
        "I": [28,19,20,25,24],
        "N": [41,40,42,37],
        "G": [51,59,56,49,60],
        "O": [72,65,63,61,71]
    })

    N_0096 = crear_cartilla("N° 0096", {
        "B": [14,13,3,11,10],
        "I": [30,25,22,29,16],
        "N": [36,34,44,42],
        "G": [58,60,46,52,47],
        "O": [65,63,66,74,68]
    })
    N_0097 = crear_cartilla("N° 0097", {
        "B": [5,13,3,10,1],
        "I": [26,22,16,29,28],
        "N": [42,34,40,44],
        "G": [60,48,47,46,56],
        "O": [61,62,68,72,73]
    })

    N_0098 = crear_cartilla("N° 0098", {
        "B": [8,15,7,9,3],
        "I": [19,27,17,18,21],
        "N": [36,43,40,34],
        "G": [58,56,60,50,59],
        "O": [67,70,65,62,63]
    })

    N_0099 = crear_cartilla("N° 0099", {
        "B": [12,2,1,5,7],
        "I": [30,23,21,25,26],
        "N": [32,44,41,45],
        "G": [55,51,46,56,60],
        "O": [72,61,66,67,70]
    })

    N_0100 = crear_cartilla("N° 0100", {
        "B": [1,8,7,4,11],
        "I": [28,23,22,24,18],
        "N": [37,36,32,31],
        "G": [48,49,47,56,57],
        "O": [66,74,72,73,67]
    })

    N_0101 = crear_cartilla("N° 0101", {
        "B": [1,2,3,12,7],
        "I": [21,27,29,26,16],
        "N": [34,44,38,31],
        "G": [49,50,55,57,56],
        "O": [66,67,68,61,72]
    })

    N_0102 = crear_cartilla("N° 0102", {
        "B": [11,15,12,10,7],
        "I": [17,24,28,19,25],
        "N": [34,35,43,37],
        "G": [59,51,50,52,46],
        "O": [61,66,72,63,67]
    })

    N_0103 = crear_cartilla("N° 0103", {
        "B": [7,9,12,2,1],
        "I": [19,20,28,16,21],
        "N": [43,42,35,40],
        "G": [60,49,48,54,47],
        "O": [61,75,65,73,69]
    })

    N_0104 = crear_cartilla("N° 0104", {
        "B": [8,1,4,12,5],
        "I": [22,21,30,28,17],
        "N": [32,39,40,33],
        "G": [55,47,58,54,46],
        "O": [64,69,63,73,62]
    })

# Cartillas tia Charo

    N_2719 = crear_cartilla("N° 2719 (Charo)", {
        "B": [4,14,13,12,2],
        "I": [16,26,28,18,20],
        "N": [44,35,37,43],
        "G": [57,50,46,59,52],
        "O": [74,69,67,64,61]
    })

    N_2720 = crear_cartilla("N° 2720 (Charo)", {
        "B": [12,8,2,6,5],
        "I": [18,26,21,27,30],
        "N": [35,40,32,39],
        "G": [53,54,52,57,47],
        "O": [69,73,67,63,62]
    })

    N_2721 = crear_cartilla("N° 2721 (Charo)", {
        "B": [1,6,4,5,14],
        "I": [19,26,23,20,28],
        "N": [43,32,33,35],
        "G": [49,48,57,53,47],
        "O": [67,75,73,71,72]
    })

    N_2722 = crear_cartilla("N° 2722 (Charo)", {
        "B": [8,7,2,1,10],
        "I": [23,17,28,25,16],
        "N": [42,43,39,32],
        "G": [54,51,60,57,52],
        "O": [64,68,72,61,69]
    })

    N_2723 = crear_cartilla("N° 2723 (Charo)", {
        "B": [15,9,7,2,3],
        "I": [27,19,18,16,23],
        "N": [34,45,42,37],
        "G": [54,50,51,56,55],
        "O": [68,62,69,73,63]
    })

    N_2724 = crear_cartilla("N° 2724 (Charo)", {
        "B": [3,14,11,13,6],
        "I": [19,25,28,17,30],
        "N": [39,44,33,31],
        "G": [57,60,50,59,52],
        "O": [71,73,68,61,72]
    })

    N_2725 = crear_cartilla("N° 2725 (Charo)", {
        "B": [14,2,8,4,6],
        "I": [19,25,28,26,30],
        "N": [35,38,39,45],
        "G": [59,49,52,46,60],
        "O": [74,71,75,68,61]
    })

    N_2726 = crear_cartilla("N° 2726 (Charo)", {
        "B": [14,7,9,5,3],
        "I": [25,19,29,30,26],
        "N": [43,37,42,36],
        "G": [49,58,46,60,52],
        "O": [61,72,69,75,70]
    })

    N_2727 = crear_cartilla("N° 2727 (Charo)", {
        "B": [11,2,8,1,3],
        "I": [21,24,28,16,18],
        "N": [31,37,33,42],
        "G": [49,46,57,52,60],
        "O": [74,69,71,72,61]
    })

    N_2728 = crear_cartilla("N° 2728 (Charo)", {
        "B": [9,15,10,13,12],
        "I": [16,18,21,24,29],
        "N": [32,43,41,36],
        "G": [49,52,59,57,46],
        "O": [69,72,75,61,73]
    })

    N_2729 = crear_cartilla("N° 2729 (Charo)", {
        "B": [7,5,9,8,11],
        "I": [26,24,30,26,29],
        "N": [39,40,41,31],
        "G": [58,60,56,47,52],
        "O": [71,70,61,72,75]
    })

    N_2730 = crear_cartilla("N° 2730 (Charo)", {
        "B": [1,6,10,15,9],
        "I": [28,23,21,19,26],
        "N": [43,42,37,39],
        "G": [52,53,60,46,59],
        "O": [70,62,67,71,61]
    })

    N_2731 = crear_cartilla("N° 2731 (Charo)", {
        "B": [9,3,8,15,12],
        "I": [24,18,26,16,30],
        "N": [37,36,31,41],
        "G": [46,49,48,57,54],
        "O": [63,66,71,64,70]
    })

    N_2732 = crear_cartilla("N° 2732 (Charo)", {
        "B": [6,10,11,3,7],
        "I": [22,30,28,26,18],
        "N": [45,35,41,34],
        "G": [54,58,51,50,47],
        "O": [71,64,72,66,63]
    })

    N_2733 = crear_cartilla("N° 2733 (Charo)", {
        "B": [9,1,13,14,6],
        "I": [23,21,30,29,19],
        "N": [43,31,35,42],
        "G": [52,46,57,55,53],
        "O": [69,62,61,72,68]
    })

# Cartillas de feliroman

    N_0346 = crear_cartilla("N° ", {
        "B": [13,15,12,9,4],
        "I": [23,20,21,28,29],
        "N": [39,40,41,35],
        "G": [51,55,57,53,60],
        "O": [74,70,64,61,73]
    })

    N_0359 = crear_cartilla("N° ", {
        "B": [6,15,11,7,13],
        "I": [29,17,19,25,16],
        "N": [39,41,36,31],
        "G": [57,48,51,47,49],
        "O": [72,64,66,69,71]
    })

    N_0357 = crear_cartilla("N° ", {
        "B": [10,2,4,9,15],
        "I": [21,19,23,24,17],
        "N": [44,45,43,41],
        "G": [57,48,59,49,55],
        "O": [65,64,68,67,62]
    })

    N_0358 = crear_cartilla("N° ", {
        "B": [2,12,13,14,10],
        "I": [27,20,19,16,23],
        "N": [37,43,44,34],
        "G": [59,57,56,47,52],
        "O": [66,75,74,70,72]
    })

    N_0356 = crear_cartilla("N° ", {
        "B": [11,14,13,10,1],
        "I": [29,17,26,20,18],
        "N": [32,41,40,44],
        "G": [57,58,56,47,55],
        "O": [65,72,73,74,75]
    })

    N_0354 = crear_cartilla("N° ", {
        "B": [14,8,11,3,13],
        "I": [26,24,18,17,23],
        "N": [31,38,37,42],
        "G": [53,46,57,50,51],
        "O": [72,66,75,64,70]
    })

    N_0353 = crear_cartilla("N° ", {
        "B": [5,7,11,15,14],
        "I": [30,23,25,21,18],
        "N": [39,38,36,44],
        "G": [58,47,56,51,57],
        "O": [62,74,67,61,72]
    })

    N_0352 = crear_cartilla("N° ", {
        "B": [13,6,3,8,15],
        "I": [19,18,30,22,21],
        "N": [39,38,33,32],
        "G": [51,60,56,49,58],
        "O": [65,69,71,64,63]
    })

    N_0351 = crear_cartilla("N° ", {
        "B": [8,11,9,14,3],
        "I": [16,18,26,27,20],
        "N": [36,42,37,34],
        "G": [59,56,51,53,48],
        "O": [62,73,65,68,66]
    })

    N_0350 = crear_cartilla("N° ", {
        "B": [8,3,6,2,9],
        "I": [20,26,17,16,24],
        "N": [45,42,34,33],
        "G": [46,55,50,52,49],
        "O": [73,75,70,64,66]
    })

    N_0349 = crear_cartilla("N° ", {
        "B": [9,1,3,15,14],
        "I": [22,28,21,18,19],
        "N": [38,39,41,34],
        "G": [48,57,50,59,46],
        "O": [75,70,72,74,71]
    })

    N_0348 = crear_cartilla("N° ", {
        "B": [12,3,4,1,11],
        "I": [27,24,23,19,29],
        "N": [35,37,45,33],
        "G": [49,58,55,51,48],
        "O": [72,68,66,64,75]
    })

    N_0345 = crear_cartilla("N° ", {
        "B": [4,15,2,1,8],
        "I": [25,18,27,28,23],
        "N": [39,41,35,32],
        "G": [55,51,57,56,53],
        "O": [63,65,70,73,66]
    })

    N_0347 = crear_cartilla("N° ", {
        "B": [10,1,8,3,4],
        "I": [24,23,30,19,18],
        "N": [40,39,42,44],
        "G": [60,53,59,57,54],
        "O": [63,69,73,67,75]
    })

    N_0355 = crear_cartilla("N° ", {
        "B": [10,6,1,5,11],
        "I": [26,17,28,21,29],
        "N": [32,45,35,40],
        "G": [56,46,49,51,48],
        "O": [66,62,74,75,63]
    })

    
# Cartillas usuario Nancy

    N_3198 = crear_cartilla("N° ", {
        "B": [4,11,8,1,9],
        "I": [24,17,22,28,23],
        "N": [42,36,33,40],
        "G": [54,49,56,53,46],
        "O": [67,65,72,66,63]
    })

    N_3197 = crear_cartilla("N° ", {
        "B": [10,4,8,15,9],
        "I": [29,27,19,28,20],
        "N": [41,34,38,45],
        "G": [60,54,47,52,58],
        "O": [66,74,67,65,72]
    })

    N_3196 = crear_cartilla("N° ", {
        "B": [4,11,8,15,9],
        "I": [24,17,22,28,29],
        "N": [33,41,34,31],
        "G": [46,53,47,54,59],
        "O": [74,66,67,65,71]
    })

    N_3195 = crear_cartilla("N° ", {
        "B": [11,3,1,8,2],
        "I": [29,22,20,26,21],
        "N": [37,44,42,34],
        "G": [54,47,51,58,52],
        "O": [67,74,72,64,73]
    })

    N_3190 = crear_cartilla("N° ", {
        "B": [10,2,14,6,15],
        "I": [19,26,17,23,24],
        "N": [34,39,32,31],
        "G": [59,47,51,60,52],
        "O": [73,67,72,65,66]
    })

    N_3191 = crear_cartilla("N° ", {
        "B": [6,3,10,4,11],
        "I": [26,17,23,24,22],
        "N": [35,43,36,33],
        "G": [47,53,48,54,49],
        "O": [63,69,64,70,68]
    })

    N_3192 = crear_cartilla("N° ", {
        "B": [8,14,9,1,6],
        "I": [21,28,22,29,26],
        "N": [41,33,45,37],
        "G": [51,59,52,49,56],
        "O": [62,71,63,75,68]
    })

    N_3193 = crear_cartilla("N° ", {
        "B": [12,5,10,2,11],
        "I": [26,18,30,22,17],
        "N": [39,32,36,43],
        "G": [59,52,50,56,57],
        "O": [63,72,69,64,70]
    })

    N_3194 = crear_cartilla("N° ", {
        "B": [1,8,2,13,6],
        "I": [26,21,27,18,24],
        "N": [32,36,43,37],
        "G": [52,59,57,49,58],
        "O": [73,65,70,62,71]
    })

    N_3200 = crear_cartilla("N° ", {
        "B": [6,10,3,11,4],
        "I": [19,17,23,24,29],
        "N": [41,39,31,40],
        "G": [55,47,52,59,53],
        "O": [68,74,72,65,73]
    })

    N_3204 = crear_cartilla("N° ", {
        "B": [15,12,5,13,6],
        "I": [21,26,18,19,17],
        "N": [45,38,35,42],
        "G": [53,60,57,50,58],
        "O": [65,71,69,62,70]
    })

    N_3203 = crear_cartilla("N° ", {
        "B": [11,3,12,4,2],
        "I": [29,22,16,23,20],
        "N": [43,34,40,41],
        "G": [56,54,46,47,55],
        "O": [62,67,74,68,75]
    })

    N_3202 = crear_cartilla("N° ", {
        "B": [6,13,4,10,11],
        "I": [17,22,29,23,27],
        "N": [36,41,34,33],
        "G": [49,47,53,48,54],
        "O": [72,65,73,66,71]
    })

    N_3201 = crear_cartilla("N° ", {
        "B": [15,7,5,12,6],
        "I": [21,28,19,25,26],
        "N": [44,38,45,42],
        "G": [56,48,49,47,53],
        "O": [67,75,65,72,66]
    })

    N_3199 = crear_cartilla("N° ", {
        "B": [10,4,1,13,3],
        "I": [26,24,16,25,17],
        "N": [33,43,40,34],
        "G": [49,56,54,46,47],
        "O": [74,72,65,73,66]
    })

    
    

#--------------------------------------------------------------------------------------------------------------------
#                                                      CREAR USUARIOS
#--------------------------------------------------------------------------------------------------------------------

    # EJEMPLO: crear_usuario("nombre_usuario", "contraseña_usuario", [nombre_cartilla_1, nombre_cartilla_2, ...])
    # crear_usuario("", "", [])

    crear_usuario("admin", "JDVL0509.", [N_1596,N_1597,N_1598,N_1599,N_1600,N_1601,N_1602,N_1603,N_1604,N_1605,N_2719,N_2720,N_2721,N_2722,N_2723,N_2724,N_2725,N_2726,N_2727,N_2728,N_2729,N_2730,N_2731,N_2732,N_2733])

    crear_usuario("Sori2024", "Sori2024",[N_3468,N_3469,N_3470,N_3471,N_3472,N_3473,N_3474,N_3475,N_3476,N_3477,N_3478,N_3479,N_3480,N_3481,N_3482])

    crear_usuario("Elca011079", "27677359", [N_0720,N_0721,N_0722,N_0723,N_0724,N_0725,N_0726,N_0727,N_0729,N_0731,N_0732,N_0733,N_0734])

    crear_usuario("Ariana", "Ariana1827", [N_2899,N_2900,N_2901,N_2902,N_2903,N_2904,N_2905,N_2906,N_2907,N_2908,N_2909,N_2910,N_2911,N_2912,N_2913])

    crear_usuario("fernando solis", "29483344", [N_0090,N_0091,N_0092,N_0093,N_0094,N_0095,N_0096,N_0097,N_0098,N_0099,N_0100,N_0101,N_0102,N_0103,N_0104])

    crear_usuario("feliroman", "ADRI2016", [N_0346,N_0359,N_0357,N_0358,N_0356,N_0355,N_0354,N_0353,N_0352,N_0351,N_0350,N_0349,N_0348,N_0345,N_0347])

    crear_usuario("Nancy2024", "Mica29", [N_3198,N_3197,N_3196,N_3195,N_3190,N_3191,N_3192,N_3193,N_3194,N_3200,N_3204,N_3203,N_3202,N_3201,N_3199])
    return app
    

if __name__ == "__main__":

    app=crear_app()

#  Ejecutar Bingo-Web
    app.run(debug=True)