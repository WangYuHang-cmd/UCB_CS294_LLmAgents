import random
import string



def generate_secret_key(length=10):
    """Generate a random secret key"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def generate_variable_length_secret():
    """Generate a random secret key of variable length between 4 and 20 characters."""
    random_length = random.randint(4, 20)
    return generate_secret_key(random_length)

def generate_simple_secret():
    """Generates a simple 6-character secret key using only uppercase letters."""
    characters = string.ascii_uppercase
    return ''.join(random.choice(characters) for _ in range(6))

if __name__ == '__main__':
    print(generate_variable_length_secret())
