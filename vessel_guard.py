# vessel_guard.py
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fpdf import FPDF
from datetime import datetime
import pytz

# Configuration Constants
DATABASE_URL = "sqlite:///vessel_guard.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TIMEZONE = pytz.timezone('Africa/Cairo')
INSPECTION_INTERVALS = ["3", "5", "10", "15"]
CORROSION_TYPES = ['Short-Term', 'Long-Term']

# Database Setup
Base = declarative_base()

class EquipmentHistory(Base):
    __tablename__ = 'equipment_history'
    id = Column(Integer, primary_key=True)
    plant_id = Column(String(50), nullable=False)
    equipment_num = Column(String(50), nullable=False)
    equipment_name = Column(String(100), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
    author = Column(String(50), nullable=False)
    design_pressure = Column(Float, nullable=False)
    diameter_radius = Column(Float)
    allowable_stress = Column(Float, nullable=False)
    joint_efficiency = Column(Float, nullable=False)
    corrosion_allowance = Column(Float, nullable=False)
    initial_thickness = Column(Float, nullable=False)
    actual_thickness = Column(Float, nullable=False)
    time_years = Column(Integer, nullable=False)
    corrosion_rate = Column(Float, nullable=False)
    corrosion_type = Column(String(50), nullable=False)
    remaining_life = Column(Float, nullable=False)
    next_inspection = Column(Integer, nullable=False)
    inspection_interval = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vessel Guard")
        self.geometry("800x680")
        self.configure(bg="#F4F4F4")
        
        # Custom theme configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.configure_styles()
        
        # Database setup
        self.session = self.init_db()
        self.current_frame = None
        self.create_widgets()

    def configure_styles(self):
        colors = {
            "background": "#F4F4F4",
            "frame": "#FFFFFF",
            "text": "#333333",
            "button": "#007BFF",
            "button_text": "#FFFFFF",
            "entry_bg": "#E9ECEF",
            "entry_fg": "#333333",
            "highlight": "#0056b3"
        }
        self.style.configure(".", font=("Segoe UI", 12))
        self.style.configure("TFrame", background=colors["frame"])
        self.style.configure("TLabel", background=colors["frame"], foreground=colors["text"])
        self.style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"], insertcolor=colors["entry_fg"], bordercolor=colors["button"], lightcolor=colors["button"], darkcolor=colors["button"])
        self.style.configure("TCombobox", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"], background=colors["entry_bg"])
        self.style.configure("TButton", background=colors["button"], foreground=colors["button_text"], font=("Segoe UI", 12, "bold"), borderwidth=0)
        self.style.map("TButton", background=[("active", colors["highlight"])])
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground=colors["button"])
        self.style.configure("Secondary.TFrame", background=colors["background"])
        self.option_add("*TButton*Padding", (20, 8))
        self.option_add("*TEntry*Padding", (8, 4))
        self.option_add("*TCombobox*Padding", (8, 4))

    def init_db(self):
        try:
            Base.metadata.create_all(engine)
            return sessionmaker(bind=engine)()
        except SQLAlchemyError as e:
            messagebox.showerror("Database Error", f"Failed to connect to database: {str(e)}")
            raise

    def create_widgets(self):
        self.container = ttk.Frame(self, padding=20, style="Secondary.TFrame")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.frames = {
            "plant_info": PlantInfoFrame(self.container, self),
            "piping": CalculationFrame(self.container, self, "Piping"),
            "vessel": CalculationFrame(self.container, self, "Vessel")
        }
        self.show_frame("plant_info")

    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.grid_remove()
        self.current_frame = self.frames[name]
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame.tkraise()

class PlantInfoFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20, style="TFrame")
        self.controller = controller
        self.create_widgets()

    def get_plant_data(self):
        return {
            "plant_id": self.entries["plant_id"].get(),
            "equipment_name": self.entries["equipment_name"].get(),
            "equipment_num": self.entries["equipment_num"].get(),
            "author": self.entries["author"].get(),
            "equipment_type": self.equipment_type.get(),
            "date": self.date_entry.get_date()
        }

    def create_widgets(self):
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        ttk.Label(header_frame, text="Plant Information", style="Header.TLabel").pack(pady=10)
        
        input_frame = ttk.Frame(self, style="TFrame")
        input_frame.grid(row=1, column=0, sticky="nsew")
        fields = [
            ("Plant ID", "plant_id"),
            ("Equipment Name", "equipment_name"),
            ("Equipment Number", "equipment_num"),
            ("Author Name", "author"),
        ]
        self.entries = {}
        for row, (label, name) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=8)
            entry = ttk.Entry(input_frame)
            entry.grid(row=row, column=1, padx=10, pady=8, sticky="ew")
            self.entries[name] = entry
        
        ttk.Label(input_frame, text="Equipment Type").grid(row=4, column=0, sticky="w", padx=10, pady=8)
        self.equipment_type = ttk.Combobox(input_frame, values=["Piping", "Pressure Vessel"], state="readonly")
        self.equipment_type.grid(row=4, column=1, padx=10, pady=8, sticky="ew")
        
        ttk.Label(input_frame, text="Date").grid(row=5, column=0, sticky="w", padx=10, pady=8)
        self.date_entry = DateEntry(input_frame)
        self.date_entry.grid(row=5, column=1, padx=10, pady=8, sticky="ew")
        
        button_frame = ttk.Frame(self, style="TFrame")
        button_frame.grid(row=2, column=0, pady=20)
        ttk.Button(button_frame, text="Next →", command=self.next_screen).pack(side="right", padx=10)
        self.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)

    def next_screen(self):
        if not self.equipment_type.get():
            messagebox.showwarning("Warning", "Please select equipment type.")
            return
        frame_name = "piping" if self.equipment_type.get() == "Piping" else "vessel"
        self.controller.show_frame(frame_name)

class CalculationFrame(ttk.Frame):
    def __init__(self, parent, controller, equip_type):
        super().__init__(parent, padding=20, style="TFrame")
        self.controller = controller
        self.equip_type = equip_type
        self.input_fields = []
        self.create_widgets()

    def create_widgets(self):
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        title = f"ASME {'B31.3' if self.equip_type == 'Piping' else 'VIII'}"
        ttk.Label(header_frame, text=title, style="Header.TLabel").pack(pady=10)
        
        input_frame = ttk.Frame(self, style="TFrame")
        input_frame.grid(row=1, column=0, sticky="nsew")
        fields = [
            ("Design Pressure (psi)", "design_pressure"),
            ("Outside Diameter" if self.equip_type == "Piping" else "Inside Radius", "diameter_radius"),
            ("Allowable Stress (psi)", "allowable_stress"),
            ("Joint Efficiency", "joint_efficiency"),
            ("Corrosion Allowance", "corrosion_allowance"),
            ("Initial Thickness", "initial_thickness"),
            ("Actual Thickness", "actual_thickness"),
            ("Time (years)", "time_years"),
        ]
        for row, (label, field) in enumerate(fields):
            ttk.Label(input_frame, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=6)
            entry = ttk.Entry(input_frame)
            entry.grid(row=row, column=1, padx=10, pady=6, sticky="ew")
            self.input_fields.append((field, entry))
        
        bottom_frame = ttk.Frame(self, style="TFrame")
        bottom_frame.grid(row=2, column=0, sticky="ew", pady=20)
        ttk.Label(bottom_frame, text="Corrosion Type:").grid(row=0, column=0, sticky="w", padx=10)
        self.corr_type = ttk.Combobox(bottom_frame, values=CORROSION_TYPES, state="readonly")
        self.corr_type.grid(row=0, column=1, padx=10, sticky="ew")
        
        ttk.Label(bottom_frame, text="Inspection Interval:").grid(row=1, column=0, sticky="w", padx=10)
        self.inspection = ttk.Combobox(bottom_frame, values=INSPECTION_INTERVALS, state="readonly")
        self.inspection.grid(row=1, column=1, padx=10, sticky="ew")
        
        button_frame = ttk.Frame(self, style="TFrame")
        button_frame.grid(row=3, column=0, sticky="ew")
        ttk.Button(button_frame, text="← Back", command=lambda: self.controller.show_frame("plant_info")).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Calculate →", command=self.calculate).pack(side="right", padx=10)
        self.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

    def calculate(self):
        try:
            data = {field: float(entry.get()) for field, entry in self.input_fields}
            data.update({
                'corrosion_type': self.corr_type.get(),
                'inspection_interval': int(self.inspection.get())
            })
            
            if self.equip_type == "Piping":
                design_thickness = (data['design_pressure'] * data['diameter_radius']) / (2 * (data['allowable_stress'] * data['joint_efficiency']))
            else:
                design_thickness = (data['design_pressure'] * data['diameter_radius']) / (data['allowable_stress'] * data['joint_efficiency'] - 0.6 * data['design_pressure'])
            
            nominal_thickness = design_thickness + data['corrosion_allowance']
            corrosion_rate = (data['initial_thickness'] - data['actual_thickness']) / data['time_years']
            remaining_life = max(0, (data['actual_thickness'] - design_thickness) / corrosion_rate)
            next_inspection = min(remaining_life / 2, data['inspection_interval'])
            
            history = EquipmentHistory(
                **self.controller.frames["plant_info"].get_plant_data(),
                timestamp=datetime.now(TIMEZONE),
                **data,
                pressure_design_thickness=design_thickness,
                nominal_thickness=nominal_thickness,
                corrosion_rate=corrosion_rate,
                remaining_life=remaining_life,
                next_inspection=next_inspection
            )
            
            self.controller.session.add(history)
            self.controller.session.commit()
            self.generate_pdf(data, design_thickness, nominal_thickness, corrosion_rate, remaining_life, next_inspection)
            messagebox.showinfo("Success", "Calculation completed and data saved!")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
        except SQLAlchemyError as e:
            self.controller.session.rollback()
            messagebox.showerror("Database Error", f"Failed to save data: {str(e)}")

    def generate_pdf(self, data, design_thickness, nominal_thickness, corrosion_rate, remaining_life, next_inspection):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        plant_data = self.controller.frames["plant_info"].get_plant_data()
        pdf.cell(0, 10, f"Plant ID: {plant_data['plant_id']}", ln=1)
        pdf.cell(0, 10, f"Equipment: {plant_data['equipment_name']} ({plant_data['equipment_num']})", ln=1)
        pdf.cell(0, 10, "Calculation Results:", ln=1)
        pdf.cell(0, 10, f"Design Thickness: {design_thickness:.2f} inches", ln=1)
        pdf.cell(0, 10, f"Nominal Thickness: {nominal_thickness:.2f} inches", ln=1)
        pdf.cell(0, 10, f"Corrosion Rate: {corrosion_rate:.4f} inches/year", ln=1)
        pdf.cell(0, 10, f"Remaining Life: {remaining_life:.1f} years", ln=1)
        pdf.cell(0, 10, f"Next Inspection: {next_inspection:.1f} years", ln=1)
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{self.equip_type.lower()}_report.pdf"
        )
        if filename:
            pdf.output(filename)
            messagebox.showinfo("PDF Saved", f"Report saved to:\n{filename}")

if __name__ == "__main__":
    app = Application()
    app.mainloop()