# generator.py
import secrets
import json
import csv
import yaml
from datetime import datetime
from typing import Dict, Union, List, Optional
from pathlib import Path
import string
import requests
import time
import re
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging
from utils import fore, style, COLORAMA_AVAILABLE

class TemporaryIdentityGenerator:
    def __init__(self, config_dir: str = "config"):
        """Initialize the identity generator with configuration files."""
        self.config_dir = config_dir
        self.state_maps = {
            "US": ["CA", "NY", "TX"],
            "in": ["MH", "DL", "KA"]
        }
        # Fallback defaults for config files
        self.first_names = {"male": ["John", "Michael"], "female": ["Mary", "Sarah"], "neutral": ["Alex", "Taylor"]}
        self.last_names = {"US": ["Smith", "Johnson"]}
        self.domains = ["example.com", "test.org"]
        self.streets = {"US": ["Main St", "Elm St"], "in": ["MG Road", "Park Ave"]}
        self.addresses = {"CA": ["San Francisco", "Los Angeles"], "NY": ["New York", "Albany"], "MH": ["Mumbai", "Pune"]}
        self.phone_formats = {"US": "+1-###-###-####", "in": "+91-#####-#####"}
        
        # Load configuration files
        try:
            config_path = Path(config_dir)
            with open(config_path / "first_names.json", 'r', encoding='utf-8') as f:
                self.first_names = json.load(f)
                if not all(key in self.first_names for key in ["male", "female", "neutral"]):
                    print(f"{fore.YELLOW}Warning: first_names.json missing required keys, using fallbacks.{fore.RESET if COLORAMA_AVAILABLE else ''}")
                    logging.warning("first_names.json validation failed, using fallbacks")
            with open(config_path / "last_names.json", 'r', encoding='utf-8') as f:
                self.last_names = json.load(f)
                if not isinstance(self.last_names, dict) or not all(isinstance(v, list) for v in self.last_names.values()):
                    print(f"{fore.YELLOW}Warning: last_names.json has invalid format, using fallbacks.{fore.RESET if COLORAMA_AVAILABLE else ''}")
                    logging.warning("last_names.json validation failed, using fallbacks")
            with open(config_path / "domains.json", 'r', encoding='utf-8') as f:
                self.domains = json.load(f)
                if not isinstance(self.domains, list):
                    print(f"{fore.YELLOW}Warning: domains.json has invalid format, using fallbacks.{fore.RESET if COLORAMA_AVAILABLE else ''}")
                    logging.warning("domains.json validation failed, using fallbacks")
            with open(config_path / "streets.json", 'r', encoding='utf-8') as f:
                self.streets = json.load(f)
                if not isinstance(self.streets, dict) or not all(isinstance(v, list) for v in self.streets.values()):
                    print(f"{fore.YELLOW}Warning: streets.json has invalid format, using fallbacks.{fore.RESET if COLORAMA_AVAILABLE else ''}")
                    logging.warning("streets.json validation failed, using fallbacks")
            with open(config_path / "addresses.json", 'r', encoding='utf-8') as f:
                self.addresses = json.load(f)
                if not isinstance(self.addresses, dict) or not all(isinstance(v, list) for v in self.addresses.values()):
                    print(f"{fore.YELLOW}Warning: addresses.json has invalid format, using fallbacks.{fore.RESET if COLORAMA_AVAILABLE else ''}")
                    logging.warning("addresses.json validation failed, using fallbacks")
            with open(config_path / "phone_formats.json", 'r', encoding='utf-8') as f:
                self.phone_formats = json.load(f)
                if not isinstance(self.phone_formats, dict) or not all(isinstance(v, str) for v in self.phone_formats.values()):
                    print(f"{fore.YELLOW}Warning: phone_formats.json has invalid format, using fallbacks.{fore.RESET if COLORAMA_AVAILABLE else ''}")
                    logging.warning("phone_formats.json validation failed, using fallbacks")
        except FileNotFoundError as e:
            print(f"{fore.YELLOW}Warning: Configuration file {e.filename} not found, using fallbacks.{fore.RESET if COLORAMA_AVAILABLE else ''}")
            logging.warning(f"Configuration file {e.filename} not found, using fallbacks")
        except json.JSONDecodeError as e:
            print(f"{fore.YELLOW}Warning: Configuration file {e} is invalid JSON, using fallbacks.{fore.RESET if COLORAMA_AVAILABLE else ''}")
            logging.warning(f"Configuration file {e} is invalid JSON, using fallbacks")

    def generate_name(self, gender: str, country: str) -> tuple[str, str]:
        """Generate a random first and last name based on gender and country."""
        gender = gender.lower() if gender else 'any'
        if gender == 'any':
            gender = secrets.choice(['male', 'female', 'neutral'])
        
        first_name_key = gender if gender in self.first_names else 'neutral'
        first_name = secrets.choice(self.first_names.get(first_name_key, self.first_names['neutral']))
        
        last_name_key = country if country in self.last_names else 'US'
        last_name = secrets.choice(self.last_names.get(last_name_key, self.last_names['US']))
        
        return first_name, last_name

    def generate_email(self, first_name: str, last_name: str, country: str) -> str:
        """Generate a random email address."""
        domain = secrets.choice(self.domains)
        username = f"{first_name.lower()}.{last_name.lower()}{secrets.randbelow(1000)}"
        return f"{username}@{domain}"

    def generate_temp_email(self) -> tuple[Optional[str], Optional[str]]:
        """Generate a temporary email using Mail.tm."""
        retries = 3
        for attempt in range(retries):
            try:
                # Get available domains from Mail.tm
                response = requests.get("https://api.mail.tm/domains", timeout=5)
                response.raise_for_status()
                domains = response.json().get('hydra:member', [])
                if not domains:
                    logging.warning("No domains available from Mail.tm")
                    break
                domain = secrets.choice([d['domain'] for d in domains])

                # Generate random username and password
                username = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
                password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
                email = f"{username}@{domain}"

                # Create account
                payload = {"address": email, "password": password}
                response = requests.post("https://api.mail.tm/accounts", json=payload, timeout=5)
                response.raise_for_status()

                # Get token for inbox access
                response = requests.post("https://api.mail.tm/token", json=payload, timeout=5)
                response.raise_for_status()
                token = response.json().get('token')
                logging.info(f"Created Mail.tm account: {email}")
                return email, token
            except requests.RequestException as e:
                logging.error(f"Mail.tm attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue

        print(f"{fore.RED if COLORAMA_AVAILABLE else ''}Failed to create Mail.tm account after {retries} attempts.{fore.RESET if COLORAMA_AVAILABLE else ''}")
        return None, None

    def generate_phone(self, country: str) -> str:
        """Generate a random phone number based on country format."""
        phone_format = self.phone_formats.get(country, self.phone_formats['US'])
        phone = ''.join(secrets.choice(string.digits) if c == '#' else c for c in phone_format)
        return phone

    def generate_address(self, country: str) -> Dict[str, str]:
        """Generate a random address based on country."""
        country = country if country in self.state_maps else 'US'
        state = secrets.choice(self.state_maps.get(country, self.state_maps['US']))
        street = secrets.choice(self.streets.get(country, self.streets['US']))
        city = secrets.choice(self.addresses.get(state, self.addresses['CA']))
        return {
            "street": f"{secrets.randbelow(1000)} {street}",
            "city": city,
            "state": state,
            "country": country
        }

    def generate_username(self, first_name: str, last_name: str) -> str:
        """Generate a random username."""
        base = f"{first_name.lower()}{last_name.lower()}"
        suffix = secrets.token_hex(2)
        return f"{base}{suffix}"

    def generate_birthdate(self, min_age: int, max_age: int) -> str:
        """Generate a random birthdate within the age range."""
        current_year = datetime.now().year
        start_year = current_year - max_age
        end_year = current_year - min_age
        year = secrets.randbelow(end_year - start_year + 1) + start_year
        month = secrets.randbelow(12) + 1
        day = secrets.randbelow(28) + 1  # Simplified to avoid invalid dates
        return f"{year}-{month:02d}-{day:02d}"

    def generate_password(self) -> str:
        """Generate a random secure password."""
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(chars) for _ in range(12))

    def generate_identity(self, country: str = "US", gender: str = "any", use_temp_email: bool = False, 
                        manual_email: Optional[str] = None, min_age: int = 18, max_age: int = 65) -> Dict[str, Union[str, Dict]]:
        """Generate a single identity with specified parameters."""
        first_name, last_name = self.generate_name(gender, country)
        full_name = f"{first_name} {last_name}"
        
        if manual_email:
            email = manual_email
            email_token = None
        elif use_temp_email:
            email, email_token = self.generate_temp_email()
            if not email:
                email = self.generate_email(first_name, last_name, country)
                email_token = None
        else:
            email = self.generate_email(first_name, last_name, country)
            email_token = None

        identity = {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "email": email,
            "phone": self.generate_phone(country),
            "address": self.generate_address(country),
            "username": self.generate_username(first_name, last_name),
            "birthdate": self.generate_birthdate(min_age, max_age),
            "password": self.generate_password(),
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if email_token:
            identity["email_token"] = email_token
        return identity

    def check_inbox(self, token: str, code_pattern: str = r'\b\d{6}\b', link_pattern: str = r'https?://[^\s]+', 
                    poll_attempts: int = 5, poll_interval: float = 2.0) -> tuple[Optional[str], Optional[str]]:
        """Check email inbox for verification code or link using Mail.tm."""
        for attempt in range(poll_attempts):
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get("https://api.mail.tm/messages", headers=headers, timeout=5)
                response.raise_for_status()
                messages = response.json().get('hydra:member', [])
                for message in messages:
                    msg_id = message.get('id')
                    response = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=5)
                    response.raise_for_status()
                    content = response.json().get('text', '')
                    code_match = re.search(code_pattern, content)
                    if code_match:
                        logging.info(f"Found verification code in Mail.tm inbox: {code_match.group()}")
                        return code_match.group(), None
                    link_match = re.search(link_pattern, content)
                    if link_match:
                        logging.info(f"Found confirmation link in Mail.tm inbox: {link_match.group()}")
                        return None, link_match.group()
            except requests.RequestException as e:
                logging.error(f"Inbox check attempt {attempt + 1} failed: {e}")
            time.sleep(poll_interval)
        logging.warning("No verification code or link found after polling")
        return None, None

    def display_identity(self, identity: Dict[str, Union[str, Dict]]) -> None:
        """Display a single identity in a formatted way."""
        print(f"{style.BRIGHT if COLORAMA_AVAILABLE else ''}============================================================{style.RESET_ALL if COLORAMA_AVAILABLE else ''}")
        print(f"{style.BRIGHT if COLORAMA_AVAILABLE else ''}GENERATED IDENTITY{style.RESET_ALL if COLORAMA_AVAILABLE else ''}")
        print(f"{style.BRIGHT if COLORAMA_AVAILABLE else ''}============================================================{style.RESET_ALL if COLORAMA_AVAILABLE else ''}")
        for key, value in identity.items():
            if key == "address" and isinstance(value, dict):  # Type check for dictionary
                print("Address:")
                for addr_key, addr_value in value.items():
                    print(f"  {addr_key.capitalize()}: {addr_value}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        print(f"{style.BRIGHT if COLORAMA_AVAILABLE else ''}============================================================{style.RESET_ALL if COLORAMA_AVAILABLE else ''}")

    def save_identity(self, identities: List[Dict[str, Union[str, Dict]]], output_format: str, 
                     encrypt_password: Optional[str] = None) -> None:
        """Save identities to a file in the specified format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data", exist_ok=True)
        
        if output_format == "csv":
            filename = f"data/identities_{timestamp}.csv"
            flat_identities = []
            for identity in identities:
                flat_identity = {}
                for key, value in identity.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            flat_identity[f"{key}_{subkey}"] = subvalue
                    else:
                        flat_identity[key] = value
                flat_identities.append(flat_identity)
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flat_identities[0].keys())
                writer.writeheader()
                writer.writerows(flat_identities)
        else:
            filename = f"data/identities_{timestamp}.{output_format}"
            data = json.dumps(identities) if output_format == "json" else yaml.dump(identities, allow_unicode=True)
            if encrypt_password:
                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=b"salt_", iterations=100000)
                key = base64.urlsafe_b64encode(kdf.derive(encrypt_password.encode()))
                fernet = Fernet(key)
                data = fernet.encrypt(data.encode()).decode()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(data)
        
        print(f"{fore.GREEN if COLORAMA_AVAILABLE else ''}Identities saved to {filename}{fore.RESET if COLORAMA_AVAILABLE else ''}")
        logging.info(f"Identities saved to {filename}")

    def save_identity_log(self, identity: Dict[str, Union[str, Dict]], filename: str) -> None:
        """Save detailed identity information to a log file."""
        os.makedirs("logs/manual_logs", exist_ok=True)
        filepath = f"logs/manual_logs/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("Generated Identity Details\n")
            f.write("==========================\n")
            for key, value in identity.items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for subkey, subvalue in value.items():
                        f.write(f"  {subkey}: {subvalue}\n")
                else:
                    f.write(f"{key}: {value}\n")
        logging.info(f"Identity log saved to {filepath}")

    def generate_batch_identities(self, count: int, country: str, gender: str, save: bool, fields: Optional[List[str]], 
                                 output_format: str, preview: bool = True, min_age: int = 18, max_age: int = 65,
                                 use_temp_email: bool = False, manual_email: Optional[str] = None,
                                 encrypt_password: Optional[str] = None) -> List[Dict[str, Union[str, Dict]]]:
        """Generate a batch of identities with specified parameters."""
        identities = []
        all_valid = ['first_name', 'last_name', 'full_name', 'email', 'phone', 'address', 'username', 
                     'birthdate', 'password', 'created', 'email_token', 'address_street', 'address_city', 
                     'address_state', 'address_country']
        
        for _ in range(count):
            identity = self.generate_identity(country, gender, use_temp_email, manual_email, min_age, max_age)
            if fields:
                filtered_identity = {}
                for field in fields:
                    if field in identity:
                        filtered_identity[field] = identity[field]
                    elif field in ['address_street', 'address_city', 'address_state', 'address_country']:
                        address = identity.get('address')
                        if isinstance(address, dict):  # Type check for dictionary
                            subkey = field.split('_')[1]
                            if subkey in address:  # Check if subkey exists
                                filtered_identity[field] = address[subkey]
                identity = filtered_identity
            identities.append(identity)
            
            if preview:
                self.display_identity(identity)
                if use_temp_email and 'email_token' in identity:
                    print(f"{fore.CYAN if COLORAMA_AVAILABLE else ''}To retrieve verification code or link from inbox, run the script with check-inbox {identity['email_token']} [--code-pattern <pattern>] [--link-pattern <pattern>]{fore.RESET if COLORAMA_AVAILABLE else ''}")
        
        if save:
            self.save_identity(identities, output_format, encrypt_password)
        
        return identities