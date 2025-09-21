# identity_generator.py
import argparse
import os
from typing import List, Optional
from generator import TemporaryIdentityGenerator
from utils import print_banner, fore, style, COLORAMA_AVAILABLE

def main():
    """Main function to run the identity generator in interactive mode."""
    generator = TemporaryIdentityGenerator()
    print_banner()
    
    while True:
        print("\nAvailable Commands:")
        print("  generate  - Generate identities with specified parameters")
        print("  check-inbox - Check email inbox for verification code or link")
        print("  clean     - Clear recent command output")
        print("  stop      - Quit the program")
        
        command = input("\nEnter a command (e.g., 'generate --count 2 --country US --save'): ").strip()
        args_list = command.split()
        
        if not args_list:
            continue
        if args_list[0].lower() == "stop":
            print("Exiting program.")
            break
        elif args_list[0].lower() == "clean":
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
            print_banner()
            continue
        elif args_list[0].lower() == "generate":
            all_valid = ['first_name', 'last_name', 'full_name', 'email', 'phone', 'address', 'username', 
                         'birthdate', 'password', 'created', 'email_token', 'address_street', 'address_city', 
                         'address_state', 'address_country']
            parser = argparse.ArgumentParser(description="Generate temporary identities")
            parser.add_argument("--save", action="store_true", help="Save generated identity to a file")
            parser.add_argument("--save-log", action="store_true", help="Save detailed identity info to a log file")
            parser.add_argument("--country", default="US", help="Country format for identity (e.g., US, es, zh)")
            parser.add_argument("--gender", default="any", choices=["male", "female", "neutral", "any"], 
                              help="Gender for name selection")
            parser.add_argument("--format", default="json", choices=["json", "csv", "yaml"], help="Output file format")
            parser.add_argument("--count", type=int, default=1, help="Number of identities to generate")
            parser.add_argument("--fields", nargs="+", help="Fields to include (e.g., first_name last_name email)")
            parser.add_argument("--no-preview", action="store_true", help="Disable preview before saving")
            parser.add_argument("--min-age", type=int, default=18, help="Minimum age for birthdate")
            parser.add_argument("--max-age", type=int, default=65, help="Maximum age for birthdate")
            parser.add_argument("--use-temp-email", action="store_true", help="Use Mail.tm temporary email service")
            parser.add_argument("--manual-email", type=str, help="Manually specify an email address")
            parser.add_argument("--encrypt", type=str, help="Password to encrypt saved JSON/YAML files")
            try:
                args = parser.parse_args(args_list[1:])
                # Validate arguments
                if args.count < 1:
                    print("Error: Count must be positive")
                    continue
                if args.min_age < 0 or args.max_age < args.min_age or args.max_age > 120:
                    print("Error: Invalid age range (min_age >=0, min_age <= max_age <=120)")
                    continue
                if args.use_temp_email and args.manual_email:
                    print("Error: Cannot use both --use-temp-email and --manual-email")
                    continue
                if args.encrypt and args.format == "csv":
                    print("Error: Encryption is not supported for CSV format")
                    continue
                if args.fields and not all(field in all_valid for field in args.fields):
                    print(f"Warning: Invalid fields specified. Valid fields: {all_valid}")
                    args.fields = None

                identities = generator.generate_batch_identities(
                    args.count, 
                    args.country, 
                    args.gender, 
                    args.save, 
                    args.fields, 
                    args.format, 
                    preview=not args.no_preview, 
                    min_age=args.min_age, 
                    max_age=args.max_age,
                    use_temp_email=args.use_temp_email, 
                    manual_email=args.manual_email,
                    encrypt_password=args.encrypt
                )
                
                if args.no_preview:
                    for identity in identities:
                        generator.display_identity(identity)
                        if "email_token" in identity:
                            print(f"{fore.CYAN if COLORAMA_AVAILABLE else ''}To retrieve verification code or link from inbox, run the script with check-inbox {identity['email_token']} [--code-pattern <pattern>] [--link-pattern <pattern>]{fore.RESET if COLORAMA_AVAILABLE else ''}")

                if args.save_log:
                    for i, identity in enumerate(identities):
                        if len(identities) > 1:
                            log_filename = f"identity_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}.log"
                        else:
                            log_filename = f"identity_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                        generator.save_identity_log(identity, log_filename)
            except SystemExit:
                print("Error: Invalid arguments.")
            except Exception as e:
                print(f"Error: {e}")
        elif args_list[0].lower() == "check-inbox":
            parser = argparse.ArgumentParser(description="Check email inbox")
            parser.add_argument("token", help="Email token for inbox access")
            parser.add_argument("--code-pattern", default=r'\b\d{6}\b', help="Regex pattern for verification code")
            parser.add_argument("--link-pattern", default=r'https?://[^\s]+', help="Regex pattern for confirmation link")
            parser.add_argument("--poll-attempts", type=int, default=5, help="Number of attempts to poll inbox")
            parser.add_argument("--poll-interval", type=float, default=2.0, help="Interval (seconds) between inbox polling attempts")
            try:
                args = parser.parse_args(args_list[1:])
                if args.poll_attempts < 1:
                    print("Error: Poll attempts must be positive")
                    continue
                if args.poll_interval <= 0:
                    print("Error: Poll interval must be positive")
                    continue
                code, link = generator.check_inbox(
                    args.token, 
                    code_pattern=args.code_pattern, 
                    link_pattern=args.link_pattern,
                    poll_attempts=args.poll_attempts,
                    poll_interval=args.poll_interval
                )
                if code:
                    print(f"{fore.GREEN if COLORAMA_AVAILABLE else ''}Retrieved Verification Code: {code}{fore.RESET if COLORAMA_AVAILABLE else ''}")
                elif link:
                    print(f"{fore.GREEN if COLORAMA_AVAILABLE else ''}Retrieved Confirmation Link: {link}{fore.RESET if COLORAMA_AVAILABLE else ''}")
                    print(f"{fore.YELLOW if COLORAMA_AVAILABLE else ''}Please open the link in a browser to confirm.{fore.RESET if COLORAMA_AVAILABLE else ''}")
                else:
                    print(f"{fore.RED if COLORAMA_AVAILABLE else ''}No verification code or link found after polling.{fore.RESET if COLORAMA_AVAILABLE else ''}")
            except SystemExit:
                print("Error: Invalid arguments.")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"Unknown command: {args_list[0]}.")

if __name__ == "__main__":
    from datetime import datetime
    main()