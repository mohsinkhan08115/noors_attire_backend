import os
from fastapi import Request

def save_local_image(file_data: bytes, filename: str, request: Request) -> str:
    os.makedirs(os.path.dirname(f'uploads/{filename}'), exist_ok=True)
    with open(f'uploads/{filename}', 'wb') as f:
        f.write(file_data)
    base_url = str(request.base_url).rstrip('/')
    return f'{base_url}/uploads/{filename}'
