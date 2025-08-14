# Generador de Autómatas Finitos No Deterministas (AFN) para Expresiones Regulares

## 📹 Video demostrativo

[![Video de YouTube](https://img.youtube.com/vi/hMfBXDaeyiI/0.jpg)](https://youtu.be/YVup0Z4JT1E)

---

Este proyecto implementa un generador y visualizador de autómatas finitos no deterministas (AFN) a partir de expresiones regulares, usando el algoritmo de Thompson y visualización con matplotlib. El código está organizado en los siguientes módulos:

- **regex_tools.py**: Convierte expresiones regulares infijas a notación postfija (RPN), insertando concatenaciones explícitas y manejando precedencias de operadores.
- **nfa_core.py**: Implementa el algoritmo de Thompson para construir un AFN desde la expresión postfija. Define las clases `State` y `Frag` para representar estados y fragmentos del autómata, y funciones para simular el autómata y verificar aceptación de cadenas.
- **draw_ortho.py**: Dibuja el autómata generado usando matplotlib, mostrando los estados, transiciones y diferenciando visualmente los símbolos y las transiciones epsilon.
- **main.py**: Orquesta el proceso: lee expresiones regulares desde un archivo (`regex_p1.txt`), las convierte a postfijo, genera el AFN, lo renumera y lo dibuja. Permite probar cadenas en el autómata generado.
- **regex_p1.txt**: Archivo de entrada con expresiones regulares, una por línea.

## 📋 Descripción

El proyecto implementa el algoritmo de Thompson para construir AFNs desde expresiones regulares, con visualización gráfica de los autómatas resultantes.

## 🚀 Características

- Conversión automática de expresiones regulares infijas a postfijas
- Construcción de autómatas finitos no deterministas (AFN) con Thompson
- Visualización gráfica de los autómatas generados
- Soporte para operadores: `*` (Kleene), `+` (uno o más), `?` (opcional), `|` (alternancia), `.` (concatenación)
- Manejo de épsilon (ε)
- Guardado automático de imágenes en la carpeta `afn_outputs/`
- Permite probar cadenas en cada autómata generado


## 📦 Dependencias

El proyecto requiere la siguiente librería de Python:

```
matplotlib
```

## ⚙️ Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Vann06/Lab4_TCC.git
   cd Lab4_TCC
   ```

2. **Instala las dependencias:**
   ```bash
   pip install matplotlib
   ```

## 🏃‍♂️ Uso

1. Coloca tus expresiones regulares en `regex_p1.txt`, una por línea.
2. Ejecuta `main.py` para generar los autómatas y sus imágenes en la carpeta `afn_outputs/`.
3. El programa permite probar cadenas en cada autómata generado.

### Expresiones de Ejemplo

El archivo `regex_p1.txt` contiene las siguientes expresiones:

```
(a* | b*)+
((ε | a) | b*)*
(a | b)* abb (a | b)*
0? (1?)? 0*
```

### Procesamiento de Expresiones Personalizadas

Puedes agregar tus propias expresiones regulares al archivo `regex_p1.txt`, una por línea.

## 📁 Estructura de Salida

Al ejecutar el programa principal, se creará automáticamente una carpeta `afn_outputs/` que contendrá:

```
afn_outputs/
├── afn_1.png
├── afn_2.png
├── afn_3.png
└── afn_4.png
```

Cada imagen muestra:
- El autómata visual generado
- Los estados y transiciones
- Diferenciación visual de símbolos y transiciones epsilon

## 🎨 Visualización

Los autómatas generados utilizan:
- **Círculos de colores**: Estados (inicio, aceptación, intermedios)
- **Flechas**: Transiciones entre estados
- **Etiquetas**: Símbolos y transiciones epsilon

## 🔧 Operadores Soportados

| Operador | Nombre | Precedencia | Descripción |
|----------|---------|-------------|-------------|
| `*` | Estrella de Kleene | 3 | Cero o más repeticiones |
| `+` | Más | 3 | Una o más repeticiones |
| `?` | Interrogación | 3 | Cero o una repetición |
| `.` | Concatenación | 2 | Unión secuencial |
| `|` | Alternancia | 1 | OR lógico |

## 🖥️ Ejemplo de Ejecución

```bash
C:\Users\Vianka\Documents\GitHub\Lab4_TCC> python main.py

[1] Regex (infijo): (a*|b*)+
Postfix: ['a', '*', 'b', '*', '|', '+']
[Imagen generada: afn_outputs/afn_1.png]

... (similar para las demás expresiones)
```

## 🐛 Solución de Problemas

### Error: Módulo no encontrado
```bash
pip install matplotlib
```

### Error: Archivo no encontrado
Verifica que `regex_p1.txt` existe en el directorio del proyecto.

### Error: No se generan imágenes
Asegúrate de tener permisos de escritura en el directorio del proyecto.
