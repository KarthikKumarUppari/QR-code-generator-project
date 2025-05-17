# QR Event Generator

A full-stack web application to generate **QR codes** for:
- Simple text or links
- Calendar events in VCALENDAR (.ics) format

## 📁 Project Structure
```
qr-event-generator/
├── app.py        # Flask backend for text & calendar QR generation
├── index.html    # Frontend for input and QR display
└── README.md     # Documentation
```

## 🔧 Requirements
- Python 3.x
- Flask
- flask-cors

### Install Dependencies
```bash
pip install flask flask-cors
```

## ▶️ How to Run
1. Place `app.py` and `index.html` in the same folder
2. Run the backend:
```bash
python app.py
```
3. Open your browser:
```
http://localhost:5000
```

## ✅ Features
- 📄 Text/Link to QR
- 📅 Calendar Event to QR
- 🧾 VCALENDAR `.ics` support for event QR codes

## 📦 Future Ideas
- `.ics` file download
- Event database
- Export/share QR images
- Dark/light theme toggle
