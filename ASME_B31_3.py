import os
from tkinter import ttk
from tkcalendar import DateEntry
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename
from fpdf import FPDF
from datetime import datetime
import pytz
import babel
import babel.numbers
import babel.dates
import babel.core
import babel.localedata
import babel.messages
import babel.support
import babel.util
import babel.plural

print(babel.__version__)

# Database setup
Base = declarative_base()

class HistoryPiping(Base):
    __tablename__ = 'history_piping'
    id = Column(Integer, primary_key=True)
    plant_id = Column(String(50), nullable=False)
    equipment_num = Column(String(50), nullable=False)
    equipment_name = Column(String(100), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
    name = Column(String(50), nullable=False)
    p = Column(Float, nullable=False)
    d = Column(Float, nullable=False)
    s = Column(Float, nullable=False)
    e = Column(Float, nullable=False)
    c = Column(Float, nullable=False)
    t = Column(Float, nullable=False)
    tm = Column(Float, nullable=False)
    t_int = Column(Float, nullable=False)
    t_act = Column(Float, nullable=False)
    time_years = Column(Integer, nullable=False)
    corrosion_rate = Column(Float, nullable=False)
    corrosion_type = Column(String(50), nullable=False)
    remaining_life = Column(Float, nullable=False)
    next_inspection_year = Column(Integer, nullable=False)
    inspection_interval = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class Historypv(Base):
    __tablename__ = 'history_pv'
    id = Column(Integer, primary_key=True)
    plant_id = Column(String(50), nullable=False)
    equipment_num = Column(String(50), nullable=False)
    equipment_name = Column(String(100), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
    name = Column(String(50), nullable=False)
    p = Column(Float, nullable=False)
    r = Column(Float, nullable=False)
    s = Column(Float, nullable=False)
    e = Column(Float, nullable=False)
    c = Column(Float, nullable=False)
    t = Column(Float, nullable=False)
    tm = Column(Float, nullable=False)
    t_int = Column(Float, nullable=False)
    t_act = Column(Float, nullable=False)
    time_years = Column(Integer, nullable=False)
    corrosion_rate = Column(Float, nullable=False)
    corrosion_type = Column(String(50), nullable=False)
    remaining_life = Column(Float, nullable=False)
    next_inspection_year = Column(Integer, nullable=False)
    inspection_interval = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)

# Connect to the database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://USER:PASSWORD@URL:PORT/DATABASENAME")

# Handle database connection
try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    print("Connection successful!")
except SQLAlchemyError as e:
    messagebox.showerror("Database Connection Error", f"Could not connect to the database. Error: {str(e)}")
    raise

cairo_tz = pytz.timezone('Africa/Cairo')

def reset_readings():
    # Resets the readings inputs
    global entry_R_PV, entry_D, entry_P, entry_S, entry_E, entry_c, entry_t_int, entry_t_act, entry_time, inspection_interval_var, entry_P_PV, entry_D_PV, entry_R_PV, entry_S_PV, entry_E_PV, entry_c_PV, entry_t_int_PV, entry_t_act_PV, entry_time_PV, inspection_interval_PV_var
    entry_P.delete(0, tk.END)
    entry_P_PV.delete(0, tk.END)
    entry_D.delete(0, tk.END)
    entry_R_PV.delete(0, tk.END)
    entry_S.delete(0, tk.END)
    entry_S_PV.delete(0, tk.END)
    entry_E.delete(0, tk.END)
    entry_E_PV.delete(0, tk.END)
    entry_c.delete(0, tk.END)
    entry_c_PV.delete(0, tk.END)
    entry_t_int.delete(0, tk.END)
    entry_t_int_PV.delete(0, tk.END)
    entry_t_act.delete(0, tk.END)
    entry_t_act_PV.delete(0, tk.END)
    entry_time.delete(0, tk.END)
    entry_time_PV.delete(0, tk.END)
    corr_type_var.set('')
    corr_type_PV_var.set('')
    inspection_interval_var.set('')
    inspection_interval_PV_var.set('')
    label_result.config(text="")
    label_result_PV.config(text="")

def reset_all():
    # Reset the entire form, including Plant ID and Equipment details
    reset_readings()  # Clear the readings
    entry_plant_id.delete(0, tk.END)
    entry_equipment_name.delete(0, tk.END)
    entry_equipment_num.delete(0, tk.END)
    equipment_type_var.set('')  # Reset the equipment type dropdown
    entry_name.delete(0, tk.END)
    date_entry.set_date(datetime.now())  # Reset the date to today
    switch_frame(plant_info_frame)  # Switch back to the first frame

# Utility functions for calculations
def calculate_piping(P, D, S, E, c, t_int, t_act, time_years, W=1.0, Y=0.4):
    # Calculate pressure design thickness (t) and nominal thickness (tm) based on ASME B31.3
    t = (P * D) / (2 * (S * E * W) + (P * Y))
    tm = t + c
    corr_rate = (t_int - t_act) / time_years
    return t, tm, corr_rate

def calculate_PV(P, R, S, E, c, t_int, t_act, time_years):
    # Calculate pressure design thickness (t) and nominal thickness (tm) based on ASME VIII
    t = (P * R) / ((S * E) - (0.6 * P))
    tm = t + c  # c is corrosion allowance
    corr_rate = (t_int - t_act) / time_years
    return t, tm, corr_rate

def calculate_remaining_life(t, t_act, corr_rate):
    # Calculate the remaining life of the equipment
    return (t_act - t) / corr_rate

def generate_next_inspection_year(remaining_life):
    # Calculate the next inspection date based on the remaining life and inspection interval
    return remaining_life / 2

# PDF generation utilities
class PDFReport(FPDF):
    def __init__(self, equipment_type_var, plant_info, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equipment_type = equipment_type_var.get()
        self.plant_info = plant_info  # Storing plant_info as an instance variable

    def header(self):
        self.set_font("Helvetica", "B", 12)

        # Title aligned to the left
        self.cell(0, 10, "Plant Information Report", 0, 0, "L")

        # Move to the right to place the author name
        self.set_x(-50)  # Adjust this value based on the length of the text

        # Author name aligned to the right
        self.cell(0, 10, f"{self.plant_info['name']}", 0, 1, "R")

        self.ln(5)


    def footer(self):
        # Custom footer with page number
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "L")
        self.cell(0, 10, f"{self.plant_info['date']}", 0, 0, "R")

    def chapter_title(self, title):
        # Title for each chapter/section
        self.set_font("Helvetica", "B", 16)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, "C", fill=True)
        self.ln(5)

    def chapter_body(self, body):
        # Body text for each chapter/section
        self.set_font("Helvetica", "", 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_plant_info(self, plant_info):
        # Add plant information to the PDF
        self.chapter_title("Plant Information")
        self.chapter_body(
            f"Plant ID: {plant_info['plant_id']}\n"
            f"Equipment Number: {plant_info['equipment_num']}\n"
            f"Equipment Name: {plant_info['equipment_name']}\n"
            f"Equipment Type: {plant_info['equipment_type']}\n"
            f"Date: {plant_info['date'].strftime('%Y-%m-%d')}\n"
        )

    def service_input(self, service_info):
        self.chapter_title("Service Information")
        if self.equipment_type == "Piping":
            self.chapter_body(
                f"Design Pressure (P): {service_info['p']} psi\n"
                f"Outside Diameter (D): {service_info['d']} inches\n"
                f"Allowable Stress (S): {service_info['s']} psi\n"
                f"Effective Length (E): {service_info['e']} inches\n"
                f"Corrosion Allowance (c): {service_info['c']} inches\n"
                f"Initial Thickness (initial t): {service_info['t_int']} inches\n"
                f"Actual Thickness (actual t): {service_info['t_act']} inches\n"
                f"Time (t): {service_info['time_years']} years\n"
                f"Corrosion Type: {service_info['corrosion_type']}\n"
            )
        elif self.equipment_type == "Pressure Vessel":
            self.chapter_body(
                f"Design Pressure (P): {service_info['p']} psi\n"
                f"Inside Radius (R): {service_info['r']} inches\n"
                f"Allowable Stress (S): {service_info['s']} psi\n"
                f"Joint Efficiency (E): {service_info['e']}\n"
                f"Corrosion Allowance (c): {service_info['c']} inches\n"
                f"Initial Thickness (initial t): {service_info['t_int']} inches\n"
                f"Actual Thickness (actual t): {service_info['t_act']} inches\n"
                f"Time (t): {service_info['time_years']} years\n"
                f"Corrosion Type: {service_info['corrosion_type']}\n"

            )

    def add_service_calculations(self, service_info):
        # Add service calculations to the PDF
        self.add_page()  # Add a new page before printing the readings
        self.chapter_title("Calculation Results")
        self.chapter_body(
            f"Pressure Design Thickness (t): {service_info['t']:.2f} inches\n"
            f"Nominal Thickness (tm): {service_info['tm']:.2f} inches\n"
            f"Corrosion Rate: {service_info['corrosion_rate']:.2f} inches/year\n"
            f"Remaining Life: {service_info['remaining_life']:.2f} years\n"
            f"Next Inspection Year: {service_info['next_inspection_year']}\n"

        )


def save_to_pdf(plant_info, service_info, equipment_type_var):
    try:
        # Ensure that equipment_type_var.get() returns a string
        equipment_type = str(equipment_type_var.get())
        if isinstance(equipment_type, dict):
            raise TypeError(f"Expected a string, but got a dictionary: {equipment_type}")

        equipment_num = plant_info['equipment_num']
        if isinstance(equipment_num, dict):
            raise TypeError(f"Expected a string or number, but got a dictionary: {equipment_num}")

        root = tk.Tk()
        root.withdraw()
        file_path = asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF as",
            initialfile=f"{equipment_type.lower()}-{str(equipment_num)}.pdf"
        )
        if not file_path:
            print("PDF generation cancelled by the user.")
            return

        pdf = PDFReport(equipment_type_var, plant_info)
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()

        pdf.add_plant_info(plant_info)
        pdf.service_input(service_info)
        pdf.add_service_calculations(service_info)

        pdf.output(file_path)
        print(f"PDF saved successfully as {file_path}")

    except Exception as e:
        messagebox.showerror("PDF Error", f"An error occurred while saving the PDF: {str(e)}")



# Function to handle the calculations and saving
def on_calculate_piping(entry_P, entry_D, entry_R, entry_S, entry_E, entry_c, entry_t_int, entry_t_act, entry_time, inspection_interval_var):
    # Calculate and display results based on the user input
    global corr_rate, remaining_life, next_inspection, t, tm, corr_type_var, next_inspection_year, equipment_type_var
    try:
        # Input validation
        if not entry_P.get().strip():
            raise ValueError("Design Pressure (P) is required.")
        if entry_D and not entry_D.get().strip():
            raise ValueError("Outside Diameter (D) is required for Piping.")
        if entry_R and not entry_R.get().strip():
            raise ValueError("Inside Radius (R) is required for Pressure Vessel.")
        if not entry_S.get().strip():
            raise ValueError("Allowable Stress (S) is required.")
        if not entry_E.get().strip():
            raise ValueError("Joint Efficiency (E) is required.")
        if not entry_c.get().strip():
            raise ValueError("Corrosion Allowance (c) is required.")
        if not entry_t_int.get().strip():
            raise ValueError("Initial Thickness (t_int) is required.")
        if not entry_t_act.get().strip():
            raise ValueError("Actual Thickness (t_act) is required.")
        if not entry_time.get().strip():
            raise ValueError("Time (years) is required.")
        if not corr_type_var.get().strip():
            raise ValueError("Corrosion Type is required.")
        if corr_type_var.get() not in ['Short-Term', 'Long-Term']:
            raise ValueError(f"Invalid corrosion_type: {corr_type_var.get()}")
        if not inspection_interval_var.get().strip():
            raise ValueError("Inspection Interval is required.")

        # Convert inputs to proper types
        p = float(entry_P.get())
        d = float(entry_D.get()) if entry_D else None
        r = float(entry_R.get()) if entry_R else None
        s = float(entry_S.get())
        e = float(entry_E.get())
        c = float(entry_c.get())
        t_act = float(entry_t_act.get())
        t_int = float(entry_t_int.get())
        time_years = int(entry_time.get())
        inspection_interval = int(inspection_interval_var.get())

        # Choose calculation based on equipment type
        if d is not None:  # Piping
            t, tm, corr_rate = calculate_piping(p, d, s, e, c, t_int, t_act, time_years, W=1.0, Y=0.4)
        elif r is not None:  # Pressure Vessel
            t, tm, corr_rate = calculate_PV(p, r, s, e, c, t_int, t_act, time_years)

        remaining_life = calculate_remaining_life(t, t_act, corr_rate)
        if remaining_life>inspection_interval or remaining_life==inspection_interval:
            remaining_life = inspection_interval
        else:
            remaining_life = remaining_life


        next_inspection_year = generate_next_inspection_year(remaining_life)
        if next_inspection_year>inspection_interval or next_inspection_year==inspection_interval:
            next_inspection_year = inspection_interval
        else:
            next_inspection_year = next_inspection_year

        # Display results
        result_text = (
            f"Pressure design thickness (t): {t:.5f} inches\n"
            f"Nominal required thickness (tm): {tm:.5f} inches\n"
            f"Corrosion rate: {corr_rate:.5f} inches/year\n"
            f"Remaining life: {remaining_life:.5f} years\n"
            f"Next Inspection Date: {next_inspection_year}\n"
        )
        label_result.config(text=result_text)

        # Save the history and report
        plant_info = {
            'plant_id': entry_plant_id.get(),
            'equipment_name': entry_equipment_name.get(),
            'equipment_num': entry_equipment_num.get(),
            'equipment_type': equipment_type_var.get(),
            'date': date_entry.get_date(),
            'name': entry_name.get()
        }
        service_info = {
            'p': p,
            'd': d if equipment_type_var.get() == "Piping" else None,
            'r': r if equipment_type_var.get() == "Pressure Vessel" else None,
            's': s,
            'e': e,
            't_int': t_int,
            't_act': t_act,
            'c': c,
            'inspection_interval': inspection_interval,
            't': t,
            'tm': tm,
            'corrosion_rate': corr_rate,
            'corrosion_type': corr_type_var.get(),
            'remaining_life': remaining_life,
            'next_inspection_year': next_inspection_year,
            'time_years': time_years
        }

        # Save the history in the database
        timestamp = datetime.now()
        new_history = HistoryPiping(
            name=plant_info['name'],
            plant_id=plant_info['plant_id'],
            equipment_num=plant_info['equipment_num'],
            equipment_name=plant_info['equipment_name'],
            equipment_type=plant_info['equipment_type'],
            date=plant_info['date'],
            p=p, d=d, s=s, e=e, c=c, t=t, tm=tm,
            t_int=t_int, t_act=t_act, corrosion_rate=corr_rate, corrosion_type=corr_type_var.get(), time_years=time_years,
            remaining_life=remaining_life, next_inspection_year=next_inspection_year,
            inspection_interval=inspection_interval, timestamp=timestamp
        )


        session.add(new_history)
        session.commit()

        # Save to PDF file
        save_to_pdf(plant_info, service_info, equipment_type_var)

    except ValueError as e:
        messagebox.showerror("Invalid input", f"Error: {str(e)}")
    except SQLAlchemyError as e:
        messagebox.showerror("Database Error", f"Error saving data to the database: {str(e)}")
        session.rollback()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

def on_calculate_PV(entry_P_PV, entry_D_PV, entry_R_PV, entry_S_PV, entry_E_PV, entry_c_PV, entry_t_int_PV, entry_t_act_PV, entry_time_PV, inspection_interval_PV_var):
    # Calculate and display results based on the user input
    global corr_rate, remaining_life, next_inspection, t, tm, corr_type_var, corr_type_PV_var, next_inspection_year, equipment_type_var
    try:
        # Input validation
        if not entry_P_PV.get().strip():
            raise ValueError("Design Pressure (P) is required.")
        if entry_R_PV and not entry_R_PV.get().strip():
            raise ValueError("Inside Radius (R) is required for Pressure Vessel.")
        if not entry_S_PV.get().strip():
            raise ValueError("Allowable Stress (S) is required.")
        if not entry_E_PV.get().strip():
            raise ValueError("Joint Efficiency (E) is required.")
        if not entry_c_PV.get().strip():
            raise ValueError("Corrosion Allowance (c) is required.")
        if not entry_t_int_PV.get().strip():
            raise ValueError("Initial Thickness (t_int) is required.")
        if not entry_t_act_PV.get().strip():
            raise ValueError("Actual Thickness (t_act) is required.")
        if not entry_time_PV.get().strip():
            raise ValueError("Time (years) is required.")
        if not corr_type_PV_var.get().strip():
            raise ValueError("Corrosion Type is required.")
        if corr_type_PV_var.get() not in ['Short-Term', 'Long-Term']:
            raise ValueError(f"Invalid corrosion_type: {corr_type_PV_var.get()}")
        if not inspection_interval_PV_var.get().strip():
            raise ValueError("Inspection Interval is required.")

        # Convert inputs to proper types
        p = float(entry_P_PV.get())
        r = float(entry_R_PV.get())
        s = float(entry_S_PV.get())
        e = float(entry_E_PV.get())
        c = float(entry_c_PV.get())
        t_act = float(entry_t_act_PV.get())
        t_int = float(entry_t_int_PV.get())
        time_years = int(entry_time_PV.get())
        inspection_interval = int(inspection_interval_PV_var.get())
        corr_type = str(corr_type_PV_var.get())

        t, tm, corr_rate = calculate_PV(p, r, s, e, c, t_int, t_act, time_years)

        remaining_life = calculate_remaining_life(t, t_act, corr_rate)

        next_inspection_year = generate_next_inspection_year(remaining_life)

        if next_inspection_year > inspection_interval or next_inspection_year == inspection_interval:
            next_inspection_year = inspection_interval
        else:
            next_inspection_year = next_inspection_year

        # Display results
        result_text_PV = (
            f"Pressure design thickness (t): {t:.5f} inches\n"
            f"Nominal required thickness (tm): {tm:.5f} inches\n"
            f"Corrosion rate: {corr_rate:.5f} inches/year\n"
            f"Remaining life: {remaining_life:.5f} years\n"
            f"Next Inspection Date: {next_inspection_year} years\n"
        )
        label_result.config(text=result_text_PV)

        # Save the history and report
        plant_info_PV = {
            'plant_id': entry_plant_id.get(),
            'equipment_name': entry_equipment_name.get(),
            'equipment_num': entry_equipment_num.get(),
            'equipment_type': equipment_type_var.get(),
            'date': date_entry.get_date(),
            'name': entry_name.get()
        }
        service_info_PV = {
            'p': p,
            'd': None,
            'r': r if equipment_type_var.get() == "Pressure Vessel" else None,
            's': s,
            'e': e,
            't_int': t_int,
            't_act': t_act,
            'c': c,
            'inspection_interval': inspection_interval,
            't': t,
            'tm': tm,
            'corrosion_rate': corr_rate,
            'corrosion_type': corr_type,
            'remaining_life': remaining_life,
            'next_inspection_year': next_inspection_year,
            'time_years': time_years
        }

        # Save the history in the database
        timestamp = datetime.now()
        new_history = Historypv(
            name=plant_info_PV['name'],
            plant_id=plant_info_PV['plant_id'],
            equipment_num=plant_info_PV['equipment_num'],
            equipment_name=plant_info_PV['equipment_name'],
            equipment_type=plant_info_PV['equipment_type'],
            date=plant_info_PV['date'],
            p=p, r=r, s=s, e=e, c=c, t=t, tm=tm,
            t_int=t_int, t_act=t_act, corrosion_rate=corr_rate, corrosion_type=corr_type, time_years=time_years,
            remaining_life=remaining_life, next_inspection_year=next_inspection_year,
            inspection_interval=inspection_interval, timestamp=timestamp
        )

        session.add(new_history)

        session.commit()

        # Save to PDF file
        save_to_pdf(plant_info_PV, service_info_PV, equipment_type_var)

    except ValueError as e:
        messagebox.showerror("Invalid input", f"Error: {str(e)}")
    except SQLAlchemyError as e:
        messagebox.showerror("Database Error", f"Error saving data to the database: {str(e)}")
        session.rollback()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

# GUI Setup
root = tk.Tk()
root.title("Vessel Guard")
root.geometry("600x600")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Container frame to hold all other frames
container = ttk.Frame(root)
container.grid(row=0, column=0, sticky="nsew")
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Create frames
plant_info_frame = ttk.Frame(container, padding="10 10 10 10")
plant_info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
PV_frame = ttk.Frame(container)
piping_frame = ttk.Frame(container)

# Place all frames in the same grid location
for frame in (plant_info_frame, PV_frame, piping_frame):
    frame.grid(row=0, column=0, sticky="nsew")

# Function to switch frames
def switch_frame(frame):
    frame.tkraise()

# Plant ID
title_label = ttk.Label(plant_info_frame, text="Plant Information", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

ttk.Label(plant_info_frame, text="Plant ID:").grid(row=1, column=0, padx=5, pady=5)
entry_plant_id = ttk.Entry(plant_info_frame, width=30)
entry_plant_id.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(plant_info_frame, text="Equipment Name:").grid(row=2, column=0, padx=5, pady=5)
entry_equipment_name = ttk.Entry(plant_info_frame, width=30)
entry_equipment_name.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(plant_info_frame, text="Equipment Number:").grid(row=3, column=0, padx=5, pady=5)
entry_equipment_num = ttk.Entry(plant_info_frame, width=30)
entry_equipment_num.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(plant_info_frame, text="Equipment Type:").grid(row=4, column=0, padx=5, pady=5)
equipment_type_var = tk.StringVar()
equipment_type_combobox = ttk.Combobox(
    plant_info_frame, textvariable=equipment_type_var,
    values=["Piping", "Pressure Vessel"], state="readonly", width=27
)
equipment_type_combobox.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(plant_info_frame, text="Date:").grid(row=5, column=0, padx=5, pady=5)
date_entry = DateEntry(plant_info_frame, width=28, background='darkblue',
                       foreground='white', borderwidth=2, year=datetime.now().year)
date_entry.grid(row=5, column=1, padx=5, pady=5)

ttk.Label(plant_info_frame, text="Author Name").grid(row=6, column=0, padx=5, pady=5)
entry_name = ttk.Entry(plant_info_frame, width=30)
entry_name.grid(row=6, column=1, padx=5, pady=5)

# Switch to appropriate frame based on equipment type
def on_next_button_click():
    equipment_type = equipment_type_var.get()
    if equipment_type == "Piping":
        switch_frame(piping_frame)
    elif equipment_type == "Pressure Vessel":
        switch_frame(PV_frame)
    else:
        messagebox.showwarning("Warning", "Please select an equipment type.")
    return equipment_type

# Next Button
next_button = ttk.Button(plant_info_frame, text="Next", command=on_next_button_click)
next_button.grid(row=7, column=0, columnspan=2, pady=10)

#-----------------------------------------------------------------------------------------------------------------

# Main Frame for Pressure Vessel
title_text = "ASME-VIII"
title_label = ttk.Label(PV_frame, text=title_text, font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

# Input fields for Pressure Vessel
ttk.Label(PV_frame, text="Design Pressure (P):").grid(row=2, column=0, padx=5, pady=5)
entry_P_PV = ttk.Entry(PV_frame)
entry_P_PV.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(PV_frame, text="Inside Radius (R):").grid(row=3, column=0, padx=5, pady=5)
entry_R_PV = ttk.Entry(PV_frame)
entry_R_PV.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(PV_frame, text="Allowable Stress (S):").grid(row=4, column=0, padx=5, pady=5)
entry_S_PV = ttk.Entry(PV_frame)
entry_S_PV.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(PV_frame, text="Joint Efficiency (E):").grid(row=5, column=0, padx=5, pady=5)
entry_E_PV = ttk.Entry(PV_frame)
entry_E_PV.grid(row=5, column=1, padx=5, pady=5)

ttk.Label(PV_frame, text="Corrosion Allowance (c):").grid(row=6, column=0, padx=5, pady=5)
entry_c_PV = ttk.Entry(PV_frame)
entry_c_PV.grid(row=6, column=1, padx=5, pady=5)

title_label = ttk.Label(PV_frame, text="Corrosion Rate", font=("Helvetica", 16, "bold"))
title_label.grid(row=8, column=0, columnspan=2, pady=(0, 15))

ttk.Label(PV_frame, text="Initial or Previous Thickness (inches):").grid(row=9, column=0, padx=5, pady=5)
entry_t_int_PV = ttk.Entry(PV_frame)
entry_t_int_PV.grid(row=9, column=1, padx=5, pady=5)

ttk.Label(PV_frame, text="Actual Thickness (inches):").grid(row=10, column=0, padx=5, pady=5)
entry_t_act_PV = ttk.Entry(PV_frame)
entry_t_act_PV.grid(row=10, column=1, padx=5, pady=5)

ttk.Label(PV_frame, text="Time (years):").grid(row=11, column=0, padx=5, pady=5)
entry_time_PV = ttk.Entry(PV_frame)
entry_time_PV.grid(row=11, column=1, padx=5, pady=5)

ttk.Label(PV_frame, text="Type of Corrosion rate:").grid(row=12, column=0, padx=5, pady=5)
corr_type_PV_var = tk.StringVar(value="Short-Term")
corr_type_PV_menu = ttk.Combobox(
    PV_frame, textvariable=corr_type_PV_var,
    values=['Long-Term', 'Short-Term'], state="readonly", width=27
)
corr_type_PV_menu.grid(row=12, column=1, padx=5, pady=5)

ttk.Label(PV_frame, text="Inspection Interval (years):").grid(row=13, column=0, padx=5, pady=5)
inspection_interval_PV_var = tk.StringVar(value="")
inspection_interval_PV_menu = ttk.Combobox(
    PV_frame, textvariable=inspection_interval_PV_var,
    values=["3", "5", "10", "15"], state="readonly", width=27
)
inspection_interval_PV_menu.grid(row=13, column=1, padx=5, pady=5)

# Result display for Pressure Vessel
label_result_PV = ttk.Label(PV_frame, text="")
label_result_PV.grid(row=14, column=0, columnspan=2, padx=10, pady=10)

# Calculate Button for Pressure Vessel
calculate_button = ttk.Button(
    PV_frame,
    text="Calculate",
    command=lambda: on_calculate_PV(entry_P_PV, None, entry_R_PV, entry_S_PV, entry_E_PV, entry_c_PV, entry_t_int_PV, entry_t_act_PV,
                                        entry_time_PV, inspection_interval_PV_var)
)
calculate_button.grid(row=15, column=0, columnspan=2, pady=10)

btn_reset_readings = tk.Button(root, text="Reset Readings", command=reset_readings)
btn_reset_readings.grid(row=16, column=1, padx=10, pady=10)

btn_reset_all = tk.Button(root, text="Reset All", command=reset_all)
btn_reset_all.grid(row=16, column=0, padx=10, pady=10)

btn_back = tk.Button(root, text="Back", command=lambda: switch_frame(plant_info_frame))
btn_back.grid(row=16, column=2, padx=10, pady=10)


#-----------------------------------------------------------------------------------------------------------------

# Main Frame for Piping
title_text = "ASME-B31.3"
title_label = ttk.Label(piping_frame, text=title_text, font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

# Input fields for Piping
ttk.Label(piping_frame, text="Design Pressure (P):").grid(row=2, column=0, padx=5, pady=5)
entry_P = ttk.Entry(piping_frame)
entry_P.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(piping_frame, text="Outside Diameter (D):").grid(row=3, column=0, padx=5, pady=5)
entry_D = ttk.Entry(piping_frame)
entry_D.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(piping_frame, text="Allowable Stress (S):").grid(row=4, column=0, padx=5, pady=5)
entry_S = ttk.Entry(piping_frame)
entry_S.grid(row=4, column=1, padx=5, pady=5)

ttk.Label(piping_frame, text="Joint Efficiency (E):").grid(row=5, column=0, padx=5, pady=5)
entry_E = ttk.Entry(piping_frame)
entry_E.grid(row=5, column=1, padx=5, pady=5)

ttk.Label(piping_frame, text="Corrosion Allowance (c):").grid(row=6, column=0, padx=5, pady=5)
entry_c = ttk.Entry(piping_frame)
entry_c.grid(row=6, column=1, padx=5, pady=5)

title_label = ttk.Label(piping_frame, text="Corrosion Rate", font=("Helvetica", 16, "bold"))
title_label.grid(row=8, column=0, columnspan=2, pady=(0, 15))

ttk.Label(piping_frame, text="Initial or Previous Thickness (inches):").grid(row=9, column=0, padx=5, pady=5)
entry_t_int = ttk.Entry(piping_frame)
entry_t_int.grid(row=9, column=1, padx=5, pady=5)

ttk.Label(piping_frame, text="Actual Thickness (inches):").grid(row=10, column=0, padx=5, pady=5)
entry_t_act = ttk.Entry(piping_frame)
entry_t_act.grid(row=10, column=1, padx=5, pady=5)

ttk.Label(piping_frame, text="Time (years):").grid(row=11, column=0, padx=5, pady=5)
entry_time = ttk.Entry(piping_frame)
entry_time.grid(row=11, column=1, padx=5, pady=5)

ttk.Label(piping_frame, text="Type of Corrosion rate:").grid(row=12, column=0, padx=5, pady=5)
corr_type_var = tk.StringVar(value="Short-Term")
corr_type_menu = ttk.Combobox(
    piping_frame, textvariable=corr_type_var,
    values=["Short-Term", "Long-Term"], state="readonly", width=27
)
corr_type_menu.grid(row=12, column=1, padx=5, pady=5)

ttk.Label(piping_frame, text="Inspection Interval (years):").grid(row=13, column=0, padx=5, pady=5)
inspection_interval_var = tk.StringVar(value="")
inspection_interval_menu = ttk.Combobox(
    piping_frame, textvariable=inspection_interval_var,
    values=["3", "5", "10", "15"], state="readonly", width=27
)
inspection_interval_menu.grid(row=13, column=1, padx=5, pady=5)

# Result display for Piping
label_result = ttk.Label(piping_frame, text="")
label_result.grid(row=14, column=0, columnspan=2, padx=10, pady=10)

# Calculate Button for Piping
calculate_button = ttk.Button(
    piping_frame,
    text="Calculate",
    command=lambda: on_calculate_piping(entry_P, entry_D, None, entry_S, entry_E, entry_c, entry_t_int, entry_t_act,
                                        entry_time, inspection_interval_var)
)
calculate_button.grid(row=15, column=0, columnspan=2, pady=10)


# Initially show the plant_info_frame
switch_frame(plant_info_frame)
# Start the Tkinter event loop
root.mainloop()