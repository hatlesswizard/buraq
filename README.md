# Buraq: SQL Injection Detector
Buraq is a **Dynamic Application Security Testing (DAST)** tool designed to identify **SQL Injection (SQLi)** vulnerabilities in web applications. Leveraging HTTP query logs, Buraq modifies request parameters and detects potential vulnerabilities in the application's query handling.

---
## Features
- **Automated Query Testing**: Modifies query parameters and values dynamically to identify potential injection points.
- **Log Monitoring**: Continuously monitors MySQL logs to detect SQLi attempts.
- **Flexible Input**: Accepts direct URLs or HTTP request files for testing.
- **Multithreading**: Performs efficient, concurrent requests to speed up the testing process.
- **Vulnerability Context Detection**: Determines the context (e.g., single quotes, double quotes, backticks, or none) where vulnerabilities occur.

---
## Prerequisites
- **Python 3.8+**
- Install required libraries:
  ```bash
  pip install -r requirements.txt
  ```
- Ensure MySQL logging is enabled on the target system, and provide the log file path in the script (`log_file` variable):
```bash
# Example setup for MySQL my.cnf file:
[mysqld]
general_log_file = /var/log/mysql/mysql.log
general_log = 1
log-raw = 1
# Don't forget to provide necessary permissions to mysql user
chown mysql:mysql /var/log/mysql -R
```

---

## Usage

### Command-Line Arguments
Buraq supports the following command-line options:
- `-u, --url`: The URL to test for SQL Injection vulnerabilities.
- `-f, --file`: A file containing the raw HTTP request to be tested.

### Examples
#### Using a URL
```bash
python buraq.py -u "http://example.com/vulnerable_page.php?id=1"
```
#### Using an HTTP File
Save your HTTP request in a file (e.g., `request.txt`):
```
POST /vulnerable_page.php HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 13

id=1&name=test
```
Run:
```bash
python buraq.py -f request.txt
```
---

## How It Works
1. **Parameter Modification**:
   - Replaces query and post parameters with random strings or SQL special characters to test for vulnerabilities.
   - Explores multiple contexts (e.g., inside single quotes, double quotes, backticks).
2. **Request Execution**:
   - Sends modified requests to the server.
   - Monitors the MySQL log file for patterns matching the injected strings.
3. **Log Analysis**:
   - Identifies whether the injected strings were interpreted as part of the SQL query, flagging potential vulnerabilities.

---
## Key Functions
- **`replace_params_keys_and_values()`**: Dynamically modifies query keys and values with random strings or special characters.
- **`monitor_log()`**: Monitors MySQL logs for evidence of SQL Injection.
- **`find_string_location()`**: Determines the SQL context of an injected string.
- **`send_requests()`**: Handles the multithreaded execution of requests.

---
## Output
The tool provides detailed output for each request, including:
- Modified URLs or POST data.
- Random strings used in the injection attempts.
- Detected SQLi along with contexts.
![image](https://github.com/user-attachments/assets/5c6fe5c1-f141-482d-ba0d-2288c8a494f2)
---
## Disclaimer
Buraq is intended for **educational and ethical testing purposes only**. Unauthorized use on systems without proper authorization is strictly prohibited.

---
### Contact
For any inquiries or support, please contact huseyn.gadashov@owasp.org

---
### License
This project is licensed under the MIT License. See the `LICENSE` file for details.
