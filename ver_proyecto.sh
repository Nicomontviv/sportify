#!/bin/bash

# Nombre del archivo: ver_proyecto.sh
ARCHIVO_SALIDA="estructura_proyecto.txt"

# Verificar si el comando 'tree' está instalado
if ! command -v tree &> /dev/null
then
    echo "⚠️  El comando 'tree' no está instalado. Usando alternativa con 'find'..."
    
    # Encabezado del archivo txt
    echo "====================================================================" > "$ARCHIVO_SALIDA"
    echo "📁 ESTRUCTURA DEL PROYECTO (Generada con find)" >> "$ARCHIVO_SALIDA"
    echo "Fecha: $(date)" >> "$ARCHIVO_SALIDA"
    echo "====================================================================" >> "$ARCHIVO_SALIDA"
    
    # Buscar archivos y guardarlos ordenados en el txt
    find . -maxdepth 4 \
        -not -path '*/.*' \
        -not -path '*node_modules*' \
        -not -path '*__pycache__*' \
        -not -path '*venv*' \
        -not -path '*instance*' \
        | sort >> "$ARCHIVO_SALIDA"
    
    echo "====================================================================" >> "$ARCHIVO_SALIDA"
else
    echo "🌲 Generando estructura ordenada con 'tree'..."
    
    # Encabezado del archivo txt
    echo "====================================================================" > "$ARCHIVO_SALIDA"
    echo "🌲 ESTRUCTURA DEL PROYECTO" >> "$ARCHIVO_SALIDA"
    echo "Fecha: $(date)" >> "$ARCHIVO_SALIDA"
    echo "====================================================================" >> "$ARCHIVO_SALIDA"
    
    # Ejecutar tree, ignorar carpetas pesadas y guardar en el txt
    tree -I 'node_modules|.git|__pycache__|venv|.pytest_cache|instance|.DS_Store' --dirsfirst >> "$ARCHIVO_SALIDA"
    
    echo "====================================================================" >> "$ARCHIVO_SALIDA"
fi

echo "✅ ¡Listo! Se ha generado el archivo '$ARCHIVO_SALIDA' con la información del proyecto."
echo "📝 Podés abrir ese archivo, copiar su contenido y pegarlo acá para que pueda verlo."
echo "===================================================================="