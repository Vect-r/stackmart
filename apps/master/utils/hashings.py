import hashlib

# data = "Hello, world!"

# # Encode the string to bytes using utf-8
# encoded_data = data.encode('utf-8')

# # Create an MD5 hash object
# md5_hash = hashlib.md5()

# # Update the hash object with the encoded data
# md5_hash.update(encoded_data)

# # Get the hash in a human-readable hexadecimal string format (32 characters)
# hex_digest = md5_hash.hexdigest()

# print(f"Original string: {data}")
# print(f"MD5 hash: {hex_digest}")

def hashIt(password):
    password+=".creepyp@st@"
    encoded_data = password.encode('utf-8')
    md5_hash = hashlib.md5()
    md5_hash.update(encoded_data)
    hex_digest = md5_hash.hexdigest()
    return hex_digest
