import requests

from src.config import API_BASE_URL, BOT_API_KEY


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.api_key = BOT_API_KEY
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    async def get_verification_code(self, user_id: int) -> dict | None:
        try:
            response = requests.get(
                f"{self.base_url}/reg/{user_id}",
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    async def get_user_by_tg_user_id(self, tg_user_id: int) -> dict | None:
        try:
            response = requests.get(
                f"{self.base_url}/users/tg/{tg_user_id}",
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    async def update_verification_code(self, user_id: int, tg_user_id: int, tg_username: str) -> dict | None:
        try:
            response = requests.patch(
                f"{self.base_url}/reg/{user_id}",
                params={'tg_user_id': tg_user_id, 'tg_username': tg_username},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    async def get_purchase(self, purchase_id: int) -> dict | None:
        try:
            response = requests.get(
                f"{self.base_url}/purchases/{purchase_id}",
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    async def get_product(self, product_id: int) -> dict | None:
        try:
            response = requests.get(
                f"{self.base_url}/products/{product_id}",
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None

    async def get_user(self, user_id: int) -> dict | None:
        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}",
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None