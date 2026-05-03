# Integrated AI-Powered Parking Management System

## Overview
This is a comprehensive parking management system built with Django and powered by AI. It automates the parking process using computer vision, specifically leveraging YOLOv5 for real-time license plate detection and Optical Character Recognition (OCR).

The system seamlessly manages parking slot allocation, tracks vehicle entry and exit times, calculates parking fees based on duration, and generates transaction receipts.

## Key Features
- **AI-Powered License Plate Recognition (ALPR):** Utilizes custom-trained YOLOv5 models to detect license plates (`LP_detector.pt`) and read alphanumeric characters (`LP_ocr.pt`) with high accuracy.
- **Automated Entry & Exit Management:** 
  - On entry: Automatically detects the license plate, finds an available parking slot, and logs the entry time.
  - On exit: Recognizes the plate again, calculates the total parked duration, and frees up the slot.
- **Dynamic Pricing & Billing:** Calculates parking fees dynamically based on the duration of the stay (e.g., varying rates for different hourly slabs).
- **Real-Time Slot Monitoring:** Provides a dashboard to view available and occupied parking slots.
- **Transaction History & Receipts:** Keeps a record of all parking transactions and generates digital receipts for users.

## Tech Stack
- **Backend:** Python, Django
- **Database:** SQLite (default Django configuration)
- **AI/Computer Vision:** PyTorch, YOLOv5, OpenCV, NumPy
- **Frontend:** HTML, CSS, JavaScript (Django Templates)

## Project Structure
- `lpproject/`: Core Django project settings and routing.
- `lpapp/`: Main Django application containing models, views, and business logic.
  - `models.py`: Defines database schemas for `LicensePlate`, `ParkingSlot`, `ParkingTransaction`, and `Transaction`.
  - `views.py`: Contains logic for image processing, ALPR inference, and transaction management.
  - `model/`: Directory storing the PyTorch models (`LP_detector.pt` and `LP_ocr.pt`).
  - `function/`: Helper functions for image deskewing and reading plates.
- `templates/`: HTML templates for the user interface.
- `media/`: Stores captured images and cropped license plates.
- `static/`: Contains static assets like CSS and JS files.
- `yolov5/`: YOLOv5 repository/dependencies.

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Create a Virtual Environment (Optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   Make sure you have Python installed. You will need to install Django, PyTorch, OpenCV, and other requirements.
   *(Note: Ensure you have the appropriate PyTorch version installed for your system, especially if you plan to use GPU acceleration).*
   ```bash
   pip install django torch torchvision torchaudio opencv-python pandas numpy
   ```

4. **Apply Database Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application:**
   Open your web browser and navigate to `http://127.0.0.1:8000/`.

## Note on Models
This application relies on custom YOLOv5 weights (`LP_detector.pt` and `LP_ocr.pt`). Ensure these models are correctly placed within the `lpapp/model/` directory for the system to function correctly.
