from fpdf import FPDF
from datetime import date

from fpdf import FPDF
from datetime import date

class PDF(FPDF):
    def header(self):
        # Logo
        self.image('static/rhd-logo.png', 10, 8, 33)
        # Arial bold 16
        self.set_font('Times', 'B', 16)
        self.set_text_color(255,0,0)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Retinal Diseases Diagnosis Reports', 0, 0, 'C')
        
        # Times bold 12
        self.set_font('Times', 'B', 12)
        self.set_text_color(0,0,0)
        # Move to the left
        self.cell(-30)
        # Tag line
        self.cell(30, 27, 'Cataracts, Diabetic Retinopathy, Diabetic Macular Edema', 0, 0, 'C')
        
        # Move to the left
        self.cell(-110)
        # Add Date & Contact details
        self.set_font('Times', '', 12)
        self.cell(0, 50, 'Date: %s' % date.today().strftime("%b-%d-%Y"), 0, 0, 'L')
        self.cell(0, 50, "Shaik Nagur Shareef, Teja Krishna Cherukuri ", 0, 0, 'R')
        
        #draw line
        self.set_line_width(0.5)
        self.line(10, 40, 200, 40)
        
        # Line break
        self.ln(35)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Times', 'I', 9)
        self.set_text_color(0,0,0)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generate_report(name, gender, age, mobile, email, address, test, result, scan_path, r1, r2, observations):
    
    # Instantiation of inherited class
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.ln(2)

    # Set Caption Font
    pdf.set_font("Times",'B', size=14)
    pdf.set_text_color(0,0,255)
    # Caption
    pdf.cell(0, 5, "Patient Details",align="C", ln=1)
    pdf.ln(5)
    # Set Normal Font
    pdf.set_font("Times", size=12)
    pdf.set_text_color(0,0,0)

    
    space = "\t\t\t\t\t\t\t\t\t"
    patient_details_names = ["Name", "Gender", "Age", "Mobile", "Email Id", "Address"]
    patient_details_values = [name, gender, age, mobile, email, address]
    for i in range(len(patient_details_names)):
        pdf.cell(0, 10, patient_details_names[i].ljust(50, " ") + " : " + space + patient_details_values[i], 0, 1)

    pdf.ln(10)
    # Set Caption Font
    pdf.set_font("Times",'B', size=14)
    pdf.set_text_color(0,0,255)
    # Caption
    pdf.cell(0, 5, "Diagonosis Report",align="C", ln=1)
    pdf.ln(5)

    # Set Normal Font
    pdf.set_font("Times", size=12)
    pdf.set_text_color(0,0,0)

    diagnosis_details_names = ["Type of Test", "Diagnosis Result", "Observations", "Recommendation"]
    diagnosis_details_values = [test, result, observations, r2]
    for i in range(len(diagnosis_details_names)):
        pdf.cell(0, 10,diagnosis_details_names[i] + space + " : " + space + diagnosis_details_values[i], 0, 1)
        
    
    #add Scan Image
    pdf.set_text_color(255,0,0)
    
    # Add Scan & Processed Images
    clahe_path = "static/ProcessedImgs/CLAHE/"+name+".png"
    gradcam_path = "static/ProcessedImgs/GradCAM/"+name+".png"
    
    img_names = ["Scan Image", "CLAHE Processed Image", "Grad-CAM Visualization"]
    imgs_list = [scan_path, clahe_path, gradcam_path]
    for ind, img in enumerate(imgs_list):
        pdf.cell(0, 10,img_names[ind], 0, 2)
        pdf.image(img , x=60, w=85, h=80,)
        
    # Set Normal Font
    pdf.set_font("Times", size=10)
    pdf.set_text_color(0,0,0)
    pdf.ln(5)
    pdf.cell(0, 10,"Note: Correlate the information provided clinically, Write to 'rhd.reports@gmail.com' for any queries.", 0, 1)
    
    pdf.output("static/Reports/"+name+".pdf", "F")
