#!/bin/bash

NIKNAME="KornilovLN"
TOKEN_FILE=~/virt/token/tok.txt

# Проверка наличия файла с токеном
if [ ! -f "$TOKEN_FILE" ]; then
    echo "Ошибка: Файл с токеном не найден по пути $TOKEN_FILE"
    exit 1
fi

# Функция для запроса подтверждения
confirm() {
    read -p "$1 [Yes]/No: " response
    case "$response" in
        [nN][oO]|[nN]) return 1 ;;
        *) return 0 ;;
    esac
}

# Git status
if confirm "Выполнить git status?"; then
    git status
fi

# Git add
if confirm "Выполнить git add .?"; then
    git add .
fi

# Git status после add
if confirm "Выполнить git status после add?"; then
    git status
fi

# Git commit
if confirm "Выполнить git commit?"; then
    read -p "Введите сообщение коммита: " commit_message
    git commit -m "$commit_message"
fi

# Git push
if confirm "Выполнить git push?"; then
    github_username=${github_username:-$NIKNAME}
    token=$(cat "$TOKEN_FILE")
    echo "Используется токен из файла $TOKEN_FILE"
    git push https://$github_username:$token@github.com/$github_username/$(basename $(git rev-parse --show-toplevel)).git
fi

echo "Операции Git завершены."
