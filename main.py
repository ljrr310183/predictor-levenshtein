def greeting():
    name = input("Ingrese su nombre: ")
    if not name:
        print("EL nombre es requeriDo")
        return
        
    print(f"Hola {name}")

greeting()