"""Computer vision interface: classical OpenCV heuristics for image analysis.

Estimates colonization, pinheads, fruits and contamination from a photo or
camera frame using HSV color thresholding and contour/blob counting. These
are heuristics (tunable via ``Config``), not a trained model — no labeled
mushroom-image dataset exists in this repo to train one. Swapping in a real
trained model (e.g. YOLOv8) later only requires reimplementing the estimate_*
methods below; the rest of the twin does not need to change.
"""

import cv2
import numpy as np

from ..config import Config
from ..state import TwinState


class ComputerVisionInterface:
    """Estimate colonization, pinheads, fruits and contamination from images."""

    def __init__(self):
        self.camera_connected = False
        self.last_image = None

    def connect_camera(self) -> None:
        self.camera_connected = True

    def disconnect_camera(self) -> None:
        self.camera_connected = False

    def load_image(self, path: str):
        """Load a photo from disk into ``self.last_image``."""
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Could not read image file: {path}")
        self.last_image = image
        return self.last_image

    def capture_image(self, source: int = 0):
        """Grab a single frame from a webcam/USB camera.

        Falls back to returning ``self.last_image`` (e.g. a previously loaded
        photo) if no camera is available, so callers without physical
        hardware attached can still use ``load_image`` + this interface.
        """
        capture = cv2.VideoCapture(source)
        try:
            if not capture.isOpened():
                return self.last_image
            self.camera_connected = True
            ok, frame = capture.read()
            if ok:
                self.last_image = frame
        finally:
            capture.release()
        return self.last_image

    def _mycelium_mask(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return cv2.inRange(
            hsv, np.array(Config.MYCELIUM_HSV_LOWER), np.array(Config.MYCELIUM_HSV_UPPER)
        )

    def _mold_mask(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return cv2.inRange(
            hsv, np.array(Config.MOLD_HSV_LOWER), np.array(Config.MOLD_HSV_UPPER)
        )

    @staticmethod
    def _count_blobs(mask, area_range) -> int:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area, max_area = area_range
        return sum(1 for c in contours if min_area <= cv2.contourArea(c) <= max_area)

    def estimate_colonization(self, image) -> float:
        """% of frame covered by white/cream mycelium color."""
        mask = self._mycelium_mask(image)
        return float(100.0 * np.count_nonzero(mask) / mask.size)

    def estimate_contamination(self, image) -> float:
        """% of frame covered by mold-colored (green/black) regions."""
        mask = self._mold_mask(image)
        return float(100.0 * np.count_nonzero(mask) / mask.size)

    def detect_pinheads(self, image) -> int:
        """Count small mycelium-colored blobs sized like pinheads."""
        mask = self._mycelium_mask(image)
        return self._count_blobs(mask, Config.PINHEAD_BLOB_AREA)

    def detect_fruits(self, image) -> int:
        """Count larger mycelium-colored blobs sized like mature fruit bodies."""
        mask = self._mycelium_mask(image)
        return self._count_blobs(mask, Config.FRUIT_BLOB_AREA)

    def analyze(self, image) -> dict:
        """Run all estimators once and return a single analysis dict."""
        mycelium_mask = self._mycelium_mask(image)
        colonization = float(100.0 * np.count_nonzero(mycelium_mask) / mycelium_mask.size)
        contamination = self.estimate_contamination(image)
        return {
            "colonization": colonization,
            "contamination": contamination,
            "pinheads": self._count_blobs(mycelium_mask, Config.PINHEAD_BLOB_AREA),
            "fruits": self._count_blobs(mycelium_mask, Config.FRUIT_BLOB_AREA),
        }

    def update_state(self, state: TwinState) -> None:
        """Update TwinState from a captured image, if one is available."""
        image = self.capture_image()
        if image is None:
            return

        state.colonization_percentage = self.estimate_colonization(image)
        state.pinhead_count = self.detect_pinheads(image)
        state.fruit_count = self.detect_fruits(image)
        state.contamination_level = self.estimate_contamination(image)

    def status(self):
        return {"Camera Connected": self.camera_connected}

    def validate(self) -> bool:
        # NOTE: called by IntelligentDigitalTwin.validate_system() but never
        # defined in the original framework; added here to prevent AttributeError.
        return isinstance(self.camera_connected, bool)
