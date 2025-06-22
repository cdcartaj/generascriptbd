
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import io, json, logging, time, os
from pathlib import Path

# Se setea el log
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'procesador/index.html')

def generar_sql_pc9_pie_amount_preview(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        #Se recupera la extensión del archivo.
        extension = os.path.splitext(archivo.name)[1].lower()
        
        #Por defecto toma la tabla pc9_pie_amount. Si no se ingresa el nombre.
        nombre_tabla = request.POST.get('tabla', 'pc9_pie_amount')

        logger.info(f"Procesando archivo para tabla: {nombre_tabla}")
        logger.info(f"Nombre del archivo recibido: {archivo.name}")
        
        try:
            
            # Cargar el mapeo desde el JSON
            config_path = Path(__file__).resolve().parent.parent / 'pc9_pie_amount.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                mapeo_columnas = json.load(f)

            #Se verifica el tiempo de carga del archivo.
            start = time.time()
            
            # Detectar y leer según tipo
            if extension == '.csv':
                #decimal=',' permite cambiar la coma a punto para el decimal.
                df = pd.read_csv(archivo, sep=';', decimal=',', keep_default_na=False)  # <-- CSV más rápido
            elif extension == '.xlsx':
                #Se lee el archivo, optimizando la con openpyxl (archivos .xlsx) y 
                #que pandas conserve los textos "NA" tal como están (como texto), y no lo reemplace por NaN
                #Pensando que es un "NA", "NaN", "null".
                df = pd.read_excel(archivo, engine="openpyxl", keep_default_na=False)
            else:
                return HttpResponse("Formato no soportado. Usa .csv o .xlsx", status=400)
            
            
            logger.info(f"Tiempo lectura Excel: {time.time() - start :.2f} segundos")
            logger.info(f"Columnas encontradas en {archivo.name}: {list(df.columns)}")
            
            # Verifica que todas las columnas del Excel estén mapeadas
            logger.info(f"Archivo JSON recuperado: {config_path}")
            columnas_excel = df.columns
            columnas_sql = []
            for col in columnas_excel:
                #logger.info(f"Columna buscada: {col}")
                if col not in mapeo_columnas:
                    return HttpResponse(f'Falta mapeo para la columna "{col}" en columnas_map.json', status=400)
                columnas_sql.append(mapeo_columnas[col])

            #logger.info(f"Columnas SQL mapeadas: {columnas_sql}")
            
            contenido = io.StringIO()
            for _, row in df.iterrows():
                #logger.info(f"Row: {row}")
                columnas_str = ', '.join([f'{col}' for col in columnas_sql])
                #logger.info(f"Columnas_str: {columnas_str}")
                valores = []
                
                for col, valor in zip(df.columns, row):
                    #logger.info(f"Proceso {col}: {valor}")
                    #Campos con formato fecha (to_date)
                    if col == 'EFFECTIVE DATE' or col == 'EXPIRATION DATE':
                        valor_formateado = f"TO_DATE('{valor}','YYYY-MM-DD HH24:MI:SS')"
                        valores.append(valor_formateado)
                    #Campos con formato numérico decimal redondeado a 4 dígitos.    
                    elif col == 'PVP s/IVA':
                        #logger.info(f"Valor: {valor}")
                        valores.append(f"{valor}")
                    #Campos de tipo String.
                    else:
                        valores.append(f"'{valor}'")
                #logger.info(f"Valores generados: {valores}")
                valores_str = ', '.join(valores)
                sql = f'INSERT INTO {nombre_tabla} ({columnas_str}) VALUES ({valores_str});\n'
                contenido.write(sql)


            logger.info(f"Generación de SQL finalizada. Total filas: {len(df)}")

            resultado_sql = contenido.getvalue()
            return render(request, 'procesador/resultado_sql.html', {
                'sql_generado': resultado_sql,
                'nombre_tabla': nombre_tabla
            })

        except Exception as e:
            logger.exception("Ocurrió un error procesando el archivo Excel")
            return HttpResponse(f"Error al procesar archivo: {e}", status=500)

    return render(request, 'procesador/form_excel_preview.html')

def generar_sql_pc9_pie_amount_descarga(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        #Se recupera la extensión del archivo.
        extension = os.path.splitext(archivo.name)[1].lower()
        
        #Por defecto toma la tabla pc9_pie_amount. Si no se ingresa el nombre.
        nombre_tabla = request.POST.get('tabla', 'pc9_pie_amount')

        logger.info(f"Procesando archivo para tabla: {nombre_tabla}")
        logger.info(f"Nombre del archivo recibido: {archivo.name}")
        
        try:
            
            # Cargar el mapeo desde el JSON
            config_path = Path(__file__).resolve().parent.parent / 'pc9_pie_amount.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                mapeo_columnas = json.load(f)

            #Se verifica el tiempo de carga del archivo.
            start = time.time()
            
            # Detectar y leer según tipo
            if extension == '.csv':
                #decimal=',' permite cambiar la coma a punto para el decimal.
                df = pd.read_csv(archivo, sep=';', decimal=',', keep_default_na=False)  # <-- CSV más rápido
            elif extension == '.xlsx':
                #Se lee el archivo, optimizando la con openpyxl (archivos .xlsx) y 
                #que pandas conserve los textos "NA" tal como están (como texto), y no lo reemplace por NaN
                #Pensando que es un "NA", "NaN", "null".
                df = pd.read_excel(archivo, engine="openpyxl", keep_default_na=False)
            else:
                return HttpResponse("Formato no soportado. Usa .csv o .xlsx", status=400)
            
            
            logger.info(f"Tiempo lectura Excel: {time.time() - start :.2f} segundos")
            logger.info(f"Columnas encontradas en {archivo.name}: {list(df.columns)}")
            
            # Verifica que todas las columnas del Excel estén mapeadas
            logger.info(f"Archivo JSON recuperado: {config_path}")
            columnas_excel = df.columns
            columnas_sql = []
            for col in columnas_excel:
                #logger.info(f"Columna buscada: {col}")
                if col not in mapeo_columnas:
                    return HttpResponse(f'Falta mapeo para la columna "{col}" en columnas_map.json', status=400)
                columnas_sql.append(mapeo_columnas[col])

            #logger.info(f"Columnas SQL mapeadas: {columnas_sql}")
            
            contenido = io.StringIO()
            for _, row in df.iterrows():
                #logger.info(f"Row: {row}")
                columnas_str = ', '.join([f'{col}' for col in columnas_sql])
                #logger.info(f"Columnas_str: {columnas_str}")
                valores = []
                
                for col, valor in zip(df.columns, row):
                    #logger.info(f"Proceso {col}: {valor}")
                    #Campos con formato fecha (to_date)
                    if col == 'EFFECTIVE DATE' or col == 'EXPIRATION DATE':
                        valor_formateado = f"TO_DATE('{valor}','YYYY-MM-DD HH24:MI:SS')"
                        valores.append(valor_formateado)
                    #Campos con formato numérico decimal redondeado a 4 dígitos.    
                    elif col == 'PVP s/IVA':
                        #logger.info(f"Valor: {valor}")
                        valores.append(f"{valor}")
                    #Campos de tipo String.
                    else:
                        valores.append(f"'{valor}'")
                #logger.info(f"Valores generados: {valores}")
                valores_str = ', '.join(valores)
                sql = f'INSERT INTO {nombre_tabla} ({columnas_str}) VALUES ({valores_str});\n'
                contenido.write(sql)


            logger.info(f"Generación de SQL finalizada. Total filas: {len(df)}")

            response = HttpResponse(contenido.getvalue(), content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{nombre_tabla}_insert.sql"'
            return response

        except Exception as e:
            logger.exception("Ocurrió un error procesando el archivo Excel")
            return HttpResponse(f"Error al procesar archivo: {e}", status=500)

    return render(request, 'procesador/form_excel_descarga.html')
