# Secretome

## Getting your release up to speed

0. Install Django (1.8.3+), mysql and Apache configuration
1. Download a release from https://github.com/EDRN/Secretome
2. Extract the archive in /usr/local/edrn/secretome
3. Change into that directory
4. Add the local_settings.py if it does not exist (details below)
5. Add the wsgi.py to include appropriate paths (example below)
6. Obtain a mysql dump from AshishMahabal and load it
7. Copy the file "bigger_table" obtained from AshishMahabal in to the MEDIA_ROOT dir
8. Restart Apache
9. Go to http://{hostname}/secretome/ and have fun

### Specifics

- local_settings.py should contain values for:

SECRET_KEY  
DATABASES  
STATIC_URL  
MEDIA_ROOT	# This should be outside the django area  
BASE_RELPATH  
DEBUG = False	# For production mode  

- example line for wsgi.py:

sys.path.append('/usr/local/python-3.5.0/lib/python3.5/site-packages')
