# Define default environment variables
INFO=true

# Normal mode (INFO only)
run:
	@INFO=$(INFO) streamlit run app.py

# Debug mode (INFO and DEBUG)
debug:
	@DEBUG=true INFO=$(INFO) streamlit run app.py
