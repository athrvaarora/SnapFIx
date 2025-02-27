# SnapFix

<p align="center">
  <em>AI-powered productivity solution for instant troubleshooting</em>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#achievements">Achievements</a> •
  <a href="#team">Team</a> •
  <a href="#license">License</a>
</p>

## Overview

SnapFix is an innovative AI-powered productivity solution developed at The University of Texas's Engineering Entrepreneurship Program. It transforms troubleshooting by intelligently analyzing screenshots to provide immediate solutions without requiring users to formulate prompts or queries.



## Features

- **Instant Error Resolution**: Automatically diagnoses and solves technical errors captured in screenshots
- **Continuous Monitoring**: Works silently in the background, analyzing screen captures as they happen
- **Contextual Understanding**: Identifies the type of content in the screenshot and provides targeted solutions
- **Document Processing**: Creates flashcards and comprehensive notes from educational materials
- **No Prompt Writing**: Get solutions without having to formulate queries - just take a screenshot!

## How It Works

1. **Screenshot Capture**: Use the standard Windows shortcut (Win+Shift+S) to capture any part of your screen
2. **Automatic Analysis**: SnapFix detects new screenshots and performs:
   - Text extraction with EasyOCR
   - Visual analysis using OpenAI's GPT-4V
   - Context-aware prompt engineering
3. **Solution Generation**: Provides tailored solutions based on the content type:
   - Code fixes for programming errors
   - Step-by-step solutions for technical problems
   - Summaries for documentation
4. **Intelligent Document Processing**: Upload documents to:
   - Generate comprehensive, structured notes
   - Create effective flashcards for studying



## Tech Stack

- **Backend**:
  - Python with Flask for API endpoints
  - OpenAI GPT-4o-mini and GPT-3.5 Turbo for analysis and solution generation
  - EasyOCR for text extraction from images
  - PyWin32 for Windows OS integration
  - PyStray for system tray functionality

- **Frontend**:
  - React for the user interface
  - TailwindCSS for styling
  - React Router for navigation
  - React Markdown for rendering notes

- **Document Processing**:
  - PyPDF2 for PDF handling
  - python-docx for Word document processing
  - python-pptx for PowerPoint presentations

- **Development & Deployment**:
  - Vite for frontend build
  - PyInstaller for creating executable
  - Flask-CORS for cross-origin resource sharing

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Setup

1. Clone the repository
```bash
git clone https://github.com/your-username/snapfix.git
cd snapfix
```

2. Install backend dependencies
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies
```bash
cd frontend
npm install
cd ..
```

4. Configure your OpenAI API key
```bash
# In main.py, replace the API_KEY with your own key
API_KEY = "your-api-key-here"
```

5. Run the development server
```bash
python main.py
```

6. In a separate terminal, run the frontend
```bash
cd frontend
npm run dev
```

### Building for Production

```bash
# Build the frontend
cd frontend
npm run build

# Create executable
pyinstaller --onefile --windowed --add-data "frontend/dist;frontend/dist" main.py
```

## Usage

### Screenshot Analysis
1. Press `Win+Shift+S` to capture a screenshot
2. Select the area you want to analyze
3. The analysis appears automatically in the SnapFix interface

### Document Processing
1. Navigate to the Flashcards or Notes tab
2. Click the upload area to select a document (.pdf, .docx, .ppt, .pptx)
3. SnapFix will process the document and generate the requested content

## Achievements

- 🏆 **Outstanding Pitch Award** at the Mavpitch competition
- 💰 Secured $2,500 in pre-seed funding
- 📊 85% satisfaction rate among IT professionals during user testing

## Team

- Athrva Arora 
- Araohat Kokate 
- Asmin Pothula  
- Sneh Acharya  

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- University of Texas Arlington's Engineering Entrepreneurship Program
- Our mentors and advisors who guided us throughout this journey
- The open-source community for the amazing tools that made this possible
