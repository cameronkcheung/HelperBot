import re
import base64
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def process_string(string):
    return re.findall(r'/(.*?)/', string)[0]


def mock_string(string):
    exp = []

    for i in range(len(string)):
        if i % 2 == 0:
            exp.append(string[i].swapcase())
        else:
            exp.append(string[i])

    output = "".join(exp)
    return output


def to_rn(in_num: int):
    numeral_dict = {1000: "M", 900: "CM", 500: "D", 100: "C", 90: "XC", 50: "L", 10: "X", 9: "IX", 5: "V", 1: "I"}

    output = ""

    while in_num != 0:
        for key in numeral_dict:

            if in_num >= key:
                output += numeral_dict.get(key)
                in_num = in_num - key
                break
    return output


def encode_morse(message):
    char_to_dots = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..', ' ': ' ', '0': '-----',
        '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..', '9': '----.',
        '&': '.-...', "'": '.----.', '@': '.--.-.', ')': '-.--.-', '(': '-.--.',
        ':': '---...', ',': '--..--', '=': '-...-', '!': '-.-.--', '.': '.-.-.-',
        '-': '-....-', '+': '.-.-.', '"': '.-..-.', '?': '..--..', '/': '-..-.'
    }
    output = ""
    for c in str(message).upper():
        output = output + char_to_dots.get(c) + " "
    output = output[:-1]
    return output


def decode_morse(message):
    dots_to_chars = {'.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', '....': 'H',
                     '..': 'I',
                     '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q',
                     '.-.': 'R',
                     '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z',
                     ' ': ' ',
                     '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6',
                     '--...': '7',
                     '---..': '8', '----.': '9', '.-...': '&', '.----.': "'", '.--.-.': '@', '-.--.-': ')',
                     '-.--.': '(',
                     '---...': ':', '--..--': ',', '-...-': '=', '-.-.--': '!', '.-.-.-': '.', '-....-': '-',
                     '.-.-.': '+',
                     '.-..-.': '"', '..--..': '?', '-..-.': '/'
                     }
    output = ""
    words = message.split('   ')
    for word in words:
        for char in word.split(' '):
            output = output + dots_to_chars.get(char)
        output = output + " "
    output = output[:-1]
    return output


def aes_encrypt(message, password):
    message = message.encode()
    password = password.encode()
    salt = b'9639242'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    encrypted = f.encrypt(message)
    return encrypted.decode("utf-8")


def aes_decrypt(message, password):
    try:
        message = message.encode()
        password = password.encode()
        salt = b'9639242'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        f = Fernet(key)
        decrypted = f.decrypt(message)
        return decrypted.decode("utf-8")
    except cryptography.fernet.InvalidToken:
        return None