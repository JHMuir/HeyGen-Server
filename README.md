# HeyGen-Server
Hello! This is my take-home project, assigned by HeyGen.
## Running the project

To run this project, first clone it, then install the dependencies:
```
pip install -r requirements.txt
```
Start the server with:
```
python3 server_main.py
```
In a new terminal window, you can test the client library with:
```
python3 client_main.py
```
## Documentation
The main client library can be found in library/client.py. It is contained entirely within the TranslationClient class. It was developed with a circuit breaker design pattern, which prevents cascading failures, and attempts to repair itself after a configurable amount of time. The main 4 public functions that a user would interact with are: 
```python
def create_job()
  # Creates a job and posts it the server endpoint 
```
```python
def get_status()
  # Simple check, retrieves the current status of the specified job
```
```python
def wait_for_completion()
  # Waits for job completion using exponential backoff
```
```python
def wait_for_completion_with_interval()
  # Waits for job completion, checking every specified interval in seconds 
```
View the code for more specific documentation. Every class and function in this project is well documented with docstrings and comments. 

This project was modularly designed, and easily maintainable and extensible. 

## Contributing
If, for whatever reason, you'd like to contribute, first install the pre-commit hook with:
```
pre-commit install
```
This allows for code linting and formatting at every ```git commit```, ensuring readibility and consistency. Then open an issue and submit a PR. 
