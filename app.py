from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
db = SQLAlchemy(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_type = db.Column(db.String(10), nullable=False)
    medical_condition = db.Column(db.String(100), nullable=False)
    date_of_admission = db.Column(db.Date, nullable=False)
    doctor = db.Column(db.String(100), nullable=False)
    hospital = db.Column(db.String(100), nullable=False)
    insurance_provider = db.Column(db.String(100), nullable=False)
    billing_amount = db.Column(db.Float, nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    admission_type = db.Column(db.String(20), nullable=False)
    discharge_date = db.Column(db.Date, nullable=True)
    medication = db.Column(db.String(100), nullable=False)
    test_results = db.Column(db.String(20), nullable=False)

@app.route('/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([p.as_dict() for p in patients])

@app.route('/patients/<int:id>', methods=['GET'])
def get_patient(id):
    patient = Patient.query.get(id)
    if patient:
        return jsonify(patient.as_dict())
    else:
        return jsonify({'error': 'Patient not found'}), 404

@app.route('/patients', methods=['POST'])
def add_patient():
    try:
        data = request.json
        data['date_of_admission'] = datetime.strptime(data['date_of_admission'], '%Y-%m-%d').date()
        if data.get('discharge_date'):
            data['discharge_date'] = datetime.strptime(data['discharge_date'], '%Y-%m-%d').date()
        new_patient = Patient(**data)
        db.session.add(new_patient)
        db.session.commit()
        return jsonify(new_patient.as_dict()), 201
    except KeyError as e:
        return jsonify({'error': f'Missing key: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Integrity error, possibly duplicate entry'}), 400

@app.route('/patients/<int:id>', methods=['PUT'])
def update_patient(id):
    data = request.json
    patient = Patient.query.get(id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    for key, value in data.items():
        if key in ['date_of_admission', 'discharge_date']:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        setattr(patient, key, value)
    
    db.session.commit()
    return jsonify(patient.as_dict()), 200

@app.route('/patients/<int:id>', methods=['DELETE'])
def delete_patient(id):
    patient = Patient.query.get(id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted'}), 200

# Helper method to convert Patient object to dictionary
def patient_as_dict(patient):
    return {
        'id': patient.id,
        'name': patient.name,
        'age': patient.age,
        'gender': patient.gender,
        'blood_type': patient.blood_type,
        'medical_condition': patient.medical_condition,
        'date_of_admission': patient.date_of_admission.isoformat(),
        'doctor': patient.doctor,
        'hospital': patient.hospital,
        'insurance_provider': patient.insurance_provider,
        'billing_amount': patient.billing_amount,
        'room_number': patient.room_number,
        'admission_type': patient.admission_type,
        'discharge_date': patient.discharge_date.isoformat() if patient.discharge_date else None,
        'medication': patient.medication,
        'test_results': patient.test_results
    }

Patient.as_dict = patient_as_dict

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

