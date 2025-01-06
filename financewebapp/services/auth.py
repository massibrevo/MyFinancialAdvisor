import yaml
from yaml.loader import SafeLoader
import os

def load_auth_config():
    """Load the authentication configuration from the YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "../../auth_config.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path) as file:
        return yaml.load(file, Loader=SafeLoader)

def get_authenticator():
    """Initialize and return the Streamlit Authenticator object."""
    config = load_auth_config()
    if not config or "credentials" not in config:
        raise ValueError("Invalid configuration. Ensure 'credentials' is defined.")
    import streamlit_authenticator as stauth
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )
    return authenticator
