# GitHub Publish Guide

Repository name:

```text
crypto-funding-scanner
```

Repository description:

```text
Real-time negative funding rate scanner for Binance, Bybit and Bitget perpetual futures.
```

Topics / tags:

```text
python
crypto
funding-rate
binance
bybit
bitget
futures
scanner
trading-tools
perpetual-futures
```

---

# Как опубликовать проект на GitHub

## Вариант 1 — через сайт GitHub

1. Зайди на GitHub.
2. Нажми `New repository`.
3. В поле `Repository name` вставь:

```text
crypto-funding-scanner
```

4. В поле `Description` вставь:

```text
Real-time negative funding rate scanner for Binance, Bybit and Bitget perpetual futures.
```

5. Выбери:
   - `Public`, если хочешь открыть проект всем
   - `Private`, если проект только для себя

6. Не ставь галочки:
   - `Add a README file`
   - `Add .gitignore`
   - `Choose a license`

Потому что эти файлы уже есть в проекте.

7. Нажми `Create repository`.

---

## Загрузка файлов через GitHub web interface

1. Открой созданный репозиторий.
2. Нажми `uploading an existing file`.
3. Перетащи все файлы из папки проекта.
4. Внизу в поле commit message напиши:

```text
Initial stable release
```

5. Нажми `Commit changes`.

---

## Вариант 2 — через Git на компьютере

Открой терминал в папке проекта и выполни:

```bash
git init
git add .
git commit -m "Initial stable release"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/crypto-funding-scanner.git
git push -u origin main
```

Замени `YOUR_USERNAME` на свой GitHub username.

---

# Что вставить в GitHub About

## Description

```text
Real-time negative funding rate scanner for Binance, Bybit and Bitget perpetual futures.
```

## Website

Оставить пустым.

## Topics

Вставить по одному:

```text
python
crypto
funding-rate
binance
bybit
bitget
futures
scanner
trading-tools
perpetual-futures
```

---

# Первый релиз

После загрузки проекта можно создать release:

1. Открой вкладку `Releases`.
2. Нажми `Create a new release`.
3. В поле `Choose a tag` напиши:

```text
v1.0.0
```

4. Release title:

```text
Crypto Funding Scanner v1.0.0
```

5. Description:

```text
Initial stable release.

Features:
- Binance Futures support
- Bybit Futures support
- Bitget Futures support
- Negative funding rate scanner
- Stable live console dashboard
- Windows BAT launcher
- Automatic Python and dependency checks
```

6. Нажми `Publish release`.
