from src.services.categorizador import obtener_categoria

sigue_bucle = True

test_cases = [
    ("mercadona", "Supermercado"),
    ("carrefour", "Supermercado"),
    ("netflix", "Suscripciones"),
    ("spotify", "Suscripciones"),
    ("uber", "Transporte"),
    ("repsol", "Transporte"),
    ("cafeteria", "Hostelería"),
    ("bar", "Hostelería"),
    ("farmacia", "Salud/Deporte"),
    ("gimnasio", "Salud/Deporte"),
    ("hotel eurostars", "Hostelería"),
    ("zara compra online", "Ropa/Calzado"),
    ("matricula universidad complutense", "Educación"),
    ("corte ingles camiseta deportiva", "Ropa/Calzado"),
    ("bbva comision mantenimiento", "Gastos Financieros"),
    ("renfe billete madrid", "Viajes"),
    ("veterinario sanos y felices", "Mascotas"),
    ("hacienda impuesto renta", "Impuestos/Administración"),
    ("caritas donacion mensual", "Donaciones/ONG"),
    ("peluquería canina reyes", "Belleza/Estética"),
    ("fontanero arreglo lavabo", "Mantenimiento/Reparaciones"),
    ("mediamarkt televisor led", "Electrónica/Informática"),
    ("amazon compra libros", "Electrónica/Informática"),
    ("cine nocturno", "Ocio"),
    ("museo nacional entrada", "Cultura"),
    ("factura luz endesa", "Hogar/Servicios"),
    ("videojuego steam", "Ocio"),
    ("suscripción google one", "Suscripciones"),
    ("expedia vuelo barcelona", "Viajes"),
    ("Cepsa pago gasóleo", "Transporte"),
    ("bizum comida 5 septiembre", "Hostelería"),
    ("salir")
]

while sigue_bucle:
    entrada = input("Introduce el nombre de la transacción que quieras interpretar: ")
    if entrada == "salir":
        sigue_bucle = False

    else:
        salida = obtener_categoria(entrada)
        print(salida)