from fpdf import FPDF
from datetime import date
from io import BytesIO
from fpdf import FPDF
from datetime import date
from aws.aws_utils import AWSUtils
from PIL import Image
import tempfile

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

def generate_report(name, image_name, gender, age, mobile, email, address, test, result, scan_path, r1, r2, observations):
    
    filename = name + '_' + image_name
    try: 
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
  
       # Load Scan Image from S3
        scan_img = AWSUtils.load_file_from_s3(scan_path)

        if scan_img:
            with tempfile.NamedTemporaryFile(suffix=".jpeg") as temp_file:
                img = Image.open(BytesIO(scan_img.read()))
                img = img.resize((85, 80))
                img.save(temp_file, format='JPEG')
                temp_file.seek(0)
                pdf.ln(5)
                pdf.cell(0, 10, "Scan Image", 0, 2)
                pdf.image(temp_file.name, x=60, y=None, w=85, h=80)

        # Load CLAHE Processed Image from S3
        clahe_path = f"static/processed_imgs/CLAHE/{filename}.png"
        clahe_img = AWSUtils.load_file_from_s3(clahe_path)

        if clahe_img:
            with tempfile.NamedTemporaryFile(suffix=".jpeg") as temp_file:
                img = Image.open(BytesIO(clahe_img.read()))
                img = img.resize((85, 80))
                img.save(temp_file, format='JPEG')
                temp_file.seek(0)
                pdf.ln(5)
                pdf.cell(0, 10, "CLAHE Image", 0, 2)
                pdf.image(temp_file.name, x=60, y=None, w=85, h=80)

        # Load Grad-CAM Visualization from S3
        gradcam_path = f"static/processed_imgs/GradCAM/{filename}.png"
        gradcam_img = AWSUtils.load_file_from_s3(gradcam_path)
        if gradcam_img:
            with tempfile.NamedTemporaryFile(suffix=".jpeg") as temp_file:
                img = Image.open(BytesIO(gradcam_img.read()))
                img = img.resize((85, 80))
                img.save(temp_file, format='JPEG')
                temp_file.seek(0)
                pdf.ln(5)
                pdf.cell(0, 10, "GradCAM Image", 0, 2)
                pdf.image(temp_file.name, x=60, y=None, w=85, h=80)
       
        # Set Normal Font
        pdf.set_font("Times", size=10)
        pdf.set_text_color(0,0,0)
        pdf.ln(5)
        pdf.cell(0, 10,"Note: Correlate the information provided clinically, Write to 'rhd.reports@gmail.com' for any queries.", 0, 1)
        
        # Output PDF to S3
        # Use NamedTemporaryFile to create a temporary file to store PDF content
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_pdf:
            pdf.output(temp_pdf.name, 'F')
            temp_pdf.seek(0)

            # Upload PDF to S3
            pdf_key = f"static/reports/{name}.pdf"
            success = AWSUtils.upload_file_to_s3(temp_pdf, pdf_key)

            if success:
                print("PDF Report Uploaded to S3")
                return True, pdf_key
            else:
                return False, None
            
    except Exception as e:
            print(f"Error generating PDF report: {e}")
            return False, None

