@echo off
call .\venv\Scripts\activate.bat

echo "Checking Streamlit installation..."
python -m pip install streamlit

echo "Starting Streamlit App in local background..."
python -m streamlit run app.py

pause
