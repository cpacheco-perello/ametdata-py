def get_relativedelta():
    try:
        from dateutil.relativedelta import relativedelta
        return relativedelta
    except ImportError:
        raise ImportError("Falta el paquete 'python-dateutil'. Instálalo con 'pip install python-dateutil'.")
import asyncio
import io
import tarfile

import httpx


MAX_CICLOS = 3


class AemetError(Exception):
    """Excepción personalizada para errores de AEMET."""
    pass


async def fetch_json_url(url: str, descripcion: str | None = None):
    """Descarga un JSON desde una URL y lo devuelve como dict/list.

    Args:
        url: URL del recurso JSON.
        descripcion: Texto opcional para contextualizar errores.

    Raises:
        AemetError: Si la descarga falla o el contenido no es JSON.
    """
    contexto = f" ({descripcion})" if descripcion else ""
    print(f"📥 Descargando JSON{contexto} desde: {url}")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=30)
            resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise AemetError(f"Error descargando JSON{contexto}: {exc}")
    
    
    return resp.json()




async def fetch_con_reintentos_endpoint_aemet(url_template: str, tipo: str, api_keys: list[str]):
    print("Accediendo Base datos AEMET")
    ciclos_completados = 0

    while ciclos_completados < MAX_CICLOS:
        print(f"🔄 Ciclo {ciclos_completados + 1} de {MAX_CICLOS}")

        for key_index, api_key in enumerate(api_keys):
            endpoint = url_template.replace("{apiKey}", api_key)
            print(f"Probando endpoint: {endpoint}")

            async with httpx.AsyncClient() as client:
                try:
                    resp = await client.get(endpoint, timeout=10)
                    resp.raise_for_status()

                    if "application/json" not in resp.headers.get("Content-Type", ""):
                        print(f"❗ Respuesta inesperada (no JSON) con la clave {key_index + 1}: {resp.text[:200]}")
                        continue

                    try:
                        data = resp.json()
                    except Exception as decode_error:
                        print(f"❗ Error decodificando JSON con la clave {key_index + 1}. Primeros 200 chars: {resp.text[:200]}")
                        raise decode_error

                    print(f"✔️ Datos obtenidos con la clave {key_index + 1}.")
                    return data

                except httpx.HTTPStatusError as exc:
                    print(f"❗ Falló con la clave {key_index + 1} ({tipo}): {exc.response.status_code}")
                except Exception as e:
                    print(f"❗ Error con la clave {key_index + 1} ({tipo}): {e}")

                espera = min(1 * (2 ** key_index), 30)
                print(f"⏳ Esperando {espera} segundos antes de probar la siguiente clave...")
                await asyncio.sleep(espera)

        ciclos_completados += 1
        print(f"➡️ Terminó ciclo {ciclos_completados}.")

    raise AemetError(f"No se pudo realizar la solicitud tras {MAX_CICLOS} ciclos.")


async def descargar_archivo_tar_gz(url: str) -> dict:
    """Descarga un archivo desde una URL y extrae su contenido.
    
    Soporta formatos: tar.gz, tar.bz2, zip y arquivos simples.
    
    Args:
        url: URL del archivo.
        
    Returns:
        dict: Diccionario con los archivos extraídos {nombre_archivo: contenido}.
        
    Raises:
        AemetError: Si hay error descargando o extrayendo el archivo.
    """
    import zipfile
    
    print(f"📥 Descargando archivo desde: {url}")
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=30)
            resp.raise_for_status()
            
            print(f"✔️ Archivo descargado ({len(resp.content)} bytes)")
            
            # Detectar el formato por magic bytes
            content = resp.content
            magic_bytes = content[:4]
            
            files_content = {}
            
            # Intentar como tar.gz
            if magic_bytes[:2] == b'\x1f\x8b':  # gzip magic
                print("📦 Formato detectado: tar.gz")
                try:
                    tar_bytes = io.BytesIO(content)
                    with tarfile.open(fileobj=tar_bytes, mode='r:gz') as tar:
                        for member in tar.getmembers():
                            if member.isfile():
                                f = tar.extractfile(member)
                                if f:
                                    try:
                                        files_content[member.name] = f.read().decode('utf-8')
                                    except UnicodeDecodeError:
                                        files_content[member.name] = f.read().hex()
                                    print(f"📄 Extraído: {member.name}")
                        return files_content
                except Exception as e:
                    print(f"⚠️ Fallo con tar.gz: {e}")
            
            # Intentar como tar.bz2
            elif magic_bytes[:3] == b'BZh':  # bzip2 magic
                print("📦 Formato detectado: tar.bz2")
                try:
                    tar_bytes = io.BytesIO(content)
                    with tarfile.open(fileobj=tar_bytes, mode='r:bz2') as tar:
                        for member in tar.getmembers():
                            if member.isfile():
                                f = tar.extractfile(member)
                                if f:
                                    try:
                                        files_content[member.name] = f.read().decode('utf-8')
                                    except UnicodeDecodeError:
                                        files_content[member.name] = f.read().hex()
                                    print(f"📄 Extraído: {member.name}")
                        return files_content
                except Exception as e:
                    print(f"⚠️ Fallo con tar.bz2: {e}")
            
            # Intentar como ZIP
            elif magic_bytes[:2] == b'PK':  # ZIP magic
                print("📦 Formato detectado: ZIP")
                try:
                    zip_bytes = io.BytesIO(content)
                    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
                        for info in zip_ref.infolist():
                            if not info.is_dir():
                                try:
                                    files_content[info.filename] = zip_ref.read(info).decode('utf-8')
                                except UnicodeDecodeError:
                                    files_content[info.filename] = zip_ref.read(info).hex()
                                print(f"📄 Extraído: {info.filename}")
                        return files_content
                except Exception as e:
                    print(f"⚠️ Fallo con ZIP: {e}")
            
            # Si no es ninguno de los anteriores, intentar como tar simple
            elif magic_bytes[:6] == b'ustar\x00' or content[:256].find(b'ustar') != -1:
                print("📦 Formato detectado: tar")
                try:
                    tar_bytes = io.BytesIO(content)
                    with tarfile.open(fileobj=tar_bytes, mode='r') as tar:
                        for member in tar.getmembers():
                            if member.isfile():
                                f = tar.extractfile(member)
                                if f:
                                    try:
                                        files_content[member.name] = f.read().decode('utf-8')
                                    except UnicodeDecodeError:
                                        files_content[member.name] = f.read().hex()
                                    print(f"📄 Extraído: {member.name}")
                        return files_content
                except Exception as e:
                    print(f"⚠️ Fallo con tar: {e}")
            
            # Si no es un archivo comprimido, devolverlo como un archivo
            print(f"📦 Formato desconocido, se devuelve como contenido directo")
            filename = url.split('/')[-1] or "descargado"
            try:
                files_content[filename] = content.decode('utf-8')
            except UnicodeDecodeError:
                files_content[filename] = content.hex()
            print(f"📄 Contenido: {filename}")
            return files_content
                    
    except httpx.HTTPError as http_error:
        raise AemetError(f"Error descargando archivo: {http_error}")

