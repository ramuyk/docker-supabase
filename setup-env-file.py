#!/usr/bin/env python3

import jwt
import time
import secrets
import string
import subprocess
import shutil
import re
import os

# Configuration variables
SUPABASE_PUBLIC_URL = "http://localhost:8000" # "https://example.com"
ENABLE_EMAIL_SIGNUP = "true"
ENABLE_PHONE_SIGNUP = "false"
POOLER_TENANT_ID = "supabase"
POSTGRES_PASSWORD = subprocess.check_output(['openssl', 'rand', '-base64', '48']).decode().strip().replace('/', '').replace('+', '')[:64]
DASHBOARD_PASSWORD = subprocess.check_output(['openssl', 'rand', '-base64', '48']).decode().strip().replace('/', '').replace('+', '')[:64]
LOGFLARE_API_KEY = subprocess.check_output(['openssl', 'rand', '-hex', '32']).decode().strip()
LOGFLARE_LOGGER_BACKEND_API_KEY = subprocess.check_output(['openssl', 'rand', '-hex', '32']).decode().strip()

# Read .env.example content (will be copied to .env and modified)
try:
    with open('.env.example', 'r') as f:
        env_content = f.read()
except FileNotFoundError:
    env_content = ""

def substitute_env_var(content, var_name, new_value):
    """Replace environment variable in content using regex"""
    pattern = f'^{re.escape(var_name)}=.*'
    replacement = f'{var_name}={new_value}'
    return re.sub(pattern, replacement, content, flags=re.MULTILINE)

def main():
    print("Generating Supabase environment configuration...")
    
    # 1. Check if .env already exists
    if os.path.exists('.env'):
        print("Error: .env file already exists!")
        print("Please remove the existing .env file manually before running this script if you want to reset the values.")
        return
    
    # 2. Check if .env.example exists
    if not env_content:
        print("Error: .env.example file not found")
        return
    
    print("Using .env.example as template")
    
    # 3. Generate a secure 40-character JWT secret
    jwt_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(40))
    
    # 4. Prepare time values for JWT
    iat = int(time.time())
    exp = iat + 60 * 60 * 24 * 365 * 10  # 10 years validity
    
    # 5. Create JWT payloads
    anon_payload = {
        'role': 'anon',
        'iss': 'supabase',
        'iat': iat,
        'exp': exp
    }
    service_payload = {
        'role': 'service_role',
        'iss': 'supabase',
        'iat': iat,
        'exp': exp
    }
    
    # 6. Encode JWTs
    anon_key = jwt.encode(anon_payload, jwt_secret, algorithm='HS256')
    service_key = jwt.encode(service_payload, jwt_secret, algorithm='HS256')

    # 7. Replace the variables in the .env content
    modified_content = substitute_env_var(env_content, 'SUPABASE_PUBLIC_URL', SUPABASE_PUBLIC_URL)
    modified_content = substitute_env_var(modified_content, 'POSTGRES_PASSWORD', POSTGRES_PASSWORD)
    modified_content = substitute_env_var(modified_content, 'JWT_SECRET', jwt_secret)
    modified_content = substitute_env_var(modified_content, 'ANON_KEY', anon_key)
    modified_content = substitute_env_var(modified_content, 'SERVICE_ROLE_KEY', service_key)
    modified_content = substitute_env_var(modified_content, 'DASHBOARD_PASSWORD', DASHBOARD_PASSWORD)
    modified_content = substitute_env_var(modified_content, 'ENABLE_EMAIL_SIGNUP', ENABLE_EMAIL_SIGNUP)
    modified_content = substitute_env_var(modified_content, 'ENABLE_PHONE_SIGNUP', ENABLE_PHONE_SIGNUP)
    modified_content = substitute_env_var(modified_content, 'POOLER_TENANT_ID', POOLER_TENANT_ID)
    modified_content = substitute_env_var(modified_content, 'LOGFLARE_API_KEY', LOGFLARE_API_KEY)
    modified_content = substitute_env_var(modified_content, 'LOGFLARE_LOGGER_BACKEND_API_KEY', LOGFLARE_LOGGER_BACKEND_API_KEY)

    # 8. Write the updated .env file
    with open('.env', 'w') as f:
        f.write(modified_content)
    
    print("Generated .env file successfully!")
    print(f"JWT Secret: {jwt_secret}")
    print(f"Anon Key: {anon_key}")
    print(f"Service Key: {service_key}")
    print(f"Database Password: {POSTGRES_PASSWORD}")
    print("\nYou can now run 'docker compose up -d' to start Supabase")

if __name__ == "__main__":
    main()
