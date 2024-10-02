import random
import hashlib

from crypto.Cipher import AES


def is_prime(n, k=40):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_large_prime(bit_length):
    while True:
        prime_candidate = random.getrandbits(bit_length)
        prime_candidate |= (1 << (bit_length - 1)) | 1
        if is_prime(prime_candidate):
            return prime_candidate


P = generate_large_prime(2048)
G = 2


def generate_dh_key():
    private_key = random.randint(2, P - 2)
    public_key = pow(G, private_key, P)
    return private_key, public_key


def generate_shared_secret(private_key, other_public_key):
    shared_secret = pow(other_public_key, private_key, P)
    return shared_secret


def kdf(shared_secret, msg_key):
    data = shared_secret.to_bytes(256, 'big') + msg_key
    sha256_digest = hashlib.sha256(data).digest()

    aes_key = sha256_digest[:32]
    aes_iv = sha256_digest[32:]
    return aes_key, aes_iv


def generate_msg_key(message):
    return hashlib.sha256(message.encode()).digest()[:16]


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def aes_ige_encrypt(plaintext, aes_key, aes_iv):
    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext


def aes_ige_decrypt(ciphertext, aes_key, aes_iv):
    cipher = AES.new(aes_key, AES.MODE_CBC, aes_iv)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext
