<h1 align="center">🔍 Image Analyzer</h1>

<p align="center">
  A professional forensic image analysis tool for extracting metadata, inspecting image properties, generating hashes, analyzing visual characteristics, and detecting potential manipulation.
</p>

<p align="center">
  <a href="https://image-analyzer-by-hidden-rhythm.vercel.app/">
    <strong>🚀 Open Live Website</strong>
  </a>
  &nbsp;&nbsp;·&nbsp;&nbsp;
  <a href="https://github.com/Hidden-Rhythm/image-analyzer">
    View Source
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0.3-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/Pillow-10.3.0-3776AB?style=flat-square" alt="Pillow">
  <img src="https://img.shields.io/badge/OpenCV-4.9.0-5C3EE8?style=flat-square&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/Vercel-Deployed-000000?style=flat-square&logo=vercel&logoColor=white" alt="Vercel">
</p>

<br>

## 🧩 What It Does

**Image Analyzer** turns an uploaded image into a detailed technical report.

It combines image metadata extraction, cryptographic hashing, color statistics, GPS detection, and basic manipulation analysis into a single web interface.

The application is built with Flask on the backend and a responsive, glassmorphism-style frontend.

---

## ✨ Features

| Feature                      | Description                                                            |
| ---------------------------- | ---------------------------------------------------------------------- |
| 📤 **Image Upload**          | Upload images through a drag-and-drop interface or file picker         |
| 📊 **Basic Analysis**        | File size, format, dimensions, color mode, aspect ratio and timestamps |
| 📋 **EXIF Metadata**         | Extract camera, software, date, exposure and other available metadata  |
| 📍 **GPS Extraction**        | Detect embedded GPS coordinates when available                         |
| 🗺️ **Interactive Map**      | Generate a map from detected GPS coordinates                           |
| 🔐 **File Hashing**          | Generate MD5, SHA-1, SHA-256 and SHA-512 hashes                        |
| 🎨 **Color Analysis**        | Calculate mean RGB values, brightness, entropy and RGB deviation       |
| 🔬 **Manipulation Analysis** | Perform ELA-based analysis and inspect metadata-based warnings         |
| 🔎 **Reverse Search Links**  | Quickly access external reverse-image-search services                  |
| 📄 **JSON Results**          | Store and expose analysis results as structured JSON                   |
| 🖨️ **Report View**          | Present the collected analysis in a dedicated results page             |
| 📱 **Responsive UI**         | Designed to work across desktop and mobile screens                     |

---

## 🔬 Analysis Pipeline

The application processes an image through several stages:

```text
                    ┌─────────────────┐
                    │   Upload Image  │
                    └────────┬────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Load & Validate   │
                  └──────────┬──────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ Basic Info  │    │ EXIF / GPS  │    │ File Hashes │
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Color Analysis    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Manipulation Check  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Results Report    │
                  └─────────────────────┘
```

---

## 📊 What Gets Analyzed

### Basic Information

The analyzer collects information such as:

* Filename
* File size
* Image format
* Color mode
* Width and height
* Aspect ratio
* File timestamps
* Animation status
* Number of frames

### EXIF Metadata

When available, metadata can include:

* Camera manufacturer
* Camera model
* Software
* Date/time information
* Exposure settings
* ISO
* Aperture
* Focal length
* Metering mode
* Flash information
* Image dimensions

### GPS Data

If an image contains GPS EXIF data, the application can extract:

```text
Latitude
Longitude
Latitude Reference
Longitude Reference
```

The coordinates can then be visualized on an interactive map.

### Cryptographic Hashes

Each uploaded image can be fingerprinted using:

```text
MD5
SHA-1
SHA-256
SHA-512
```

These hashes can be useful for identifying whether two files are byte-for-byte identical.

### Color Analysis

The analyzer calculates:

* Mean RGB values
* Brightness
* Image entropy
* RGB standard deviation

### Manipulation Analysis

The application performs a basic **Error Level Analysis (ELA)** workflow when OpenCV is available.

It also checks for signals such as:

* Editing software recorded in metadata
* High entropy
* Elevated ELA score
* Availability of OpenCV-based analysis

The result includes a calculated confidence value and warnings.

> **Note:** manipulation detection is heuristic, not definitive forensic proof. A high score or warning should be treated as an indicator for further investigation rather than a conclusion that an image is fake.

---

## 🎨 Interface

The frontend uses a dark, glassmorphism-inspired interface with:

* Animated background effects
* Glass cards
* Gradient controls
* Interactive upload area
* Animated loading states
* Responsive layouts
* Result statistics
* Metadata tables
* Hash copy controls
* Warning indicators
* Interactive result sections

The interface is designed to keep a fairly technical analysis tool approachable and visually polished.

---

## 🛠️ Tech Stack

| Technology     | Purpose                        |
| -------------- | ------------------------------ |
| **Python**     | Application backend            |
| **Flask**      | Web framework                  |
| **Pillow**     | Image loading and analysis     |
| **piexif**     | EXIF/GPS extraction            |
| **ExifRead**   | Additional metadata extraction |
| **OpenCV**     | Image manipulation analysis    |
| **NumPy**      | Numerical image processing     |
| **Folium**     | Interactive GPS maps           |
| **HTML5**      | Page structure                 |
| **CSS3**       | UI and animations              |
| **JavaScript** | Client-side interaction        |
| **Bootstrap**  | Responsive UI components       |
| **Vercel**     | Deployment                     |

---

## 📁 Project Structure

```text
image-analyzer/
│
├── 📄 app.py
├── 📄 requirements.txt
├── 📄 .gitignore
├── 📄 README.md
│
├── 📁 api/
│   └── index.py
│
├── 📁 templates/
│   ├── 404.html
│   ├── 500.html
│   ├── base.html
│   ├── index.html
│   └── results.html
│
└── 📁 static/
    ├── 📁 css/
    │   └── style.css
    │
    └── 📁 js/
        └── main.js
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Hidden-Rhythm/image-analyzer.git
cd image-analyzer
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python app.py
```

The local server will be available at:

```text
http://127.0.0.1:5000
```

---

## 📦 Dependencies

The project currently uses:

```text
Flask==3.0.3
Pillow==10.3.0
piexif==1.1.3
exifread==3.0.0
opencv-python-headless==4.9.0.80
numpy==1.26.4
folium==0.16.0
```

---

## 🔐 Privacy & Security

Images uploaded for analysis are processed by the application and temporarily stored during the analysis workflow.

Because image metadata can contain sensitive information — particularly **GPS coordinates, camera information and timestamps** — avoid uploading images containing information you do not want processed.

The application is intended as an analysis utility, not as a guarantee of forensic authenticity.

---

## 🚀 Live

<p align="center">
  <a href="https://image-analyzer-by-hidden-rhythm.vercel.app/">
    <strong>🔍 Try Image Analyzer</strong>
  </a>
</p>

<p align="center">
  Analyze an image. Inspect the data. Find what's hidden inside.
</p>

---

## 👤 Author

<p align="center">
  Built by <strong>Hidden-Rhythm</strong>.
</p>

<br>

<p align="center">
  <strong>🔍 Inspect the image. Understand the data.</strong>
</p>
