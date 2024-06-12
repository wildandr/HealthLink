from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Konfigurasi untuk database SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/owwl/Downloads/healthlink/healthlink.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inisialisasi objek database SQLAlchemy
db = SQLAlchemy(app)

# Import model dan route setelah inisialisasi db untuk menghindari masalah circular import
from .models import *
from .routes import *

# Opsional: Jika Anda ingin menambahkan handling CORS
from flask_cors import CORS
CORS(app)

