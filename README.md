# Vocal Studio (`vocal-studio`)

AI Vocal Isolation, Automatic Onset Trimming & Studio Reverb Processing tool for YouTube URLs and local audio files.

---

## Мүмкіндіктері / Features

- **YouTube & Жергілікті файлдар**: YouTube сілтемесін немесе кез келген жергілікті аудио/бейне файлын автоматты түрде өңдейді.
- **AI арқылы вокалды бөлу (Demucs)**: Аспаптық сүйемелдеуден (музыкадан) вокалды жоғары сапада бөліп алады.
- **Вокал басталған жерді автоматты анықтау (Onset Detection)**: Тректің басындағы артық музыкалық интроны немесе тыныштықты кесіп, дәл әнші айта бастаған жерден бастайды.
- **Студиялық Reverb эффектісі (Pedalboard)**: Студиялық кеңістік, төменгі жиіліктерді тазарту (High-pass 80 Hz), динамикалық компрессор және дыбыс деңгейін нормализациялау (-1.0 dBFS).
- **Бірнеше форматта экспорттау**:
  - `vocal_reverb`: Reverb эффектісі қосылған таза вокал
  - `vocal_dry`: Өңделмеген таза құрғақ вокал
  - `full_trimmed`: Интросы вокал басталған жерге дейін кесілген толық ән
  - `reverb_mix`: Reverb вокал мен музыканың қайта біріктірілген миксі

---

## Орнату / Installation

### 1. Жүйелік талаптар (System Requirements)
Жүйеде `ffmpeg` бағдарламасы орнатылған болуы қажет:
```bash
# macOS (Homebrew)
brew install ffmpeg

# Ubuntu / Debian Linux
sudo apt update && sudo apt install -y ffmpeg
```

### 2. Пакетті орнату (Python Package Installation)
```bash
# GitHub арқылы тікелей орнату:
pip install git+https://github.com/Azamaperdeev05/vocal-studio.git

# Немесе репозиторийден жергілікті түрде:
git clone https://github.com/Azamaperdeev05/vocal-studio.git
cd vocal-studio
pip install -e .
```

---

## Қолдану / Usage

### CLI арқылы (Терминалдан):

```bash
# YouTube видеосынан вокалды бөліп, reverb қосып, интросын қысқарту:
vocal-studio "https://youtu.be/CNwM8BJGyTk"

# Нәтижелерді басқа қапшыққа сақтау:
vocal-studio "https://youtu.be/CNwM8BJGyTk" -o ./my_vocals

# Reverb параметрлерін өзгерту (бөлме көлемі және wet деңгейі):
vocal-studio "https://youtu.be/CNwM8BJGyTk" --room-size 0.75 --wet-level 0.40

# Интроны кеспей, толық ұзақтықты қалдыру:
vocal-studio "https://youtu.be/CNwM8BJGyTk" --no-trim

# Вокалдың басталу уақытын қолмен көрсету (мысалы 14.5 секунд):
vocal-studio "https://youtu.be/CNwM8BJGyTk" --start-time 14.5
```

### Python кодын қолдану арқылы:

```python
from vocal_studio import process_audio, VocalStudioConfig

config = VocalStudioConfig(
    output_dir="./processed_tracks",
    trim_to_vocal_start=True,
    reverb_room_size=0.68,
    reverb_wet_level=0.35,
    export_mp3=True,
    export_wav=True
)

result = process_audio("https://youtu.be/CNwM8BJGyTk", config)

print(f"Ән атауы: {result['title']}")
print(f"Вокал басталған уақыт: {result['vocal_start_seconds']:.2f} сек")
print("Шығарылған файлдар:", result['tracks'])
```

---

## Лицензия / License
MIT License. Авторлық құқық (c) 2026 Azamat.

