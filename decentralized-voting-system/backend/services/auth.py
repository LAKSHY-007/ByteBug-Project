# backend/services/auth.py
import cv2
import face_recognition
import numpy as np
from typing import Tuple, Optional
from backend.models.voter import Voter
from backend.core.exceptions import AuthenticationError

class BiometricAuthenticator:
    def __init__(self):
        self.known_voters = {}
    
    def capture_face(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Captures face from webcam and returns encoding
        Returns: (face_image, face_encoding)
        """
        video_capture = cv2.VideoCapture(0)
        
        while True:
            ret, frame = video_capture.read()
            rgb_frame = frame[:, :, ::-1]  # BGR ko RGB m kia
            
            # Display instructions
            cv2.putText(frame, "Align face and press SPACE", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow("Face Capture", frame)
            
            # Check for key press
            key = cv2.waitKey(1)
            if key == 32:  # SPACE key
                face_locations = face_recognition.face_locations(rgb_frame)
                if face_locations:
                    face_enc = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return frame, face_enc
            
            elif key == 27:  # ESC key
                video_capture.release()
                cv2.destroyAllWindows()
                raise AuthenticationError("Face capture cancelled")
    
    def verify_unique_face(self, new_encoding: np.ndarray, tolerance: float = 0.6) -> bool:
        """
        Checks if face is already registered
        Returns True if face is unique
        """
        if not self.known_voters:
            return True
            
        matches = face_recognition.compare_faces(
            list(self.known_voters.values()),
            new_encoding,
            tolerance=tolerance
        )
        return not any(matches)
    
    def register_voter(self, name: str, voter_id: str) -> Voter:
        """
        Complete voter registration process
        """
        try:
            
            face_image, face_encoding = self.capture_face()
            
            
            if not self.verify_unique_face(face_encoding):
                raise AuthenticationError("This face is already registered")
            
            # Simulated fingerprint using
            fingerprint_hash = self._generate_fingerprint_hash(voter_id)
            
            #voter record
            voter = Voter(
                voter_id=voter_id,
                name=name,
                face_encoding=face_encoding,
                fingerprint_hash=fingerprint_hash
            )
            
            
            self.known_voters[voter_id] = face_encoding
            
            return voter
            
        except Exception as e:
            raise AuthenticationError(f"Registration failed: {str(e)}")
    
    def _generate_fingerprint_hash(self, voter_id: str) -> str:
        """Simulates fingerprint scanning"""
        import hashlib
        from datetime import datetime
        unique_str = f"{voter_id}-{datetime.now().timestamp()}"
        return hashlib.sha256(unique_str.encode()).hexdigest()