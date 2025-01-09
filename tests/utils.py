import io
import os

from PIL import Image
import httpx
import random


def generate_random_image(width: int = 800, height: int = 600) -> Image.Image:
    """Generate random image without using numpy"""
    # Create a new image with RGB mode
    image = Image.new('RGB', (width, height))

    # Generate random pixel values
    pixels = [
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        for _ in range(width * height)
    ]

    # Set the pixel data
    image.putdata(pixels)

    return image


def generate_images(num_images: int = 10, width: int = 800, height: int = 600) -> list[Image.Image]:
    """Generate multiple random images"""
    images = []
    for _ in range(num_images):
        image = generate_random_image(width, height)
        images.append(image)
    return images

def generate_images_as_bytes(num_images: int = 10, width: int = 800, height: int = 600) -> list[io.BytesIO]:
    """Generate multiple random images and return as BytesIO objects"""
    images = []
    for _ in range(num_images):
        image = generate_random_image(width, height)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        images.append(buffer)
    return images

def generate_register_credentials() -> httpx.Response:
    rand = os.urandom(16).hex()
    return f"testemail{rand}@test.com", f"testpassword{rand}"

def login_or_register_user(email: str, password: str) -> httpx.Response:
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname",
        "email": email,
        "password": password,
        "role": "buyer",
    })

    if response.status_code > 299:
        response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
            "email": email,
            "password": password
        })

    return response

def login_or_register_agent(email: str, password: str) -> httpx.Response:
    response = httpx.post("http://localhost:8000/api/v1/auth/register", json={
        "name": "testname",
        "email": email,
        "password": password,
        "role": "agent",
        "serial_number": "123456",
    })

    if response.status_code > 299:
        response = httpx.post("http://localhost:8000/api/v1/auth/login", json={
            "email": email,
            "password": password
        })

    return response


def main():
    generate_random_image()

if __name__ == "__main__":
    main()
