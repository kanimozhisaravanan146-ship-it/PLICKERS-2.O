
# PLICKERS-2.0
### Dynamic QR-Based Classroom Assessment System

## 1. Project Overview

PLICKERS-2.0 is a QR-based classroom assessment system designed to make classroom tests faster and easier.

The system allows teachers to conduct multiple-choice assessments by scanning students' QR cards using a single camera.

Unlike traditional individual QR scanning systems, PLICKERS-2.0 focuses on batch scanning, allowing multiple students to be identified in a single camera frame.

## 2. Problem Statement

Traditional classroom assessment systems may require teachers to scan students' response cards individually.

This process consumes time, especially when handling a large number of students.

PLICKERS-2.0 aims to overcome this limitation through multi-card QR detection and batch response processing.

## 3. Objectives

- Generate unique QR codes for students.
- Support a dynamic number of students.
- Detect multiple QR cards in a single camera frame.
- Identify student responses using marker orientation.
- Process and validate student answers.
- Store assessment results.
- Provide a teacher-friendly dashboard.

## 4. Key Features

### Dynamic QR Identification
Each student has a unique QR code for identification.

### Batch Scanning
The teacher can scan multiple student cards in one camera frame instead of scanning each card individually.

### Red Marker Orientation
The red marker acts as the reference point for identifying the selected answer.

Answer mapping:

| Marker Direction | Answer |
|---|---|
| Top | A |
| Right | B |
| Bottom | C |
| Left | D |

### Question Management
Teachers can manage questions and correct answers.

### Response Processing
Detected student responses are processed and validated.

### Result Management
Assessment results can be retrieved and displayed.

## 5. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Computer Vision | OpenCV |
| QR Code Generation | qrcode |
| Image Processing | NumPy |
| Frontend | HTML, CSS, JavaScript |
| Testing | Pytest |
| Database | SQLite (if configured) |

## 6. Project Structure

```text
PLICKERS-2.0/
│
├── scanner/
│   ├── __init__.py
│   ├── answer_decoder.py
│   ├── camera.py
│   ├── marker_detector.py
│   ├── multi_card_scanner.py
│   ├── qr_detector.py
│   └── scan_validation.py
│
├── services/
│   ├── __init__.py
│   ├── question_service.py
│   ├── response_processor.py
│   └── result_service.py
│
├── static/
│   ├── dashboard.js
│   ├── question_import.js
│   ├── scanner.js
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── questions.html
│   └── scanner.html
│
├── tests/
│   ├── test_answer_decoder.py
│   ├── test_marker_detector.py
│   ├── test_qr_detector.py
│   └── test_question_import.py
│
├── app.py
├── config.py
├── database.py
├── qr_generator.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 7. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

### Step 2: Navigate to the Project

```bash
cd PLICKERS-2.0
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 4: Activate the Environment

Windows:

```bash
venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run the Application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## 8. Testing

The project uses Pytest for testing individual modules.

Run all tests:

```bash
python -m pytest tests -v
```

Run a specific test:

```bash
python -m pytest tests/test_answer_decoder.py -v
```

## 9. Expected Outcome

PLICKERS-2.0 aims to provide a faster classroom assessment workflow by identifying multiple students and processing their answers through a single batch-scanning process.

The system is designed to support a dynamic number of students without restricting the classroom to a fixed student count.

## 10. Future Enhancements

- Improve multi-card detection accuracy.
- Optimize scanning speed.
- Add detailed assessment analytics.
- Support exportable student reports.
- Improve duplicate-response handling.

---

**Project:** PLICKERS-2.0  
**Category:** Educational Technology / Computer Vision  
**Backend:** Python Flask
