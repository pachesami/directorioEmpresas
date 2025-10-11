"""
Extrae imágenes de Excel (.xlsx) usando zipfile
Ejecutar: python extract_images_zip.py archivo.xlsx
"""
import sys
import zipfile
import shutil
from pathlib import Path

def extract_images_from_excel(xlsx_path, output_dir='extracted_logos'):
    """Extrae todas las imágenes del archivo Excel"""
    
    xlsx_path = Path(xlsx_path)
    
    # Validar que existe el archivo
    if not xlsx_path.exists():
        print(f"❌ ERROR: No existe el archivo {xlsx_path}")
        return False
    
    # Crear carpeta de salida
    output_path = Path(output_dir)
    if output_path.exists():
        print(f"🗑️  Limpiando carpeta anterior: {output_dir}/")
        shutil.rmtree(output_path)
    
    output_path.mkdir(exist_ok=True)
    
    print(f"📂 Abriendo: {xlsx_path.name}")
    print(f"📁 Extrayendo a: {output_path.absolute()}\n")
    
    try:
        # Abrir Excel como ZIP
        with zipfile.ZipFile(xlsx_path, 'r') as zip_ref:
            # Listar todos los archivos del ZIP
            all_files = zip_ref.namelist()
            
            # Buscar archivos de imágenes en xl/media/
            image_files = [f for f in all_files if f.startswith('xl/media/')]
            
            if not image_files:
                # Buscar en cualquier carpeta que contenga 'media'
                image_files = [f for f in all_files if '/media/' in f.lower()]
            
            if not image_files:
                # Buscar por extensión
                extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.emf', '.wmf')
                image_files = [f for f in all_files if f.lower().endswith(extensions)]
            
            if not image_files:
                print("❌ ERROR: No se encontraron imágenes en el archivo Excel")
                print("\n📋 Contenido del archivo Excel:")
                for f in sorted(all_files)[:30]:
                    print(f"   {f}")
                return False
            
            print(f"✅ Encontradas {len(image_files)} imágenes\n")
            
            # Extraer cada imagen
            extracted = 0
            for idx, img_path in enumerate(sorted(image_files), 1):
                try:
                    # Obtener extensión
                    ext = Path(img_path).suffix.lower() or '.png'
                    
                    # Nombre de salida: imagen_001.png, imagen_002.png, etc.
                    output_filename = f"imagen_{idx:03d}{ext}"
                    output_filepath = output_path / output_filename
                    
                    # Extraer archivo
                    with zip_ref.open(img_path) as source:
                        with open(output_filepath, 'wb') as target:
                            shutil.copyfileobj(source, target)
                    
                    # Verificar que se extrajo correctamente
                    size_kb = output_filepath.stat().st_size / 1024
                    print(f"  ✓ {output_filename} ({size_kb:.1f} KB)")
                    extracted += 1
                    
                except Exception as e:
                    print(f"  ✗ Error en {img_path}: {e}")
            
            print(f"\n🎉 Éxito: {extracted} imágenes extraídas en {output_path.absolute()}")
            return True
            
    except zipfile.BadZipFile:
        print("❌ ERROR: El archivo no es un Excel válido (.xlsx)")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("=" * 60)
        print("📌 USO:")
        print("   python extract_images_zip.py archivo.xlsx")
        print("\n📌 EJEMPLO:")
        print("   python extract_images_zip.py empresas.xlsx")
        print("=" * 60)
        sys.exit(1)
    
    success = extract_images_from_excel(sys.argv[1])
    sys.exit(0 if success else 1)