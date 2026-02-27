import csv
import os

class FileManager:
    """
    Clase responsable de gestionar la lectura y escritura de archivos CSV.
    Actúa como la capa de persistencia física de la base de datos.
    """

    def __init__(self, data_dir="data"):
        """
        Inicializa el gestor de archivos.
        Detecta la ruta absoluta para evitar errores de 'File Not Found'.
        
        Args:
            data_dir (str): Nombre del directorio donde se guardan los .csv
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)        
        self.data_dir = os.path.join(project_root, data_dir)
        
        # Verificación de seguridad
        if not os.path.exists(self.data_dir):
            # Si no existe, intentamos crearla (o lanzar advertencia)
            os.makedirs(self.data_dir)
            print(f"Advertencia: Se creó la carpeta de datos en {self.data_dir}")

    def _get_filepath(self, filename):
        """
        Construye la ruta completa del archivo.
        Ejemplo: 'data' + 'estudiantes' -> 'data/estudiantes.csv'
        """
        return os.path.join(self.data_dir, f"{filename}.csv")

    def _parse_record(self, row):
        """
        Convierte los strings del CSV a tipos de datos reales de Python (int, float, None).
        Simula el sistema de tipos de un motor SQL.

        Args:
            row (dict): Diccionario con valores en formato string.
        Returns:
            dict: Diccionario con valores convertidos (int, float, None).
        """
        parsed_record = {}
        
        # Definición manual del esquema (Schema)
        # En una DB real, esto se define al crear la tabla.
        integer_fields = ['id', 'creditos', 'id_matricula', 'estudiante_id']
        float_fields = ['nota_final']

        for key, value in row.items():
            # Manejo de valores nulos (NULL)
            if value is None or value == "":
                parsed_record[key] = None
            elif key in integer_fields:
                parsed_record[key] = int(value)
            elif key in float_fields:
                parsed_record[key] = float(value)
            else:
                # Si no es número ni nulo, se queda como string (VARCHAR)
                parsed_record[key] = value
                
        return parsed_record

    def read_all(self, filename):
        """
        Lee todo el contenido de una 'tabla' (archivo CSV).
        
        Args:
            filename (str): Nombre del archivo (sin extensión).
        Returns:
            list[dict]: Lista de registros procesados.
        """
        file_path = self._get_filepath(filename)
        
        if not os.path.exists(file_path):
            return []

        data = []
        try:
            with open(file_path, mode='r', encoding='utf-8') as csv_file:
                # DictReader usa la primera fila como llaves (keys)
                reader = csv.DictReader(csv_file)
                for row in reader:
                    # Procesamos cada fila para corregir los tipos de datos
                    data.append(self._parse_record(row))
            return data
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return []

    def append_record(self, filename, new_record):
        """
        Inserta un nuevo registro al final del archivo (INSERT).
        
        Args:
            filename (str): Nombre del archivo destino.
            new_record (dict): Diccionario con los datos a guardar.
        """
        file_path = self._get_filepath(filename)
        file_exists = os.path.exists(file_path)

        try:
            # mode='a' significa Append (agregar al final)
            # newline='' es obligatorio en Windows para evitar líneas en blanco
            with open(file_path, mode='a', encoding='utf-8', newline='') as csv_file:
                fieldnames = list(new_record.keys())
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                # Si el archivo es nuevo, escribimos primero los encabezados
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(new_record)
                return True
        except Exception as e:
            print(f"Error writing to {filename}: {e}")
            return False

# --- Bloque de Prueba (Unit Test básico) ---
if __name__ == "__main__":
    # Instanciamos la clase
    db = FileManager()
    
    # Prueba de lectura
    print("--- Testing Read Operation ---")
    students = db.read_all("estudiantes")
    for student in students:
        print(student) 
        # Observa que 'semestre' es int, no string.

    

    # Prueba de escritura
    print("\n--- Testing Write Operation ---")
    new_enrollment = {
        "id_matricula": 100, 
        "estudiante_id": 1001, 
        "curso_codigo": "HUM001", 
        "semestre": "2024-2", 
        "nota_final": "" # Simulando NULL
    }
    
    if db.append_record("matriculas", new_enrollment):
        print("Record successfully added.")
    