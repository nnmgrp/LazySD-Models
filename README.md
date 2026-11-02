# 🎴 LazySD-Models

> Официальный каталог проверенных, оптимизированных и готовых к запуску карточек моделей для [LazySD-UI](https://github.com/nnmgrp/LazySD-UI).

[![Validate Models & Index](https://github.com/nnmgrp/LazySD-Models/actions/workflows/validate.yml/badge.svg)](https://github.com/nnmgrp/LazySD-Models/actions/workflows/validate.yml)

Этот репозиторий служит централизованным каталогом (Model Hub) для LazySD-UI. Каждая карточка содержит полную конфигурацию для загрузки, квантования, привязки текстовых энкодеров, VAE и запуска на одном из поддерживаемых движков инференса.

---

## ⚡ Поддерживаемые движки и архитектуры

Каждая модель строго привязана к базовой геометрии весов (`target_architecture`), что гарантирует **100% совместимость LoRA** между разными движками и предотвращает сбои при генерации:

| Архитектура (`target_architecture`) | Движки | Примеры моделей | Совместимость LoRA |
|---|---|---|---|
| `flux_2_klein_9b` | Nunchaku (SVDQ), OrbitQuant, GGUF (SD.CPP), QuantFunc | Flux.2 Klein 9B | ✅ Любая 9B LoRA работает на всех 4 движках |
| `flux_2_klein_4b` | Nunchaku (SVDQ), OrbitQuant, QuantFunc | Flux.2 Klein 4B | ✅ Изолирована от 9B |
| `flux_3_image_klein` | Nunchaku, SD.CPP (GGUF) | FLUX.3 Image Klein | ✅ Изолирована от Klein 2 |
| `flux_1` | SD.CPP (GGUF) | FLUX.1 Dev, Schnell | ✅ Стандартные Flux.1 LoRA |
| `qwen_image_2_1` | SDNQ, Nunchaku, SD.CPP (GGUF), QuantFunc | Qwen-Image 2.1 (Turbo / Base) | ✅ Любая Qwen 2.1 LoRA |
| `z_image_turbo` | OrbitQuant, QuantFunc | Z-Image Turbo | ✅ Z-Image LoRA |
| `sdxl` | SD.CPP (GGUF), Diffusers | SDXL Turbo, Pony, Illustrious | ✅ SDXL LoRA |

---

## 📥 Как использовать в LazySD-UI

### Автоматическая установка (Рекомендуется)
1. Откройте **LazySD-UI** и перейдите во вкладку **«Модели» → «Каталог LazySD-Models»**.
2. Найдите интересующую вас модель через поиск или фильтры по движкам/архитектуре.
3. Нажмите **«Установить карточку»** — карточка скачается за секунду и станет доступна в списке моделей без перезапуска сервера.

### Ручная установка
1. Скачайте нужный `.json` файл из папки [`models/`](models/).
2. Поместите его в папку `models/` (или `backend/registry/custom/`) вашей копии LazySD-UI.
3. Нажмите кнопку «Обновить модели» в веб-интерфейсе.

---

## 🛠️ Как добавить новую карточку модели (Pull Request)

Мы приветствуем добавление оптимизированных карточек от сообщества!

### 1. Требования к карточке
- Модель должна быть протестирована на заявленном движке (генерация хотя бы одного изображения).
- Обязательно укажите минимальный и рекомендуемый объем VRAM в `requirements`.
- В `target_architecture` укажите точную архитектуру весов (`flux_2_klein_9b`, `flux_2_klein_4b`, `qwen_image_2_1` и т.д.).
- Компоненты (Text Encoder, VAE) должны иметь рабочие ссылки на Hugging Face репозитории.

### 2. Структура JSON-манифеста
```json
{
  "id": "my_new_model_nunchaku",
  "name": "My Model Name (Nunchaku)",
  "family": "klein",
  "target_architecture": "flux_2_klein_9b",
  "pipeline": "text_to_image",
  "engine": "nunchaku",
  "engine_version": "nunchaku",
  "description": "Описание модели, особенности квантования и скорость.",
  "sources": {
    "primary": {
      "type": "huggingface",
      "repo_id": "author/model-repo"
    }
  },
  "requirements": {
    "vram_min_gb": 8,
    "vram_recommended_gb": 12
  },
  "scheduler_presets": {
    "default": {
      "steps": 4,
      "cfg": 1.0,
      "sampler": "euler"
    }
  },
  "tags": ["klein", "flux", "nunchaku"]
}
```

### 3. Локальная проверка перед отправкой PR
Перед отправкой Pull Request запустите сборщик индекса:
```bash
python scripts/build_index.py
```
Скрипт проверит валидность всех полей и обновит файл `index.json`.

---

## 📡 Прямой доступ к индексу
LazySD-UI и сторонние интеграции могут получать актуальный каталог по прямой ссылке:
```
https://raw.githubusercontent.com/nnmgrp/LazySD-Models/main/index.json
```
