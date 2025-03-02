# Vessel Guard (Fitness For Service Level 1)

Vessel Guard is a Tkinter-based GUI application designed to assist engineers in calculating the pressure design thickness, corrosion rate, remaining life, and next inspection date of piping and pressure vessels based on ASME standards (ASME B31.3 for Piping and ASME VIII for Pressure Vessels). It also provides the ability to save the calculation history in a database and generate PDF reports for further documentation.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Future Enhancements](#future-enhancements)

## Features
- **GUI**: A user-friendly graphical interface built with Tkinter.
- **ASME Calculations**: Calculate the required thickness, corrosion rate, and inspection dates based on the ASME standards for Piping and Pressure Vessels.
- **Data Persistence**: Store calculation history in a database using SQLAlchemy.
- **PDF Reports**: Generate and save detailed reports in PDF format.
- **Reset Options**: Reset individual input fields or the entire form for new calculations.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone [https://github.com/your-repo/vessel-guard.git](https://github.com/ahmed-hesham07/Vessel-Guard-Fitness-For-Service-Level-1-.git)
    cd Vessel-Guard-Fitness-For-Service-Level-1-
    ```

2. **Create and Activate a Virtual Environment (Optional but Recommended)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Required Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

    The main dependencies are:
    - `Tkinter`
    - `SQLAlchemy`
    - `tkcalendar`
    - `FPDF`
    - `pytz`
    - `babel`

4. **Setup Database**:
    Ensure the `DATABASE_URL` environment variable is set up in your environment or configure the default database connection string in the script.

    ```bash
    export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@URL:PORT/DATABASENAME" 
    ```

5. **Run the Application**:
    ```bash
    python main.py
    ```

## Usage

1. **Launch the Application**:
    Upon running the application, you'll be presented with a form to input general information about the plant and equipment.
   
2. **Select Equipment Type**:
    Choose either "Piping" or "Pressure Vessel" from the dropdown menu. The app will then guide you to the appropriate calculation screen based on the selection.

3. **Input Parameters**:
    Enter the required parameters such as Design Pressure, Diameter, Stress, Corrosion Allowance, and other variables.

4. **Perform Calculation**:
    Press the **Calculate** button to compute the required thickness, corrosion rate, remaining life, and next inspection year.

5. **Save Results**:
    The results will be displayed on the screen, saved to the database, and can also be saved as a PDF report.

6. **Reset**:
    You can reset the form using the **Reset Readings** or **Reset All** buttons.

## Screenshots

### Plant Information Form
![Plant Information](screenshots/plant_info.png)

### Piping Calculation
![Piping Calculation](screenshots/piping_calculation.png)

### Pressure Vessel Calculation
![Pressure Vessel Calculation](screenshots/pv_calculation.png)

## Report
![Report #1](screenshots/piping-P-5674.pdf)


## Project Structure

```bash
Vessel-Guard-Fitness-For-Service-Level-/
│
├── ASME_B31_3.py             # Main script to run the application
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── screenshots/              # Folder to store screenshots for documentation
