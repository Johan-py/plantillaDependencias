import subprocess
import shutil
import platform
import os
from pathlib import Path

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
        subprocess.run(cmd, shell=True, check=True)

    except subprocess.CalledProcessError as e:

        log_msg(log, f"ERROR ejecutando: {cmd}")
        raise e


def exists(cmd):
    return shutil.which(cmd) is not None


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

    run(f'git config --global user.name "{name}"', log)
    run(f'git config --global user.email "{email}"', log)

    run("git config --global init.defaultBranch main", log)
    run("git config --global pull.rebase false", log)

    if OS == "Windows":
        run("git config --global core.autocrlf true", log)
    else:
        run("git config --global core.autocrlf input", log)

    log_msg(log, "Git configurado")


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

    if exists("node"):
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


# -------------------------------------------------
# SUPABASE CLI
# -------------------------------------------------

def install_supabase(log=None):

    step("Installing Supabase CLI", log)

    if exists("supabase"):
        log_msg(log, "Supabase CLI OK")
        return

    if exists("bun"):
        run("bun add -g supabase", log)
    else:
        run("npm install -g supabase", log)


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
    else:
        run("npm install -g prisma", log)


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
    else:
        run("npm install -g eslint", log)


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
# GLOBAL GIT HOOKS
# -------------------------------------------------

def configure_git_hooks(log=None):

    step("Configuring global Git hooks", log)

    hooks_dir = os.path.expanduser("~/.githooks")

    os.makedirs(hooks_dir, exist_ok=True)

    run(f"git config --global core.hooksPath {hooks_dir}", log)

    pre_commit = os.path.join(hooks_dir, "pre-commit")

    script = """#!/bin/sh
echo "Running global checks..."

if command -v eslint >/dev/null 2>&1; then
  eslint .
fi

if command -v prettier >/dev/null 2>&1; then
  prettier --check .
fi
"""

    with open(pre_commit, "w") as f:
        f.write(script)

    os.chmod(pre_commit, 0o755)

    log_msg(log, "Hooks globales configurados")


# -------------------------------------------------
# PRETTIER CONFIG
# -------------------------------------------------

def configure_prettier(log=None):

    step("Configuring Prettier", log)

    home = Path.home()

    config = home / ".prettierrc"

    content = """
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "none",
  "printWidth": 100
}
"""

    with open(config, "w") as f:
        f.write(content)

    log_msg(log, "Prettier configurado")


# -------------------------------------------------
# ESLINT CONFIG
# -------------------------------------------------

def configure_eslint(log=None):

    step("Configuring ESLint", log)

    home = Path.home()

    config = home / ".eslintrc.json"

    content = """
{
  "env": {
    "browser": true,
    "node": true,
    "es2021": true
  },
  "extends": ["eslint:recommended"],
  "parserOptions": {
    "ecmaVersion": "latest"
  },
  "rules": {}
}
"""

    with open(config, "w") as f:
        f.write(content)

    log_msg(log, "ESLint configurado")


# -------------------------------------------------
# FINAL
# -------------------------------------------------

def finish(log=None):

    log_msg(log, "\n==============================")
    log_msg(log, "ENVIRONMENT READY")
    log_msg(log, "==============================\n")

    log_msg(log, """
Tools instaladas:

git
bun
node (opcional)

supabase CLI
prisma CLI
eslint
prettier
husky

SSH GitHub
Git hooks globales
""")