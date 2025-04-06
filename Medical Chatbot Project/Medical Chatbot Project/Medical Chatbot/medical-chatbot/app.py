from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Configure upload folders
UPLOAD_FOLDER = 'static/uploads'
PATIENT_REPORTS_FOLDER = 'static/uploads/patient_reports'

# Create folders if they don't exist
for folder in [UPLOAD_FOLDER, PATIENT_REPORTS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PATIENT_REPORTS_FOLDER'] = PATIENT_REPORTS_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

# Patient data storage (in-memory, replace with database in production)
patients = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class MedicalChatbot:
    def __init__(self):
        self.conditions = {
            'fever': {
                'medications': {
                    'paracetamol': {
                        'dosage': '500mg every 6 hours',
                        'link': '#'
                    }
                },
                'precautions': 'Stay hydrated, take rest, avoid cold beverages.',
                'diet': 'Eat light food, drink plenty of fluids, avoid spicy and fried foods.',
                'if_not_working': 'If symptoms persist or worsen (e.g., high fever, trouble breathing), consult a doctor.'
            },
            'acne': {
                'medications': {
                    'benzoyl_peroxide': {
                        'dosage': 'Apply 2.5-5% cream once daily',
                        'link': '#'
                    }
                },
                'precautions': 'Keep skin clean, avoid picking pimples, use non-comedogenic products.',
                'diet': 'Reduce dairy and high-glycemic foods, drink plenty of water.',
                'if_not_working': 'If acne persists or causes scarring, consult a dermatologist.'
            },
            'back_pain': {
                'medications': {
                    'ibuprofen': {
                        'dosage': '400mg every 8 hours',
                        'link': '#'
                    }
                },
                'precautions': 'Maintain good posture, avoid heavy lifting, do gentle stretches.',
                'diet': 'Eat anti-inflammatory foods (turmeric, ginger), stay hydrated.',
                'if_not_working': 'If pain radiates to legs or causes numbness, see a doctor.'
            },
            'insomnia': {
                'medications': {
                    'melatonin': {
                        'dosage': '1-3mg before bedtime',
                        'link': '#'
                    }
                },
                'precautions': 'Maintain sleep schedule, avoid screens before bed, create dark environment.',
                'diet': 'Avoid caffeine after noon, try chamomile tea, light dinner.',
                'if_not_working': 'If sleeplessness persists over 2 weeks, consult doctor.'
            },
            'heartburn': {
                'medications': {
                    'antacid': {
                        'dosage': 'As needed after meals',
                        'link': '#'
                    }
                },
                'precautions': 'Avoid lying down after eating, elevate head while sleeping.',
                'diet': 'Avoid spicy/fatty foods, chocolate, caffeine, alcohol.',
                'if_not_working': 'If symptoms occur more than twice weekly, see gastroenterologist.'
            },
            'migraine': {
                'medications': {
                    'sumatriptan': {
                        'dosage': '50-100mg at onset',
                        'link': '#'
                    }
                },
                'precautions': 'Identify triggers, rest in dark room, cold compress on forehead.',
                'diet': 'Stay hydrated, avoid aged cheeses, processed meats, alcohol.',
                'if_not_working': 'If accompanied by vision changes or vomiting, seek emergency care.'
            },
            'arthritis': {
                'medications': {
                    'glucosamine': {
                        'dosage': '1500mg daily',
                        'link': '#'
                    }
                },
                'precautions': 'Low-impact exercise, maintain healthy weight, warm compresses.',
                'diet': 'Anti-inflammatory diet (omega-3s, olive oil, colorful vegetables).',
                'if_not_working': 'If joints become red/swollen or deformed, see rheumatologist.'
            },
            'eczema': {
                'medications': {
                    'hydrocortisone_cream': {
                        'dosage': 'Apply thin layer twice daily',
                        'link': '#'
                    }
                },
                'precautions': 'Moisturize daily, avoid harsh soaps, wear cotton clothing.',
                'diet': 'Identify food triggers, increase omega-3s, reduce dairy if sensitive.',
                'if_not_working': 'If skin becomes infected (oozing, crusting), see dermatologist.'
            },
            'sinusitis': {
                'medications': {
                    'saline_nasal_spray': {
                        'dosage': '2-3 sprays per nostril as needed',
                        'link': '#'
                    }
                },
                'precautions': 'Use humidifier, stay hydrated, avoid irritants like smoke.',
                'diet': 'Warm fluids, spicy foods (helps drainage), avoid dairy if congested.',
                'if_not_working': 'If symptoms last >10 days or fever develops, see doctor.'
            },
            'urinary_tract_infection': {
                'medications': {
                    'cranberry_supplements': {
                        'dosage': '500mg twice daily',
                        'link': '#'
                    }
                },
                'precautions': 'Wipe front to back, urinate after intercourse, stay hydrated.',
                'diet': 'Drink plenty water, avoid irritants like caffeine/alcohol.',
                'if_not_working': 'If fever/chills develop or symptoms persist >2 days, seek antibiotics.'
            },
            'pms': {
                'medications': {
                    'calcium_supplements': {
                        'dosage': '1200mg daily',
                        'link': '#'
                    }
                },
                'precautions': 'Regular exercise, stress management, track symptoms.',
                'diet': 'Reduce salt/sugar/caffeine, increase complex carbs, small frequent meals.',
                'if_not_working': 'If symptoms severely impact life, consult gynecologist.'
            },
            'gingivitis': {
                'medications': {
                    'antimicrobial_mouthwash': {
                        'dosage': 'Rinse twice daily',
                        'link': '#'
                    }
                },
                'precautions': 'Proper brushing/flossing, regular dental cleanings, no smoking.',
                'diet': 'Vitamin C-rich foods, crunchy fruits/vegetables, limit sugary foods.',
                'if_not_working': 'If gums bleed persistently or teeth become loose, see dentist.'
            },
            'hemorrhoids': {
                'medications': {
                    'witch_hazel_wipes': {
                        'dosage': 'Use after bowel movements',
                        'link': '#'
                    }
                },
                'precautions': "Avoid straining, don't delay bowel movements, sitz baths.",
                'diet': 'High fiber (fruits, vegetables, whole grains), plenty fluids.',
                'if_not_working': 'If bleeding is heavy or persistent, consult proctologist.'
            },
            'canker_sores': {
                'medications': {
                    'benzocaine_gel': {
                        'dosage': 'Apply to sore up to 4 times daily',
                        'link': '#'
                    }
                },
                'precautions': 'Avoid spicy/acidic foods, use soft toothbrush, reduce stress.',
                'diet': 'Vitamin B-rich foods (leafy greens, eggs), avoid citrus/tomatoes.',
                'if_not_working': 'If sores last >2 weeks or spread, see oral specialist.'
            },
            'pink_eye': {
                'medications': {
                    'artificial_tears': {
                        'dosage': '1-2 drops every 4-6 hours',
                        'link': '#'
                    }
                },
                'precautions': 'Wash hands frequently, avoid touching eyes, change pillowcases.',
                'diet': 'Vitamin A-rich foods (carrots, sweet potatoes), stay hydrated.',
                'if_not_working': 'If vision affected or symptoms worsen after 2 days, see ophthalmologist.'
            },
            'athletes_foot': {
                'medications': {
                    'clotrimazole_cream': {
                        'dosage': 'Apply twice daily for 2-4 weeks',
                        'link': '#'
                    }
                },
                'precautions': "Keep feet dry, wear breathable shoes, don't share towels.",
                'diet': 'Probiotic foods (yogurt), limit sugar (feeds fungus).',
                'if_not_working': "If rash spreads or doesn't improve, see dermatologist."
            },
            'ringworm': {
                'medications': {
                    'terbinafine_cream': {
                        'dosage': 'Apply 1-2 times daily for 1-2 weeks',
                        'link': '#'
                    }
                },
                'precautions': 'Keep area dry, wash bedding/clothes, avoid scratching.',
                'diet': 'Garlic (natural antifungal), reduce sugar intake.',
                'if_not_working': 'If patches multiply or worsen, seek medical treatment.'
            },
            'sunburn': {
                'medications': {
                    'aloe_vera_gel': {
                        'dosage': 'Apply liberally as needed',
                        'link': '#'
                    }
                },
                'precautions': 'Cool compresses, stay hydrated, avoid further sun exposure.',
                'diet': 'Antioxidant-rich foods (berries), extra fluids, avoid alcohol.',
                'if_not_working': 'If blisters form or fever develops, seek medical care.'
            },
            'indigestion': {
                'medications': {
                    'simethicone': {
                        'dosage': '40-125mg after meals',
                        'link': '#'
                    }
                },
                'precautions': 'Eat slowly, avoid lying down after eating, reduce stress.',
                'diet': 'Small frequent meals, avoid greasy/spicy foods, peppermint tea.',
                'if_not_working': 'If pain is severe or persistent, consult gastroenterologist.'
            },
            'motion_sickness': {
                'medications': {
                    'dimenhydrinate': {
                        'dosage': '50-100mg every 4-6 hours',
                        'link': '#'
                    }
                },
                'precautions': 'Sit where motion is least (front seat, over wings), focus on horizon.',
                'diet': 'Light meal before travel, ginger tea/candies, avoid heavy/fatty foods.',
                'if_not_working': 'If symptoms are severe and persistent, consult doctor.'
            },
            'dehydration': {
                'medications': {
                    'oral_rehydration_salts': {
                        'dosage': 'As directed on package',
                        'link': '#'
                    }
                },
                'precautions': 'Drink fluids regularly, avoid excessive heat/sun, monitor urine color.',
                'diet': 'Water, coconut water, diluted juices, avoid alcohol/caffeine.',
                'if_not_working': 'If dizziness/confusion occurs or unable to keep fluids down, seek emergency care.'
            },
            'anemia': {
                'medications': {
                    'iron_supplements': {
                        'dosage': '65mg elemental iron daily',
                        'link': '#'
                    }
                },
                'precautions': "Take iron with vitamin C for absorption, don't take with calcium.",
                'diet': 'Iron-rich foods (red meat, spinach, lentils), vitamin C sources.',
                'if_not_working': 'If fatigue worsens or no improvement in 2 weeks, see hematologist.'
            },
            'osteoporosis': {
                'medications': {
                    'calcium_vitamin_D': {
                        'dosage': '1200mg calcium + 800IU vitamin D daily',
                        'link': '#'
                    }
                },
                'precautions': 'Weight-bearing exercise, fall prevention, no smoking.',
                'diet': 'Dairy, leafy greens, fatty fish, fortified foods.',
                'if_not_working': 'If fractures occur or bone density declines, consult specialist.'
            },
            'high_cholesterol': {
                'medications': {
                    'plant_sterols': {
                        'dosage': '2g daily with meals',
                        'link': '#'
                    }
                },
                'precautions': 'Regular exercise, maintain healthy weight, quit smoking.',
                'diet': 'Oats, nuts, olive oil, fatty fish; limit saturated/trans fats.',
                'if_not_working': 'If LDL remains high despite lifestyle changes, see cardiologist.'
            },
            'gout': {
                'medications': {
                    'cherry_extract': {
                        'dosage': '1000mg daily',
                        'link': '#'
                    }
                },
                'precautions': 'Avoid alcohol, stay hydrated, elevate affected joint.',
                'diet': 'Low-purine diet (avoid organ meats, shellfish), dairy products.',
                'if_not_working': 'If pain is severe or joints become hot/swollen, seek treatment.'
            },
            'psoriasis': {
                'medications': {
                    'coal_tar_shampoo': {
                        'dosage': 'Use 2-3 times weekly',
                        'link': '#'
                    }
                },
                'precautions': 'Moisturize daily, avoid skin trauma, moderate sun exposure.',
                'diet': 'Anti-inflammatory diet, omega-3s, limit alcohol.',
                'if_not_working': 'If plaques cover large areas or joints hurt, see dermatologist.'
            },
            'rosacea': {
                'medications': {
                    'metronidazole_gel': {
                        'dosage': 'Apply thin layer daily',
                        'link': '#'
                    }
                },
                'precautions': 'Avoid triggers (heat, spicy food, alcohol), gentle skincare.',
                'diet': 'Cool foods, omega-3s, avoid hot beverages/spicy foods.',
                'if_not_working': 'If facial redness worsens or eyes affected, seek treatment.'
            },
            'tinnitus': {
                'medications': {
                    'magnesium_supplements': {
                        'dosage': '200mg daily',
                        'link': '#'
                    }
                },
                'precautions': 'Avoid loud noise, reduce stress, white noise machines.',
                'diet': 'Limit salt/caffeine/alcohol, zinc-rich foods (nuts, seeds).',
                'if_not_working': 'If ringing is pulsatile or accompanied by hearing loss, see ENT.'
            },
            'vertigo': {
                'medications': {
                    'meclizine': {
                        'dosage': '25mg as needed',
                        'link': '#'
                    }
                },
                'precautions': 'Move slowly, Epley maneuver, avoid sudden head movements.',
                'diet': 'Stay hydrated, limit salt/alcohol/caffeine.',
                'if_not_working': 'If accompanied by hearing loss or neurological symptoms, seek emergency care.'
            },
            'carpal_tunnel': {
                'medications': {
                    'wrist_splint': {
                        'dosage': 'Wear at night',
                        'link': '#'
                    }
                },
                'precautions': 'Take typing breaks, ergonomic setup, wrist exercises.',
                'diet': 'Anti-inflammatory foods, vitamin B6 sources (bananas, potatoes).',
                'if_not_working': 'If numbness/weakness persists, consult orthopedic specialist.'
            },
            'shin_splints': {
                'medications': {
                    'ice_pack': {
                        'dosage': '15-20 minutes every 4-6 hours',
                        'link': '#'
                    }
                },
                'precautions': 'Rest from impact activities, proper footwear, gradual training.',
                'diet': 'Calcium/vitamin D for bone health, anti-inflammatory foods.',
                'if_not_working': 'If pain persists at rest or worsens, see sports medicine doctor.'
            }
        }

        self.non_reactive_medications = {
            'multivitamin': 'Take once daily to prevent deficiencies.',
            'probiotic': 'Helps maintain gut health, especially with antibiotics.'
        }

    def get_medications(self, conditions):
        meds = {}
        precautions = []
        diet = []
        if_not_working = []

        for condition in conditions:
            if condition in self.conditions:
                condition_info = self.conditions[condition]
                
                for med, info in condition_info['medications'].items():
                    if med not in meds:
                        meds[med] = info['dosage']
                        meds[f'{med}_link'] = info['link']
                
                precautions.append(condition_info['precautions'])
                diet.append(condition_info['diet'])
                if_not_working.append(condition_info['if_not_working'])
        
        return meds, precautions, diet, if_not_working

    def suggest_medication(self, conditions):
        medications, precautions, diet, if_not_working = self.get_medications(conditions)
        prevent_reactions = self.non_reactive_medications

        response = {
            'medications': medications,
            'precautions': precautions,
            'diet': diet,
            'prevent_reactions': prevent_reactions,
            'if_not_working': if_not_working
        }
        
        return response
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PATIENT_REPORTS_FOLDER'], exist_ok=True)

# Patient Reports Routes
@app.route("/patient/upload", methods=['GET', 'POST'])
def upload_patient_reports():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        file = request.files['file']
        patient_id = request.form.get('patient_id')
        patient_name = request.form.get('patient_name')
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            patient_dir = os.path.join(app.config['PATIENT_REPORTS_FOLDER'], patient_id)
            if not os.path.exists(patient_dir):
                os.makedirs(patient_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(patient_dir, new_filename)
            file.save(file_path)
            
            if patient_id not in patients:
                patients[patient_id] = {
                    'name': patient_name,
                    'reports': []
                }
            
            patients[patient_id]['reports'].append({
                'filename': new_filename,
                'original_name': filename,
                'upload_date': timestamp,
                'file_path': file_path.replace('static/', '')
            })
            
            flash('Report uploaded successfully!')
            return redirect(url_for('view_patient_reports', patient_id=patient_id))
    
    return render_template("upload_reports.html")

@app.route("/patient/<patient_id>")
def view_patient_reports(patient_id):
    if patient_id in patients:
        patient = patients[patient_id]
        return render_template("patient_reports.html", patient=patient, patient_id=patient_id)
    else:
        flash('Patient not found')
        return redirect(url_for('upload_patient_reports'))

@app.route("/patient/reports/<patient_id>/<filename>")
def serve_patient_report(patient_id, filename):
    return send_from_directory(os.path.join(app.config['PATIENT_REPORTS_FOLDER'], patient_id), filename)

# Main Application Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/scheme')
def scheme():
    return render_template('govt_scheme.html')

@app.route('/chat', methods=['POST'])
def chat():
    conditions_input = request.form.get('condition', '').lower()
    conditions = [condition.strip() for condition in conditions_input.split(',') if condition.strip()]
    
    chatbot = MedicalChatbot()
    response = chatbot.suggest_medication(conditions)

    return jsonify(response)

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)