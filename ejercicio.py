import os
from decimal import Decimal, InvalidOperation
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # lee el archivo .env y deja sus datos disponibles para os.getenv()

conexion = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    use_pure=True,  # Usa el conector en Python; evita el fallo de la extensión nativa.
)
cursor = conexion.cursor(dictionary=True)  # cada fila llega como un diccionario


def mostrar(libros):
    """Enseña una lista de libros, uno por línea."""
    if not libros:
        print("No hay libros que mostrar.")
    for libro in libros:
        print(
            libro["id"], "|", libro["titulo"], "|", libro["autor"], "|",
            libro["categoria"], "|", libro["precio"], "€ | stock:", libro["stock"],
        )


def ver_libros():
    cursor.execute("SELECT * FROM libros ORDER BY precio DESC")
    mostrar(cursor.fetchall())


def buscar_por_autor():
    autor = input("Introduce el autor: ")
    cursor.execute(
        "SELECT * FROM libros WHERE autor = %s",
        (autor,)
    )
    mostrar(cursor.fetchall())


def stock_bajo():
    limite = int(input("Mostrar libros con stock inferior a: "))
    cursor.execute(
        "SELECT * FROM libros WHERE stock < %s ORDER BY stock ASC",
        (limite,)
    )
    mostrar(cursor.fetchall())


def vender():
    try:
        libro_id = int(input("ID del libro: "))
        cantidad = int(input("Cantidad de ejemplares: "))
    except ValueError:
        print("Debes introducir números enteros.")
        return

    if cantidad <= 0:
        print("La cantidad debe ser mayor que cero.")
        return

    cursor.execute(
        "SELECT * FROM libros WHERE id = %s",
        (libro_id,)
    )
    libro = cursor.fetchone()

    if libro is None:
        print("El libro no existe.")
        return

    if cantidad > libro["stock"]:
        print(f'Stock insuficiente. Quedan {libro["stock"]} ejemplares.')
        return

    cursor.execute(
        "UPDATE libros SET stock = stock - %s WHERE id = %s",
        (cantidad, libro_id)
    )
    conexion.commit()

    total = libro["precio"] * cantidad
    print(f"Venta realizada. Total a cobrar: {total:.2f} €")


def anadir_libro():
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()
    categoria = input("Categoría: ").strip()

    if not titulo or not autor or not categoria:
        print("El título, autor y categoría son obligatorios.")
        return

    try:
        precio = Decimal(input("Precio: ").replace(",", "."))
        stock = int(input("Stock: "))
    except (InvalidOperation, ValueError):
        print("Introduce un precio válido y un stock entero.")
        return

    if not precio.is_finite() or precio < 0 or stock < 0:
        print("El precio y el stock deben ser números no negativos.")
        return

    cursor.execute(
        """
        INSERT INTO libros (titulo, autor, categoria, precio, stock)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (titulo, autor, categoria, precio, stock)
    )
    conexion.commit()

    print(f"Libro añadido con ID: {cursor.lastrowid}")


while True:
    print()
    print("1. Ver libros")
    print("2. Buscar por autor")
    print("3. Stock bajo")
    print("4. Vender")
    print("5. Añadir libro")
    print("0. Salir")
    opcion = input("Elige una opción: ")
    print()

    if opcion == "1":
        ver_libros()
    elif opcion == "2":
        buscar_por_autor()
    elif opcion == "3":
        stock_bajo()
    elif opcion == "4":
        vender()
    elif opcion == "5":
        anadir_libro()
    elif opcion == "0":
        break
    else:
        print("Esa opción no existe.")

cursor.close()
conexion.close()
