# Dev Environment Installer

Instalador gráfico para **configurar rápidamente un entorno de desarrollo** en un equipo nuevo.
Automatiza la instalación de herramientas comunes y configura Git para trabajar con GitHub mediante **SSH**.

La aplicación muestra un **log del proceso** mientras instala y configura las herramientas necesarias.

---

# Plataformas soportadas

* Windows 10 / 11
* Linux (Ubuntu / Debian / Linux Mint)

---

# Qué configura el instalador

El instalador prepara automáticamente:

**Herramientas**

* Bun
* Supabase CLI
* Prisma CLI
* ESLint
* Prettier
* Husky

**Configuración**

* Git global
* Git Credential Manager
* SSH para GitHub
* Git hooks globales
* Configuración global de ESLint
* Configuración global de Prettier

Archivos creados:

```text
~/.githooks
~/.prettierrc
~/.eslintrc.json
```

---

# Requisitos

## Windows

Debes tener instalados previamente:

* **Git**
* **Node.js**
* **Python 3.10+**

Verificar instalación:

```bash
git --version
node --version
python --version
```

Descargar:

Git
[https://git-scm.com](https://git-scm.com)

Node.js
[https://nodejs.org](https://nodejs.org)

---

## Linux (Ubuntu / Debian)

Instalar dependencias básicas:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git curl
```

Verificar:

```bash
python3 --version
git --version
curl --version
```

---

# Descargar el proyecto

Clonar el repositorio:

```bash
git clone https://github.com/USUARIO/REPO.git
```

Entrar al directorio:

```bash
cd REPO
```

---

# Crear entorno virtual

```bash
python -m venv .env
```

Activar entorno virtual.

### Windows

```bash
.env\Scripts\activate
```

### Linux

```bash
source .env/bin/activate
```

---

# Instalar dependencias

```bash
pip install PySide6
```

---

# Ejecutar el instalador

```bash
python app.py
```

Esto abrirá la interfaz gráfica.

---

# Uso

1. Introducir **Git Username**
2. Introducir **Git Email**
3. Presionar **"Correr instalador"**

El instalador configurará automáticamente el entorno.

---

# Configuración de SSH con GitHub

Durante la instalación aparecerá una ventana con tu **clave pública SSH**.

Pasos:

1. Copiar la clave
2. Ir a

```
https://github.com/settings/keys
```

3. Seleccionar **New SSH Key**
4. Pegar la clave y guardar

Esto permitirá usar GitHub sin contraseña.

---

# Resultado esperado

Después de ejecutar el instalador tendrás disponibles:

```text
git
bun
supabase
prisma
eslint
prettier
husky
```

y el entorno configurado para trabajar en proyectos modernos.

---

# Notas

* Puede ser necesario **reiniciar la terminal** para que algunas herramientas aparezcan en el PATH.
* En Linux algunas instalaciones requieren permisos `sudo`.

---

# Licencia

Proyecto creado con fines educativos y para automatizar la configuración de entornos de desarrollo.
