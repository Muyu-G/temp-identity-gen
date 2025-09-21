# Temporary Identity Generator (**experimental**)

A Python-based **temporary identity generator** designed to create realistic, random identities for testing and development purposes. This tool is **not intended for illegal or fraudulent activities**.

---

## Features

- Generate realistic personal identities including:
  - First and last names (male, female, or neutral)
  - Email addresses (supports temporary emails via Mail.tm or manual input)
  - Phone numbers (supports multiple countries)
  - Addresses (street, city, state, country)
  - Usernames (with hexadecimal suffixes for uniqueness)
  - Birthdates (customizable age range)
  - Random secure passwords
  - Creation timestamp
  - Generate temporary email accounts via [Mail.tm](https://mail.tm)
- Batch generation of multiple identities
- Save identities in **JSON** or **CSV** formats
- Optional preview before saving
- Detailed log files for each generated identity
- Cross-Platform: Windows, Linux, macOS ✅(banner may encounter render issues based on terminal encoding in diff os but functionality remains)
- No OS-specific assumptions ig ✅
---

## Requirements

- Python 3.8+
- Modules:
  - `colorama` (optional, for colored output)
  - `pyyaml`: For YAML output
  - `requests`: For temporary email API
  - `cryptography`: For encrypting JSON/YAML files
  - pyfiglet: For fonts
  - `Standard library`: `argparse`, `secrets`, `json`, `csv`, `datetime`, `logging`, `pathlib`, `string`, `os`, `time`, `re`

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/Muyu-G/temp-identity-gen.git
   ```
2. Navigate to the cloned repo

## Use in a virtual environment
```bash
python3 -m venv venv
```
# Activate the virtual environment:
- Linux/macOS:
```bash
source venv/bin/activate
```
- Windows CMD:
```bash
venv\Scripts\activate
```
- Install the required modules:
```bash
pip install -r requirements.txt
```


## Usage

Run the generator via command line:

```bash
python identity_generator.py
```
- In interactive mode, a menu displays available commands:
  - `generate [options]`: Generate identities with specified parameters.
  - `check-inbox [token] [options]`: Check email inbox for verification codes or links.
  - `stop`: Quit the program.

## Important Notes & Compliance, please read carefully.
- This project uses the Mail.tm API
- Prohibited uses:
  - Illegal activity of any kind
  - Selling programs or services that rely exclusively on this API
  - Creating mirror proxy services that explicitly use Mail.tm
  - This project only provides automation for testing purposes and does not monetize or compete with Mail.tm.

-  Please visit their site for more information.
## Disclaimer:
  - This tool is provided as-is for personal use.
  - The developer is **not responsible** for any misuse by third parties.
  - Users must respect the laws of their jurisdiction and Mail.tm’s Terms of Service.
By using this script, you agree to follow these rules and understand that improper use is **solely your responsibility**.

## Contribution
  - Contributions are welcome, but contributors must follow Mail.tm API rules.

## Generate Command Options
```bash
 Option                             Description                                                            Default 

  `--save`                          Save generated identity to a file                                     False 
  `--save-log`                      Save detailed identity info to a log file                             False 
  `--country`                       Country format for identity (e.g., `US`, `es`, `zh`)                  `US` 
  `--gender`                        Gender for name selection (`male`, `female`, `neutral`, `any`)        `any` 
  `--format`                        Output file format (`json`, `csv`, or `yaml`)                         `json` 
  `--count`                         Number of identities to generate                                      1 
  `--fields`                        Specify fields to include (e.g., `first_name last_name email`)        All fields 
  `--no-preview`                    Disable preview before saving                                         False 
  `--min-age`                       Minimum age for birthdate                                             18
  `--max-age`                       Maximum age for birthdate                                             65 
  `--use-temp-email`                Use Mail.tm temporary email service(verifcation code/link etc)        False                      
  `--manual-email`                  Manually specify an email address                                     None
  `--encrypt`                       Password to encrypt saved JSON/YAML files                             None

---

```
## Check-Inbox Command Options
```bash
 Option                             Description                                                            Default 

  `--code-pattern`                  Regex pattern for verification code                                   \b\d{6}\b
  `--link-pattern`                  Regex pattern for confirmation link                                   https?://[^\s]+
  `--poll-attempts`                 Number of attempts to poll inbox                                      5
  `--poll-interval`                 Interval (seconds) between inbox polling attempts                     2.0

---
```

## Notes

- Fields: Use `--fields` to select specific identity parts. Valid fields: `first_name`, `last_name`, `full_name`, `email`, `phone`, `address`, `username`, `birthdate`, `password`, `created`, `email_token`, `address_street`, `address_city`, `address_state`, `address_country`.

- Preview: `--no-preview` skips interactive preview before saving.

- Temporary Email: `--use-temp-email` generates a temporary email via Mail.tm and includes an `email_token` for inbox checking.

- Inbox Checking: Use `--check-inbox <token>` to retrieve verification codes or links from a temporary email inbox.

- Encryption: `--encrypt` enables AES encryption for JSON/YAML outputs (not supported for CSV).
- Gender: Valid options are `male`, `female`, `neutral`, or `any`.
- Output Formats: JSON and YAML support nested structures; CSV flattens nested fields (e.g., `address` becomes `address_street`, `address_city`, etc.).
- Batch Generation: Combine options, e.g., `--count 5 --country es --fields first_name email --save --encrypt mypassword`.
- You can make changes in the config dir and edit details by adding or removing etc
- In most scenarios, use the defaults should be enough, i.e,:
  ```bash
  generate
  generate --use-temp-email
  ```

## Example Commands
1. Generate 5 identities for Spain, saving only first name, last name, and email in encrypted JSON:
```bash
generate --count 5 --country es --fields first_name last_name email --save --format json --encrypt mypassword
```
2. Generate 3 identities with temporary emails and save detailed logs:
```bash
generate --count 3 --use-temp-email --save-log
```
3. Check inbox for a verification code using an email token:
```bash
check-inbox <email_token> 
```
4. Check inbox for a verification code using an email token with arguments:
```bash
check-inbox <email_token> --poll-attempts 3 --poll-interval 4
```

## Sample JSON output when using `--use-temp-email` (email with code):
```bash
{
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john.doe123@mail.tm",
  "email_token": "eyJhbGciOiJIUzI1NiIs...",
  "phone": "+1-555-123-4567",
  "address": {
    "street": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "country": "US"
  },
  "username": "johndoea1b2",
  "birthdate": "1985-07-23",
  "password": "p@SsW0rd!23",
  "created": "2025-09-20 07:50:00"
}
```
## Sample JSON output when **not** using `--use-temp-email` (email with no code):
```bash
{
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "email": "john.doe123@mail.tm",
  "phone": "+1-555-123-4567",
  "address": {
    "street": "123 Main Street",
    "city": "New York",
    "state": "NY",
    "country": "US"
  },
  "username": "johndoea1b2",
  "birthdate": "1985-07-23",
  "password": "p@SsW0rd!23",
  "created": "2025-09-20 07:50:00"
}
```
## Logging

  - Operation Logs: Saved to `logs/auto_logs/identity_generator.log`.
  - Identity Logs: Saved to `logs/manual_logs/` when `--save-log` is used.
## Decrypting Saved Files
- If you used --encrypt, decrypt JSON/YAML files with:
```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json  # or yaml

password = "your_password"
kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"salt_", iterations=100000)
key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
fernet = Fernet(key)

with open("data/identities_20250920_075000.json", "r", encoding="utf-8") as f:
    encrypted_data = f.read()
decrypted_data = fernet.decrypt(encrypted_data.encode()).decode()
identities = json.loads(decrypted_data)  # or yaml.safe_load(decrypted_data)
print(identities)
```
## License
Licensed under the MIT License.

## Warning
⚠️ This tool is for testing and development purposes only. Do not use it for illegal or fraudulent activities.
