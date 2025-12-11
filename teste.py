from werkzeug.security import generate_password_hash, check_password_hash

senha = "1234"
hash = generate_password_hash(senha)
print(hash)
senha_informada = "4321"

if check_password_hash(hash, senha_informada):
    print("Senha OK")
else:
    print("Senha errada")