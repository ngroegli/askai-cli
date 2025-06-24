#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
CONFIG_FILE="$HOME/.askai_config.yml"
DEFAULT_CONFIG="$SCRIPT_DIR/config/config_example.yml"

echo "==> Setting up Python virtual environment..."

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "Created virtual environment at $VENV_DIR"
else
    echo "Virtual environment already exists at $VENV_DIR"
fi

echo "==> Activating virtual environment and installing requirements..."

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "Warning: requirements.txt not found, skipping pip install"
fi

deactivate

echo "==> Checking config file..."

if [ ! -f "$CONFIG_FILE" ]; then
    if [ -f "$DEFAULT_CONFIG" ]; then
        cp "$DEFAULT_CONFIG" "$CONFIG_FILE"
        echo "Copied default config to $CONFIG_FILE"
        echo "Please review and edit your config file as needed."
    else
        echo "Default config file ($DEFAULT_CONFIG) not found! Please create $CONFIG_FILE manually."
    fi
else
    echo "Config file $CONFIG_FILE already exists."
fi

echo "==> Setting up alias for askai command..."

ALIAS_CMD="alias askai='$SCRIPT_DIR/askai.sh'"
ALIAS_COMMENT="# AskAI CLI alias added by install.sh"

add_alias_to_shell() {
    local shellrc="$1"
    if [ -f "$shellrc" ]; then
        if ! grep -q "$ALIAS_COMMENT" "$shellrc"; then
            echo -e "\n$ALIAS_COMMENT\n$ALIAS_CMD" >> "$shellrc"
            echo "Added alias to $shellrc"
        else
            echo "Alias already present in $shellrc"
        fi
    fi
}

add_alias_to_shell "$HOME/.bashrc"
add_alias_to_shell "$HOME/.zshrc"

echo "Installation complete! Please restart your terminal or run 'source ~/.bashrc' or 'source ~/.zshrc' to activate the alias."
