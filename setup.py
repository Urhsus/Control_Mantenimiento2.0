from setuptools import setup, find_packages

setup(
    name="control_mantenimiento",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        'Flask==3.0.0',
        'Flask-SQLAlchemy==3.1.1',
        'Flask-Login==0.6.3',
        'Flask-WTF==1.2.1',
        'openpyxl==3.1.2',
        'python-dotenv==1.0.0',
        'Flask-Migrate==4.0.5',
        'SQLAlchemy==2.0.23',
        'Werkzeug==3.0.1',
        'email-validator==2.1.0.post1',
        'python-dateutil==2.8.2',
        'Flask-Principal==0.4.0',
    ],
)
