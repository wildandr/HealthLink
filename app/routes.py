from flask import request, jsonify, abort
from flask_cors import cross_origin
from . import app, db
from .models import User, PatientRecord, Appointment, AuditLog, BlockchainAccess
import hashlib

# Fungsi untuk menghasilkan hash dari sebuah string
def generate_hash(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()

# Membuat log transaksi pada blockchain
def create_blockchain_entry(user_id, action, details):
    # Ini hanya contoh sederhana. Anda mungkin perlu skema yang lebih kompleks untuk 'blockchain'
    last_block = BlockchainAccess.query.order_by(BlockchainAccess.id.desc()).first()
    last_hash = last_block.transaction_id if last_block else 'genesis_block_hash'
    new_hash = generate_hash(f'{last_hash}{details}')
    new_block = BlockchainAccess(user_id=user_id, transaction_id=new_hash, details=details)
    db.session.add(new_block)
    db.session.commit()
    return new_block

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(username=data['username'], password_hash=data['password_hash'], role=data['role'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    create_blockchain_entry(new_user.id, "Create User", f"User {new_user.username} created")
    return jsonify({'message': 'User created', 'user_id': new_user.id}), 201

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'username': user.username, 'role': user.role, 'email': user.email})

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    create_blockchain_entry(user.id, "Update User", f"User {user.username} updated")
    return jsonify({'message': 'User updated'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    create_blockchain_entry(user.id, "Delete User", f"User {user.username} deleted")
    return jsonify({'message': 'User deleted'})

# Tambahkan route serupa untuk PatientRecord, Appointment, dan AuditLog

# Route untuk membuat patient record baru
@app.route('/patient_records', methods=['POST'])
def create_patient_record():
    data = request.json
    new_record = PatientRecord(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        record_details=data['record_details']
    )
    db.session.add(new_record)
    db.session.commit()
    create_blockchain_entry(new_record.doctor_id, "Create Patient Record", f"Record for patient_id {new_record.patient_id} created")
    return jsonify({'message': 'Patient record created', 'record_id': new_record.id}), 201

# Route untuk mendapatkan detail patient record
@app.route('/patient_records/<int:record_id>', methods=['GET'])
def get_patient_record(record_id):
    record = PatientRecord.query.get_or_404(record_id)
    return jsonify({
        'patient_id': record.patient_id,
        'doctor_id': record.doctor_id,
        'record_details': record.record_details,
        'last_update': record.last_update.isoformat()
    })

# Route untuk memperbarui patient record
@app.route('/patient_records/<int:record_id>', methods=['PUT'])
def update_patient_record(record_id):
    record = PatientRecord.query.get_or_404(record_id)
    data = request.json
    record.record_details = data.get('record_details', record.record_details)
    db.session.commit()
    create_blockchain_entry(record.doctor_id, "Update Patient Record", f"Record for patient_id {record.patient_id} updated")
    return jsonify({'message': 'Patient record updated'})

# Route untuk menghapus patient record
@app.route('/patient_records/<int:record_id>', methods=['DELETE'])
def delete_patient_record(record_id):
    record = PatientRecord.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    create_blockchain_entry(record.doctor_id, "Delete Patient Record", f"Record for patient_id {record.patient_id} deleted")
    return jsonify({'message': 'Patient record deleted'})

# Route untuk membuat appointment baru
@app.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    new_appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        appointment_time=data['appointment_time'],
        status=data['status']
    )
    db.session.add(new_appointment)
    db.session.commit()
    create_blockchain_entry(new_appointment.doctor_id, "Create Appointment", f"Appointment for patient_id {new_appointment.patient_id} created")
    return jsonify({'message': 'Appointment created', 'appointment_id': new_appointment.id}), 201

# Route untuk mendapatkan detail appointment
@app.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    return jsonify({
        'patient_id': appointment.patient_id,
        'doctor_id': appointment.doctor_id,
        'appointment_time': appointment.appointment_time.isoformat(),
        'status': appointment.status
    })

# Route untuk memperbarui appointment
@app.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    data = request.json
    appointment.appointment_time = data.get('appointment_time', appointment.appointment_time)
    appointment.status = data.get('status', appointment.status)
    db.session.commit()
    create_blockchain_entry(appointment.doctor_id, "Update Appointment", f"Appointment for patient_id {appointment.patient_id} updated")
    return jsonify({'message': 'Appointment updated'})

# Route untuk menghapus appointment
@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    create_blockchain_entry(appointment.doctor_id, "Delete Appointment", f"Appointment for patient_id {appointment.patient_id} deleted")
    return jsonify({'message': 'Appointment deleted'})

# Route untuk mendapatkan semua audit log
@app.route('/audit_logs', methods=['GET'])
def get_all_audit_logs():
    logs = AuditLog.query.all()
    response = [{
        'id': log.id,
        'user_id': log.user_id,
        'activity': log.activity,
        'timestamp': log.timestamp.isoformat(),
        'affected_records': log.affected_records
    } for log in logs]
    return jsonify(response)

# Route untuk mendapatkan detail audit log tertentu
@app.route('/audit_logs/<int:log_id>', methods=['GET'])
def get_audit_log(log_id):
    log = AuditLog.query.get_or_404(log_id)
    return jsonify({
        'id': log.id,
        'user_id': log.user_id,
        'activity': log.activity,
        'timestamp': log.timestamp.isoformat(),
        'affected_records': log.affected_records
    })

# Route untuk menghapus audit log (opsional, tergantung kebijakan keamanan Anda)
@app.route('/audit_logs/<int:log_id>', methods=['DELETE'])
def delete_audit_log(log_id):
    log = AuditLog.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    # Catatan: Pencatatan ke blockchain untuk penghapusan log bisa diatur sesuai kebijakan keamanan
    return jsonify({'message': 'Audit log deleted'})

# Contoh untuk blockchain access
@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    blocks = BlockchainAccess.query.all()
    response = [{'user_id': block.user_id, 'transaction_id': block.transaction_id, 'details': block.details} for block in blocks]
    return jsonify(response)

