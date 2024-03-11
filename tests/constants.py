import os


MASTER_REALM = "master"
ADMIN_CLI_CLIENT = "admin-cli"


TEST_SERVER_URL = os.environ.get("TEST_SERVER_URL", "http://localhost:9090")

TEST_MASTER_USER = "admin"
TEST_MASTER_PASSWORD = os.environ.get("TEST_MASTER_PASSWORD", "admin")

TEST_REALM = os.environ.get("TEST_REALM", "orwell")

TEST_CLIENT_ID = os.environ.get("TEST_CLIENT_ID", "weir")
TEST_CLIENT_SECRET = os.environ.get("TEST_CLIENT_SECRET", "rockyyyy!")

TEST_USER = os.environ.get("TEST_USER", "constant")
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "rabbit")
