@echo off
echo Starting EPG Merger Application...
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Flask application...
echo Open your browser and go to: http://localhost:5000
echo.
python app.py

