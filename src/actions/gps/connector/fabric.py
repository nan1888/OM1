import logging

import requests
from pydantic import Field

from actions.base import ActionConfig, ActionConnector
from actions.gps.interface import GPSAction, GPSInput
from providers.io_provider import IOProvider


class GPSFabricConfig(ActionConfig):
    """
    Configuration for GPS Fabric connector.

    Parameters
    ----------
    fabric_endpoint : str
        The endpoint URL for the Fabric network.
    """

    fabric_endpoint: str = Field(
        default="http://localhost:8545",
        description="The endpoint URL for the Fabric network.",
    )


class GPSFabricConnector(ActionConnector[GPSFabricConfig, GPSInput]):
    """
    Connector that shares GPS coordinates via a Fabric network.
    """

    def __init__(self, config: GPSFabricConfig):
        """
        Initialize the GPSFabricConnector.

        Parameters
        ----------
        config : GPSFabricConfig
            Configuration for the action connector.
        """
        super().__init__(config)

        # Set IO Provider
        self.io_provider = IOProvider()

        # Set fabric endpoint configuration
        self.fabric_endpoint = self.config.fabric_endpoint

    async def connect(self, output_interface: GPSInput) -> None:
        """
        Connect to the Fabric network and send GPS coordinates.

        Parameters
        ----------
        output_interface : GPSInput
            The GPS input containing the action to be performed.
        """
        logging.info(f"GPSFabricConnector: {output_interface.action}")

        if output_interface.action == GPSAction.SHARE_LOCATION:
            # Send GPS coordinates to the Fabric network
            self.send_coordinates()

    def send_coordinates(self) -> None:
        """
        Send GPS coordinates to the Fabric network.
        """
        logging.info("GPSFabricConnector: Sending coordinates to Fabric network.")
        latitude = self.io_provider.get_dynamic_variable("latitude")
        longitude = self.io_provider.get_dynamic_variable("longitude")
        yaw = self.io_provider.get_dynamic_variable("yaw_deg")
        logging.info(f"GPSFabricConnector: Latitude: {latitude}")
        logging.info(f"GPSFabricConnector: Longitude: {longitude}")
        logging.info(f"GPSFabricConnector: Yaw: {yaw}")

        # Fix 1: Proper coordinate validation (OR instead of AND)
        if latitude is None or longitude is None or yaw is None:
            logging.error(
                f"GPSFabricConnector: Invalid coordinates - "
                f"lat={latitude}, lon={longitude}, yaw={yaw}"
            )
            return None

        try:
            share_status_response = requests.post(
                f"{self.fabric_endpoint}",
                json={
                    "method": "omp2p_shareStatus",
                    "params": [
                        {"latitude": latitude, "longitude": longitude, "yaw": yaw}
                    ],
                    "id": 1,
                    "jsonrpc": "2.0",
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            # Fix 3: Verify HTTP status code
            share_status_response.raise_for_status()

            # Parse JSON response
            response = share_status_response.json()

            # Fix 4: Validate JSON-RPC error field
            if "error" in response:
                logging.error(
                    f"GPSFabricConnector: JSON-RPC error - {response['error']}"
                )
                return None

            # Check for successful result
            if "result" in response and response["result"]:
                logging.info("GPSFabricConnector: Coordinates shared successfully.")
                return None  # Fix 2: Explicit return on success
            else:
                logging.error(
                    "GPSFabricConnector: Failed to share coordinates - "
                    "no valid result in response."
                )
                return None

        except requests.exceptions.Timeout:
            logging.error(
                "GPSFabricConnector: Request timeout when sending coordinates."
            )
            return None
        except requests.exceptions.HTTPError as e:
            logging.error(f"GPSFabricConnector: HTTP error - {e}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"GPSFabricConnector: Network error - {e}")
            return None
        except ValueError as e:
            # JSON decode error
            logging.error(f"GPSFabricConnector: Invalid JSON response - {e}")
            return None
        except Exception as e:
            logging.error(f"GPSFabricConnector: Unexpected error - {e}")
            return None
