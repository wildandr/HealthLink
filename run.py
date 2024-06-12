from app import app, db

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()  # Only use during development to reset the database
        db.create_all()
    app.run(debug=True)
