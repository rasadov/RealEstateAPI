import os
from dotenv import load_dotenv

load_dotenv()

TEST_MODERATOR_EMAIL = os.getenv("MODERATOR_EMAIL")
TEST_MODERATOR_PASS = os.getenv("MODERATOR_PASSWORD")

TEST_AGENT_EMAIL = os.getenv("AGENT_EMAIL")
TEST_AGENT_PASS = os.getenv("AGENT_PASSWORD")

TEST_CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
TEST_CLIENT_PASS = os.getenv("CLIENT_PASSWORD")
