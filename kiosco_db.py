import sqlite3
import os

DB_NAME = "kiosco.db"

def conectar_db():
    """Establece conexión con la base de datos SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_base_de_datos():
    """Crea las tablas si no existen en el archivo .db"""
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Tabla de productos (Corazón del kiosco)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio_venta REAL NOT NULL,
        stock_actual INTEGER DEFAULT 0
    )
    """)
    
    # Tabla de ventas (Historial de caja)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
        id_producto TEXT,
        cantidad INTEGER NOT NULL,
        fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_producto) REFERENCES productos(id)
    )
    """)
    
    conexion.commit()
    conexion.close()

def registrar_producto_nuevo():
    print("\n--- REGISTRAR PRODUCTO NUEVO ---")
    id_prod = input("Escanee o ingrese el código de barras: ").strip()
    nombre = input("Nombre/Descripción del producto: ").strip()
    
    try:
        precio = float(input("Precio de venta al público: "))
        stock_inicial = int(input("Stock inicial disponible: "))
    except ValueError:
        print("❌ Error: Precio o Stock inválidos. Deben ser números.")
        return

    conexion = conectar_db()
    cursor = conexion.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO productos (id, nombre, precio_venta, stock_actual)
            VALUES (?, ?, ?, ?)
        """, (id_prod, nombre, precio, stock_inicial))
        
        conexion.commit()
        print("✅ Producto registrado exitosamente en la base de datos.")
    except sqlite3.IntegrityError:
        print("❌ Error: Ese código de barras ya está asignado a otro producto.")
    finally:
        conexion.close()

def mostrar_inventario():
    print("\n--- INVENTARIO ACTUAL (DESDE BASE DE DATOS) ---")
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id, nombre, stock_actual, precio_venta FROM productos")
    productos = cursor.fetchall()
    
    conexion.close()
    
    if not productos:
        print("La base de datos está vacía.")
        return

    print(f"{'Código/ID':<15} | {'Nombre':<25} | {'Stock':<6} | {'Precio':<10}")
    print("-" * 65)
    for p in productos:
        print(f"{p[0]:<15} | {p[1]:<25} | {p[2]:<6} | ${p[3]:<10.2f}")

def registrar_venta():
    print("\n--- PASAR PRODUCTO POR LECTORA (VENTA) ---")
    id_prod = input("Escanee el código de barras: ").strip()
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT nombre, precio_venta, stock_actual FROM productos WHERE id = ?", (id_prod,))
    producto = cursor.fetchone()
    
    if producto is None:
        print("❌ ERROR: ¡Producto NO encontrado en la base de datos! El precio no existe.")
        conexion.close()
        return
        
    nombre, precio, stock_actual = producto
    print(f"🔍 [LECTORA]: {nombre} | Precio: ${precio:.2f} | Stock disponible: {stock_actual}")
    
    if stock_actual <= 0:
        print("❌ No se puede vender: ¡Stock agotado!")
        conexion.close()
        return
        
    try:
        cant_a_vender = int(input(f"¿Cuántas unidades de '{nombre}' lleva?: "))
    except ValueError:
        print("❌ Error: Ingrese un número entero válido.")
        conexion.close()
        return
    
    if cant_a_vender > stock_actual:
        print(f"❌ Error: No podés vender {cant_a_vender}. Solo quedan {stock_actual} en estantería.")
        conexion.close()
        return

    cursor.execute("""
        UPDATE productos 
        SET stock_actual = stock_actual - ? 
        WHERE id = ?
    """, (cant_a_vender, id_prod))
    
    cursor.execute("""
        INSERT INTO ventas (id_producto, cantidad) 
        VALUES (?, ?)
    """, (id_prod, cant_a_vender))
    
    conexion.commit()
    conexion.close()
    
    total = cant_a_vender * precio
    print(f"✅ Venta cobrada con éxito. Total: ${total:.2f}. Stock actualizado.")

def actualizar_precio_producto():
    print("\n--- ACTUALIZAR PRECIO DE PRODUCTO ---")
    id_prod = input("Escanee o ingrese el código de barras del producto: ").strip()
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT nombre, precio_venta FROM productos WHERE id = ?", (id_prod,))
    producto = cursor.fetchone()
    
    if producto is None:
        print("❌ Error: El producto no existe en la base de datos.")
        conexion.close()
        return
        
    nombre, precio_actual = producto
    print(f"📦 Producto encontrado: {nombre}")
    print(f"💰 Precio actual: ${precio_actual:.2f}")
    
    try:
        nuevo_precio = float(input("Ingrese el NUEVO precio de venta: "))
        if nuevo_precio <= 0:
            print("❌ El precio debe ser mayor a cero.")
            conexion.close()
            return
            
        cursor.execute("UPDATE productos SET precio_venta = ? WHERE id = ?", (nuevo_precio, id_prod))
        conexion.commit()
        print(f"✅ ¡Precio actualizado! '{nombre}' ahora cuesta ${nuevo_precio:.2f}.")
    except ValueError:
        print("❌ Error: Ingrese un número válido para el precio.")
    finally:
        conexion.close()

def menu_principal():
    inicializar_base_de_datos()
    while True:
        print("\n==================================")
        print("  SISTEMA KIOSCO - MOTOR SQLITE3 ")
        print("==================================")
        print("1. Ver inventario completo")
        print("2. Registrar producto nuevo")
        print("3. Cobrar / Escanear venta")
        print("4. Actualizar precio de un producto")
        print("5. Salir")
        
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == "1":
            mostrar_inventario()
        elif opcion == "2":
            registrar_producto_nuevo()
        elif opcion == "3":
            registrar_venta()
        elif opcion == "4":
            actualizar_precio_producto()
        elif opcion == "5":
            print("Cerrando el sistema del kiosco...")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu_principal()