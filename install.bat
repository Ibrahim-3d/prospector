@echo off
echo Installing backend dependencies...
pip install fastapi uvicorn[standard] sqlalchemy pydantic openpyxl python-multipart

echo.
echo Installing frontend dependencies...
cd frontend
npm install
cd ..

echo.
echo Done! Run start.bat to launch the app.
pause
