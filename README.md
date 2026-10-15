# 🌍 AI Travel Guide

An AI-powered Travel Guide application that helps users explore tourist destinations through AI-generated descriptions and voice narration. The application provides informative travel content in multiple languages, making it easier for users to learn about famous places around the world.

## ✨ Features

- 🌎 **Explore Destinations:** Discover information about tourist destinations.
- 🤖 **AI-Powered Descriptions:** Generate travel guides using Google Gemini AI.
- 📝 **Summary Mode:** Get a concise overview of a destination, including its history, popularity, and highlights.
- 📚 **Detailed Mode:** Explore detailed information about a destination, including its history, architecture, culture, and interesting facts.
- 🗣️ **Text-to-Speech:** Listen to travel guides using Murf AI voice narration.
- 🌐 **Multilingual Support:** Supports English, Hindi, Tamil, and Telugu.
- 🎙️ **Male and Female Voices:** Choose a voice for a personalized listening experience.
- 🔊 **Audio Narration:** Listen to generated travel information instead of reading everything.
- 💻 **Simple User Interface:** An easy-to-use interface for exploring destinations.

## 🛠️ Technologies Used

### Frontend
- HTML
- CSS
- JavaScript

### Backend
- Python
- Flask
- Flask-CORS

### AI and APIs
- Google Gemini API
- Murf AI Text-to-Speech API
- Python Requests
- Python dotenv

## 📁 Project Structure

```text
Travel-Guide/
│
├── Frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── Backend/
│   ├── app.py
│   ├── .env
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

*Note: Adjust the filenames and folder structure to match your actual project.*

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Travel-Guide
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your GitHub repository URL.

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r Backend/requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file inside the `Backend` folder:

```env
GEMINI_API_KEY=your_gemini_api_key
MURF_API_KEY=your_murf_api_key
```

Replace the placeholder values with your own API keys. Never upload your actual API keys to GitHub.

### 5. Run the Backend

From the project root directory, run:

```bash
python Backend/app.py
```

The Flask backend should start at:

```text
http://127.0.0.1:5000
```

### 6. Open the Frontend

Open `Frontend/index.html` using VS Code Live Server or your configured frontend server.

## 🚀 How to Use

1. Open the Travel Guide application.
2. Enter the name of a tourist destination.
3. Select the preferred language.
4. Choose Summary or Detailed mode.
5. Select a male or female voice.
6. Generate the travel guide.
7. Read the AI-generated information and listen to the voice narration.

## 🔐 Security

- Store API keys in environment variables.
- Keep `.env` out of version control.
- Add `.venv/`, `__pycache__/`, and other unnecessary generated files to `.gitignore`.
- Never share API keys in public repositories.

## 🔮 Future Enhancements

- 📍 Interactive maps and location-based recommendations.
- 🌦️ Real-time weather information for destinations.
- 🏨 Hotel and restaurant recommendations.
- 🗺️ Personalized travel itineraries.
- 📱 Responsive mobile-friendly design.
- 🔊 Improved audio playback controls.

## 🎯 Project Objective

The objective of this project is to combine generative AI and text-to-speech technology to create an interactive, multilingual travel assistant that makes discovering tourist destinations more informative, accessible, and engaging.

## 👨‍💻 Author

**Travel Guide AI Project**

Built with Python, Flask, Google Gemini AI, and Murf AI.

---

⭐ If you find this project useful, consider giving the repository a star on GitHub.

