# Start Server.
uvicorn app.main:app --reload

# Start Device Bridge.
adb -s 0A101JEC207233 reverse tcp:8081 tcp:8081

# Start Device Server Bridge.
adb -s 0A101JEC207233 reverse tcp:8000 tcp:8000

# Find Devices.
adb devices

# Run on local network.
uvicorn app.main:app --reload --host 0.0.0.0

# Log into psql client for DB.
psql postgresql://postgres:postgres@127.0.0.1:5432/dev