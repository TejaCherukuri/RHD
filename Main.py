import os
from flask import Flask, render_template, request
from service.utils import apply_clahe
from ai_service import cataract_diagnosis as ct
from ai_service  import dr_diagnosis as dr
from ai_service  import dme_diagnosis as dme
from repository import db_repository as repo
from service import generate_report_service as report_gen
from service.email_service import send_email
from werkzeug.utils import secure_filename
from aws.aws_utils import AWSUtils


app = Flask(__name__)

uploads = os.path.join('static', 'uploads')
app.config['UPLOAD'] = uploads

@app.route("/")
def login():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('home.html', methods=['POST'])

@app.route("/cataract-reg")
def cataract_reg():
    return render_template('cataract_reg.html', methods=['POST'])

@app.route("/retinopathy-reg")
def retinopathy_reg():
    return render_template('retinopathy_reg.html', methods=['POST'])

@app.route("/edema-reg")
def macular_edema_reg():
    return render_template('macular_edema_reg.html', methods=['POST'])

# @app.route("/authenticate", methods=['POST'])
# def authenticate():
#     uid = request.form['UserId']
#     pwd = request.form['Password']
#     users = repo.authenticate(uid)
#     if len(users)>0:
#         if uid == users[0][0] and pwd == users[0][1]:
#             return render_template('index.html', uid = users[0])
#     return render_template('invalid_login.html')

@app.route("/getCeteractData", methods=['POST'])
def getCeteractData():
    try:
        name = request.form['Name']
        mobile = request.form['Ph_No']
        email = request.form['Email_Id']
        gender = request.form['Gender']
        age = request.form['Age']
        address = request.form['Address']
        scan_type = request.form['ScanType']
        file = request.files['img_path']
        file_name = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD'], file_name))
        img_path = os.path.join(app.config['UPLOAD'], file_name)
        cataract_label = None
        report = None
        
        s0 = "--None--"
        s1 = "Use HN-acetylcarnosine eye drops twice a day."
        s2 = "Better to go for Retinal examination & surgical treatment."
        s3 = "Better to go for a surgical treatment."
        
        r1, r2 = "", ""
        observations = "None"
        
        to_mail_list = ['skns.cse@gmail.com', 'tejkrish98@gmail.com']
        if(email != None):
            to_mail_list.append(email)
        
        
        if scan_type == 'Digital Eye':
            cataract_label = ct.digitalEyeCateractDiagnosis(img_path)
            if(cataract_label == 'Cataract'):
                r1, r2 = s1, s2
                observations = "Visual complications found - Endophthalmitis"
            else:
                r1, r2 = s0, s0
                observations = "No visual complications found"
        
        if scan_type == 'Retinal Scan':
            cataract_label = ct.retinalScanCateractDiagnosis(img_path)
            if(cataract_label == 'Cataract'):
                r1, r2 = s1, s3
                observations = "Complications - Cystoid Macular Edema/Vitreous/Suprachoroidal Hemorrhage."
            else:
                r1, r2 = s0, s0
                observations = "No visual complications found"
        
        apply_clahe(img_path, name)
        report_gen.generate_report(name, gender, age, mobile, email, address, "Cateract Diagnosis: "+scan_type, cataract_label, img_path, r1, r2, observations)
        
        # repo.write_to_db(name, gender, age, mobile, email, address, "Cateract Diagnosis - "+scan_type, cataract_label, report)
        send_email(to_mail_list, name, "Cateract Diagnosis: "+scan_type, cataract_label)
        
    except Exception as e:
        print("Exception Occured: "+str(e))
        
    return render_template('cataract_report.html', name=name, gender=gender, age=age, mobile=mobile, email = email, address = address, scan_type = scan_type, diagnosis_label = cataract_label, file_name="./static/Reports/"+name+".pdf",r1=r1,r2=r2)
    
    


@app.route("/getDMEData", methods=['POST'])
def getDMEtData():
    try:
        name = request.form['Name']
        mobile = request.form['Ph_No']
        email = request.form['Email_Id']
        gender = request.form['Gender']
        age = request.form['Age']
        address = request.form['Address']
        file = request.files['img_path']
        file_name = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD'], file_name))
        img_path = os.path.join(app.config['UPLOAD'], file_name)
        dme_label = None
        report = None
        
        s0 = "--None--"
        s1 = "Use Non-Steroidal Anti-Inflammatories (NSAIDs)."
        s2 = "Better to go for anti-VEGF intravitreal therapy."
        
        r1, r2 = "", ""
        observations = "None"
        
        to_mail_list = ['skns.cse@gmail.com', 'tejkrish98@gmail.com']
        if(email != None):
            to_mail_list.append(email)
        
        
        dme_label = dme.dme_Diagnosis(img_path)
        if(dme_label == 'Referable DME'):
            r1, r2 = s1, s2
            observations = "Possible Complications - Cataracts, Retinopathy, Glaucoma"
        else:
            r1, r2 = s0, s0
            observations = "No DME related visual complications found - Go for DR test"
        
        apply_clahe(img_path, name)        
        report_gen.generate_report(name, gender, age, mobile, email, address, "DME Diagnosis", dme_label, img_path, r1, r2, observations)
        pdf_report_path = "static/Reports/"+name+".pdf"
        with open(pdf_report_path, 'rb') as f:
            report = f.read()
        
        # repo.write_to_db(name, gender, age, mobile, email, address, "DME Diagnosis", dme_label, report)
        send_email(to_mail_list, name, "DME Diagnosis", dme_label)
    except Exception as e:
        print("Exception Occured: "+str(e))
    
    return render_template('dme_report.html', name=name, gender=gender, age=age, mobile=mobile, email = email, address = address, diagnosis_label = dme_label, file_name="./static/Reports/"+name+".pdf",r1=r1,r2=r2)
    


@app.route("/getDRData", methods=['POST'])
def getDRData():
    
    try:
        name = request.form['Name']
        mobile = request.form['Ph_No']
        email = request.form['Email_Id']
        gender = request.form['Gender']
        age = request.form['Age']
        address = request.form['Address']
        file = request.files['img_path']

        if file.filename == '':
            return 'No selected file'
        
        try:
            # Use secure_filename to sanitize the filename
            filename = secure_filename(file.filename)
            
            # Upload file to S3
            s3_key = f"static/uploads/{filename}"
            print(s3_key)
            success = AWSUtils.upload_file_to_s3(file, s3_key)
        
            if not success:
                return 'Error uploading file to S3'
            
            print(f'File uploaded successfully to S3')
        
        except Exception as e:
            return f"Error uploading file: {e}"
        
        img_path = s3_key  # Use the S3 key for processing
    
        test_type = request.form['Test']
        
        s0 = "--None--"
        s1 = "Maintain Controlled Blood Sugar Levels, Cholestrol & BP"
        s2 = "Use Hyvet Eye drops twice a day"
        s3 = "Use Lubimoist Eye drops twice a day"
        s4 = "Go for Laser Treatment"
        s5 = "Use Lubimoist Eye drops twice a day"
        s6 = "Use Nexthane Opthalmic Solution twice a day"
        s7 = "Go for Severity Test"
        
        r1, r2 = "", ""
        observations = "None"
        
        to_mail_list = ['skns.cse@gmail.com', 'tejkrish98@gmail.com']
        if(email != None):
            to_mail_list.append(email)
        
        dr_label = "Retinopathy Negative"
        dr_severity_label = dr.diabeticRetinopathyDiagnosis(img_path)
        if dr_severity_label != "Normal":
            dr_label = "Retinoapthy Positive - " + dr_severity_label
            
        if dr_severity_label == "Normal":
            r1, r2 = s0, s0
            observations = "No visual complications found"
        
        elif dr_severity_label == "Mild DR":
            r1, r2 = s1, s2
            observations = "Complications noted - Formation of Micro Aneurysms"
            
        elif dr_severity_label == "Moderate DR":
            r1, r2 = s1, s3
            observations = "Complications noted - Higher Micro Aneurysms & Minimal Exudates found"
            
        elif dr_severity_label == "Sever DR":
            r1, r2 = s3, s4
            observations = "Higher - Micro Aneurysms & Exudates found around fovea. Intra retinal micro vacular abnormalities"
            
        else:
            r1, r2 = s5, s6
            observations = "Lesions - MA, HE, Hm. New vessels growth. Neovascularisation. Endangered Retinal Detachment"
               
        if test_type == 'Identification Test':
            if('Positive' in dr_label):
                dr_label = "Retinoapthy Positive"
                r1, r2 = s1, s7
                observations = "Visual complications found due to microvascular abnormal lesions"
                
        image_name = filename.split('.')[0]
        print("Applying CLAHE")
        apply_clahe(img_path, name, image_name)
        report_gen.generate_report(name, image_name, gender, age, mobile, email, address, "Retinopathy Diagnosis: "+test_type, dr_label, img_path, r1, r2, observations)
        
         # repo.write_to_db(name, gender, age, mobile, email, address, "Retinopathy Diagnosis - "+test_type, dr_label, report)
        send_email(to_mail_list, name, "Retinopathy Diagnosis: "+test_type, dr_label)
    except Exception as e:
        print("Exception Occured: "+str(e))
    
    return render_template('dr_report.html', name=name, gender=gender, age=age, mobile=mobile, email = email, address = address, test_type = test_type, diagnosis_label = dr_label, file_name="./static/Reports/"+name+".pdf",r1=r1,r2=r2)
    	
	
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=True)
