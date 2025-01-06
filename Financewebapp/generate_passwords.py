import bcrypt

# Lista delle password da hashare
passwords = ['yourpassword', 'anotherpassword']

# Genera gli hash delle password
hashed_passwords = [bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() for password in passwords]

# Stampa gli hash generati
print("Hashed passwords:")
for password, hashed in zip(passwords, hashed_passwords):
    print(f"Password: {password} -> Hash: {hashed}")
