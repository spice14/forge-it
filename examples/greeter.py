def greet(name):
    if not name:
        return "Hello, stranger!"
    return f"Hello, {name}!"

def farewell(name):
    if name:
        return f"Goodbye, {name}."
    return "Goodbye!"
