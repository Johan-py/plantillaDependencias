import subprocess
import shutil
import platform
import os
from pathlib import Path
import time
time.sleep(2)
OS = platform.system()


# -------------------------------------------------
# UTILIDADES
# -------------------------------------------------

def log_msg(log, msg):

    if log:
        log(msg)
    else:
        print(msg)


def step(msg, log=None):

    line = f"\n==== {msg} ===="

    log_msg(log, line)


def run(cmd, log=None):

    log_msg(log, f"$ {cmd}")

    try:

        process = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )

        if process.stdout:
            log_msg(log, process.stdout.strip())

        if process.stderr:
            log_msg(log, process.stderr.strip())

    except subprocess.CalledProcessError as e:

        log_msg(log, f"ERROR ejecutando: {cmd}")

        if e.stdout:
            log_msg(log, e.stdout.strip())

        if e.stderr:
            log_msg(log, e.stderr.strip())


def exists(cmd):
    return shutil.which(cmd) is not None or shutil.which(cmd + ".cmd") is not None


def scoop_path():
    return Path.home() / "scoop" / "shims" / "scoop.cmd"


def scoop_exists():
    return scoop_path().exists()


# -------------------------------------------------
# GIT
# -------------------------------------------------

def install_git(log=None):

    step("Checking Git", log)

    if exists("git"):
        log_msg(log, "Git OK")
        return

    if OS == "Linux":
        run("sudo apt update", log)
        run("sudo apt install -y git", log)

    elif OS == "Windows":
        log_msg(log, "Instala Git manualmente desde https://git-scm.com")


def configure_git(name, email, log=None):

    step("Configuring Git", log)

    lock = Path.home() / ".gitconfig.lock"

    # eliminar lock viejo
    if lock.exists():
        try:
            lock.unlink()
            log_msg(log, "Removed stale gitconfig lock")
        except Exception as e:
            log_msg(log, f"Could not remove gitconfig lock: {e}")

    # configurar usuario
    run(f'git config --global user.name "{name}"', log)
    run(f'git config --global user.email "{email}"', log)

    run("git config --global init.defaultBranch main", log)
    run("git config --global pull.rebase false", log)

    if OS == "Windows":
        run("git config --global core.autocrlf true", log)
    else:
        run("git config --global core.autocrlf input", log)

    # verificar resultado
    user = subprocess.check_output(
        "git config --global user.name", shell=True, text=True
    ).strip()

    mail = subprocess.check_output(
        "git config --global user.email", shell=True, text=True
    ).strip()

    log_msg(log, f"Git user configurado: {user}")
    log_msg(log, f"Git email configurado: {mail}")


# -------------------------------------------------
# GIT CREDENTIAL MANAGER
# -------------------------------------------------

def install_git_credentials(log=None):

    step("Configuring Git Credential Manager", log)

    if OS == "Windows":
        run("git config --global credential.helper manager", log)
    else:
        run("git config --global credential.helper store", log)

    log_msg(log, "Credential manager configurado")


# -------------------------------------------------
# SSH GITHUB
# -------------------------------------------------
def setup_github_ssh(email, log=None, show_key=None):

    step("Setting up GitHub SSH", log)

    home = Path.home()

    ssh_dir = home / ".ssh"
    key = ssh_dir / "id_ed25519"
    pub_key = ssh_dir / "id_ed25519.pub"

    ssh_dir.mkdir(exist_ok=True)

    # si ya existe
    if key.exists():

        log_msg(log, "SSH key ya existe")

        if pub_key.exists():

            with open(pub_key) as f:
                key_text = f.read()

            log_msg(log, "SSH key encontrada")

            # mostrar popup en GUI
            if show_key:
                show_key(key_text)

        else:
            log_msg(log, "No se encontró la clave pública")

        return

    # crear key nueva
    run(f'ssh-keygen -t ed25519 -C "{email}" -f "{key}" -N ""', log)

    run(f"ssh-add {key}", log)

    with open(pub_key) as f:
        key_text = f.read()

    log_msg(log, "SSH key creada")

    if show_key:
        show_key(key_text)


# -------------------------------------------------
# NODE
# -------------------------------------------------

def install_node(log=None):

    step("Checking Node", log)

    if exists("node") and exists("npm"):
        log_msg(log, "Node OK")
        return
    if OS == "Linux":

        run("curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -", log)
        run("sudo apt install -y nodejs", log)

    else:
        log_msg(log, "Instala Node desde https://nodejs.org")


# -------------------------------------------------
# BUN
# -------------------------------------------------

def install_bun(log=None):

    step("Checking Bun", log)

    if exists("bun"):
        log_msg(log, "Bun OK")
        return

    if OS == "Linux":
        run("curl -fsSL https://bun.sh/install | bash", log)

    elif OS == "Windows":
        run('powershell -c "irm https://bun.sh/install.ps1 | iex"', log)


def ensure_bun_path(log=None):

    bun_bin = Path.home() / ".bun" / "bin"

    if OS == "Windows":

        run(f'setx PATH "%PATH%;{bun_bin}"', log)

    log_msg(log, "Bun bin agregado al PATH")


# -------------------------------------------------
# SUPABASE CLI
# -------------------------------------------------
def install_supabase(log=None):

    step("Installing Supabase CLI", log)

    if exists("supabase"):
        log_msg(log, "Supabase CLI OK")
        return

    # Prefer Bun
    if exists("bun"):
        run("bun add -g supabase", log)
        return

    # Windows -> Scoop
    if OS == "Windows":

        log_msg(log, "Installing Supabase via Scoop")

        if not scoop_exists():

            run(
                'powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"',
                log
            )

            run(
                'powershell -Command "iwr -useb get.scoop.sh | iex"',
                log
            )

        scoop = scoop_path()

        if scoop.exists():
            run(f'"{scoop}" install supabase', log)
        else:
            log_msg(log, "Scoop installation failed")

        return

    # Linux fallback
    run("curl -fsSL https://supabase.com/install | sh", log)


# -------------------------------------------------
# PRISMA CLI
# -------------------------------------------------

def install_prisma(log=None):

    step("Installing Prisma CLI", log)

    if exists("prisma"):
        log_msg(log, "Prisma CLI OK")
        return

    if exists("bun"):
        run("bun add -g prisma", log)

    elif exists("npm"):
        run("npm install -g prisma", log)

    else:
        log_msg(log, "No JS runtime found (bun/npm)")


# -------------------------------------------------
# ESLINT
# -------------------------------------------------
def install_eslint(log=None):

    step("Installing ESLint", log)

    if exists("eslint"):
        log_msg(log, "ESLint OK")
        return

    if exists("bun"):
        run("bun add -g eslint", log)

    elif exists("npm"):
        run("npm install -g eslint", log)

    else:
        log_msg(log, "No JS runtime found")


# -------------------------------------------------
# PRETTIER
# -------------------------------------------------

def install_prettier(log=None):

    step("Installing Prettier", log)

    if exists("prettier"):
        log_msg(log, "Prettier OK")
        return

    if exists("bun"):
        run("bun add -g prettier", log)
    else:
        run("npm install -g prettier", log)


# -------------------------------------------------
# HUSKY
# -------------------------------------------------

def install_husky(log=None):

    step("Installing Husky", log)

    if exists("bun"):
        run("bun add -g husky", log)
    else:
        run("npm install -g husky", log)


# -------------------------------------------------
# GLOBAL GIT HOOKS - VERSIÓN MEJORADA
# -------------------------------------------------

def configure_git_hooks(log=None):

    step("Configuring global Git hooks (mejorado)", log)

    hooks_dir = os.path.expanduser("~/.githooks")

    os.makedirs(hooks_dir, exist_ok=True)

    run(f"git config --global core.hooksPath {hooks_dir}", log)

    pre_commit = os.path.join(hooks_dir, "pre-commit")

    # Script mejorado que:
    # 1. Usa ESLint/Prettier del proyecto cuando están disponibles
    # 2. Respeta archivos de configuración del proyecto
    # 3. Soporta TypeScript correctamente
    # 4. Permite saltar hooks con un archivo .skip-global-hooks
    script = """#!/bin/sh

echo "Running global checks..."

# Permitir saltar hooks globales para proyectos específicos
if [ -f ".skip-global-hooks" ]; then
  echo "  → Skipping global hooks (found .skip-global-hooks)"
  exit 0
fi

# Verificar si estamos en un proyecto con package.json
if [ ! -f "package.json" ]; then
  exit 0
fi

# Función para usar ESLint del proyecto
run_eslint() {
  if [ -f "node_modules/.bin/eslint" ]; then
    ./node_modules/.bin/eslint "$@"
    return $?
  elif command -v eslint >/dev/null 2>&1; then
    eslint "$@"
    return $?
  fi
  return 0
}

# Función para usar Prettier del proyecto
run_prettier() {
  if [ -f "node_modules/.bin/prettier" ]; then
    ./node_modules/.bin/prettier "$@"
    return $?
  elif command -v prettier >/dev/null 2>&1; then
    prettier "$@"
    return $?
  fi
  return 0
}

# Obtener archivos staged
FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Verificar archivos JS/TS/JSX/TSX
JS_FILES=$(echo "$FILES" | grep -E '\\.(js|jsx|ts|tsx)$' | grep -v "node_modules" || true)

if [ ! -z "$JS_FILES" ]; then
  echo "  → Checking staged files:"
  echo "$JS_FILES" | sed 's/^/      /'
  
  # Ejecutar ESLint
  echo "  → Running ESLint..."
  run_eslint $JS_FILES --max-warnings=0
  ESLINT_EXIT=$?
  
  if [ $ESLINT_EXIT -ne 0 ]; then
    echo ""
    echo "❌ ESLint errors found. Fix them with:"
    echo "   bun run lint:fix"
    echo ""
    echo "Or skip hooks with: touch .skip-global-hooks"
    exit 1
  fi
  
  # Verificar formato con Prettier
  echo "  → Checking formatting..."
  run_prettier --check $JS_FILES
  PRETTIER_EXIT=$?
  
  if [ $PRETTIER_EXIT -ne 0 ]; then
    echo ""
    echo "❌ Prettier formatting issues found. Fix them with:"
    echo "   bun run lint:fix"
    echo "   or"
    echo "   npx prettier --write $JS_FILES"
    echo ""
    echo "Or skip hooks with: touch .skip-global-hooks"
    exit 1
  fi
  
  echo "  ✅ All checks passed!"
fi

exit 0
"""

    with open(pre_commit, "w") as f:
        f.write(script)

    os.chmod(pre_commit, 0o755)

    log_msg(log, "✓ Hooks globales configurados (versión mejorada)")
    log_msg(log, "  → Usa ESLint/Prettier del proyecto cuando están disponibles")
    log_msg(log, "  → Soporta TypeScript correctamente")
    log_msg(log, "  → Para saltar hooks: touch .skip-global-hooks")


# -------------------------------------------------
# PRETTIER CONFIG - VERSIÓN MEJORADA (OPCIONAL)
# -------------------------------------------------

def configure_prettier(log=None):

    step("Configuring Prettier (opcional)", log)

    home = Path.home()

    config = home / ".prettierrc"

    content = """{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "none",
  "printWidth": 100
}
"""

    # Solo crear si no existe, para no sobrescribir config existente
    if not config.exists():
        with open(config, "w") as f:
            f.write(content)
        log_msg(log, "✓ Prettier global configurado")
    else:
        log_msg(log, "→ Prettier global config ya existe, no se modificó")


# -------------------------------------------------
# ESLINT CONFIG - VERSIÓN MEJORADA (OPCIONAL)
# -------------------------------------------------

def configure_eslint(log=None):

    step("Configuring ESLint (opcional)", log)

    home = Path.home()

    config = home / ".eslintrc.json"

    # Configuración mejorada que soporta TypeScript si está disponible
    content = """{
  "env": {
    "node": true,
    "es2022": true
  },
  "extends": ["eslint:recommended"],
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module"
  },
  "rules": {
    "no-console": "off",
    "prefer-const": "warn"
  },
  "overrides": [
    {
      "files": ["*.ts", "*.tsx"],
      "parser": "@typescript-eslint/parser",
      "plugins": ["@typescript-eslint"],
      "extends": ["plugin:@typescript-eslint/recommended"]
    }
  ]
}
"""

    # Solo crear si no existe, para no sobrescribir config existente
    if not config.exists():
        with open(config, "w") as f:
            f.write(content)
        log_msg(log, "✓ ESLint global configurado")
    else:
        log_msg(log, "→ ESLint global config ya existe, no se modificó")


# -------------------------------------------------
# FINAL
# -------------------------------------------------

def finish(log=None):

    log_msg(log, "\n==============================")
    log_msg(log, "ENVIRONMENT READY")
    log_msg(log, "==============================\n")

    log_msg(log, """
Tools instaladas:

✓ git
✓ bun
✓ node (opcional)
✓ supabase CLI
✓ prisma CLI
✓ eslint
✓ prettier
✓ husky
✓ SSH GitHub
✓ Git hooks globales (mejorados)

NOTAS IMPORTANTES:
• Los hooks globales usan ESLint/Prettier del proyecto cuando están disponibles
• Para saltar hooks globales: touch .skip-global-hooks
• Si usas TypeScript, asegúrate de tener @typescript-eslint/parser en el proyecto
""")
