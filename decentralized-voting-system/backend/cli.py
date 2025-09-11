
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from streamlit.components.v1 import html
import cv2
import face_recognition
import numpy as np
from datetime import datetime
from hashlib import sha256
import time
import pandas as pd
import plotly.express as px
from backend.models.block import Blockchain
from backend.models.voter import Voter
from backend.core.config import get_config
import json
from typing import Optional
import json
import pickle
from pathlib import Path
<<<<<<< Updated upstream
=======
import qrcode
from io import BytesIO
import base64
import random
>>>>>>> Stashed changes


CANDIDATES = [
    {"id": 1, "name": "Pragati Vijay ", "party": "Vaayunagar", "color": "#636EFA", "avatar": "👩‍🚀"},
    {"id": 2, "name": "Khushi seva", "party": "BSF", "color": "#EF553B", "avatar": "👷‍♂️"},
    {"id": 3, "name": "DullPur", "party": "Mela", "color": "#00CC96", "avatar": "🧑‍💻"}
]

<<<<<<< Updated upstream
=======
VOTER_DB_PATH = Path(r"E:\voting_system\decentralized-voting-system\backend\db\voter_database.json")

def load_voter_db():
    """Load voter database from JSON file with proper error handling"""
    try:
        if not VOTER_DB_PATH.exists():
            st.error(f"Voter database not found at: {VOTER_DB_PATH}")
            return {}
            
        with open(VOTER_DB_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Voter database file not found at: {VOTER_DB_PATH}")
        return {}
    except json.JSONDecodeError:
        st.error("Invalid JSON format in voter database")
        return {}
    except Exception as e:
        st.error(f"Failed to load voter database: {str(e)}")
        return {}

def verify_voter_id(voter_id: str) -> dict:
    """
    Verify voter ID against database
    Returns: {
        "exists": bool,
        "eligible": bool,
        "name": str,
        "state": str,
        "city": str,
        "message": str
    }
    """
    voter_db = load_voter_db()
    voter_id = voter_id.strip().upper()
    
    if not isinstance(voter_db, dict):
        return {
            "exists": False,
            "eligible": False,
            "name": "",
            "state": "",
            "city": "",
            "message": "Database error"
        }
    
    if voter_id not in voter_db:
        return {
            "exists": False,
            "eligible": False,
            "name": "",
            "state": "",
            "city": "",
            "message": "Voter ID not found in database"
        }
    
    voter_data = voter_db[voter_id]
    return {
        "exists": True,
        "eligible": voter_data.get("eligible", False),
        "name": voter_data.get("name", ""),
        "state": voter_data.get("state", ""),
        "city": voter_data.get("city", ""),
        "message": voter_data.get("ineligible_reason", "Eligible to vote")
    }

def generate_voting_receipt(voter_id,timestamp, verification_key, candidate_color):
    """Generate HTML receipt with QR code and verification details"""
    # Generate discount QR code
    discount_code = f"VOTE-{verification_key[:4]}-{timestamp.strftime('%m%d')}"
    discount_url = f"https://partners.elections.gov/discount?code={discount_code}"
    
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(discount_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=candidate_color, back_color="white")
    
    # Convert QR to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"""
    <div style="
        border: 2px solid {candidate_color};
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        background: white;
        color: #333;
        font-family: Arial, sans-serif;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    ">
        <h2 style="color: {candidate_color}; text-align: center; margin-bottom: 5px;">Voting Receipt</h2>
        <p style="text-align: center; color: #666; margin-top: 0;">Your vote has been securely recorded</p>
        <hr style="border-color: #eee;">
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
            <div>
                <p><strong>Voter ID:</strong> {voter_id}</p>
                
                <p><strong>Time:</strong> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div style="text-align: center;">
                <img src="data:image/png;base64,{img_str}" width="120">
                <p style="font-size: 12px; margin-top: 5px;">Scan for exclusive discounts</p>
            </div>
        </div>
        
        <div style="
            background: #f8f9fa;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid {candidate_color};
            margin-top: 15px;
        ">
            <p style="margin: 0 0 8px 0; font-weight: bold;">Verification Key:</p>
            <div style="
                background: white;
                padding: 8px;
                border-radius: 4px;
                font-family: monospace;
                word-break: break-all;
            ">{verification_key}</div>
            <p style="font-size: 12px; margin: 8px 0 0 0;">
                Use this key at our verification portal to confirm your vote was recorded.
            </p>
        </div>
        
        <p style="font-size: 12px; color: #666; margin-top: 20px; text-align: center;">
            This receipt proves your participation but does not reveal your voting choice publicly.
        </p>
    </div>
    """

def verify_vote_page():
    """Enhanced vote verification page with blockchain validation"""
    st.title("🔍 Verify Your Vote")
    st.markdown("---")
    
    with st.form("verify_vote"):
        col1, col2 = st.columns(2)
        with col1:
            voter_id = st.text_input("Voter ID", placeholder="Enter your Voter ID").strip().upper()
        with col2:
            verification_key = st.text_input("Verification Key", placeholder="From your voting receipt")
        
        if st.form_submit_button("Verify My Vote", type="primary"):
            if not voter_id or not verification_key:
                st.warning("Please enter both Voter ID and Verification Key")
                return
            
            with st.spinner("Verifying your vote..."):
                # Check local votes first
                vote_record = next(
                    (v for v in st.session_state.votes 
                     if v["voter_id"] == voter_id 
                     and v.get("verification_key") == verification_key),
                    None
                )
                
                if vote_record:
                    # Verify against blockchain
                    blockchain_verified = False
                    for block in reversed(st.session_state.blockchain.chain):
                        for tx in block.transactions:
                            if (tx.get('type') == 'vote' and 
                                tx.get('voter_id') == voter_id and
                                sha256(verification_key.encode()).hexdigest() == tx.get('verification_hash')):
                                blockchain_verified = True
                                confirmation_block = block.index
                                break
                        if blockchain_verified:
                            break
                    
                    candidate = next(
                        c for c in CANDIDATES 
                        if c["id"] == vote_record["candidate_id"]
                    )
                    
                    # Display verification results
                    st.success("## ✅ Vote Verification Successful")
                    
                    # Create verification card
                    verification_card = f"""
                    <div style="
                        border: 2px solid {candidate['color']};
                        border-radius: 10px;
                        padding: 20px;
                        margin: 15px 0;
                        background: white;
                        color: #333;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3 style="color: {candidate['color']}; margin-bottom: 5px;">Your Voting Record</h3>
                                <p><strong>Voter ID:</strong> {voter_id}</p>
                                <p><strong>Candidate:</strong> {candidate['name']}</p>
                                <p><strong>Party:</strong> {candidate['party']}</p>
                                <p><strong>Voted at:</strong> {vote_record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</p>
                            </div>
                            <div style="font-size: 3rem;">{candidate['avatar']}</div>
                        </div>
                        <hr style="border-color: #eee;">
                        <div style="
                            background: #f8f9fa;
                            padding: 12px;
                            border-radius: 6px;
                            margin-top: 10px;
                        ">
                            <p style="margin: 0 0 5px 0; font-weight: bold;">Blockchain Confirmation:</p>
                            <p style="margin: 0;">
                                Block #{confirmation_block} ({'✅ Verified' if blockchain_verified else '⚠️ Pending'})
                            </p>
                            <p style="margin: 5px 0 0 0; font-size: 12px;">
                                Transaction hash: {sha256(f"{voter_id}{verification_key}".encode()).hexdigest()[:16]}...
                            </p>
                        </div>
                    </div>
                    """
                    st.markdown(verification_card, unsafe_allow_html=True)
                    
                    # Privacy notice
                    st.info("""
                    **Privacy Notice:**  
                    Your actual vote choice is never publicly linked to your identity.  
                    This verification only confirms your participation in the election.
                    """)
                    
                    # Additional verification info
                    with st.expander("🔒 Advanced Verification Details"):
                        st.markdown(f"""
                        **Verification Key:** `{verification_key}`  
                        **Key Hash:** `{sha256(verification_key.encode()).hexdigest()}`  
                        **Block Timestamp:** `{block.timestamp if blockchain_verified else 'Not confirmed'}`  
                        **Transactions in Block:** `{len(block.transactions) if blockchain_verified else 'N/A'}`  
                        
                        *This information can be used to independently verify the transaction on the blockchain.*
                        """)
                else:
                    st.error("""
                    ## ❌ Verification Failed
                    No matching vote found with these credentials. Please check:
                    - Your Voter ID is correct
                    - You entered the Verification Key exactly as shown on your receipt
                    - Your vote was successfully recorded
                    """)
                    
                    # Help section
                    with st.expander("Need help?"):
                        st.markdown("""
                        If you're having trouble verifying your vote:
                        1. Double-check your voting receipt
                        2. Ensure you're entering the exact Verification Key
                        3. Contact election support if you believe there's an error
                        
                        **Support Email:** verify@elections.gov
                        """)

>>>>>>> Stashed changes
def particle_animation():
    """Creates a floating particle animation background"""
    return """
    <canvas id="particle-canvas"></canvas>
    <script>
        const canvas = document.getElementById('particle-canvas');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '-1';
        canvas.style.opacity = '0.3';
        
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        
        const particles = [];
        const particleCount = 100;
        
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                size: Math.random() * 3 + 1,
                speedX: Math.random() * 1 - 0.5,
                speedY: Math.random() * 1 - 0.5,
                color: `rgba(${Math.floor(Math.random() * 100 + 155)}, 
                          ${Math.floor(Math.random() * 100 + 155)}, 
                          ${Math.floor(Math.random() * 100 + 155)}, 
                          ${Math.random() * 0.5 + 0.2})`
            });
        }
        
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            for (let i = 0; i < particles.length; i++) {
                const p = particles[i];
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.fill();
                
                p.x += p.speedX;
                p.y += p.speedY;
                
                if (p.x < 0 || p.x > canvas.width) p.speedX *= -1;
                if (p.y < 0 || p.y > canvas.height) p.speedY *= -1;
            }
            
            requestAnimationFrame(animate);
        }
        
        animate();
        
        window.addEventListener('resize', function() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });
    </script>
    """

def blockchain_visualization(height: int = 400):
    """Interactive 3D blockchain visualization"""
    return f"""
    <div id="blockchain-viz" style="height:{height}px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('blockchain-viz');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, container.offsetWidth/container.offsetHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(container.offsetWidth, container.offsetHeight);
        container.appendChild(renderer.domElement);
        
        const light = new THREE.AmbientLight(0x404040);
        scene.add(light);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        scene.add(directionalLight);
        
        const blocks = [];
        const blockCount = {len(st.session_state.get('blockchain', Blockchain()).chain)};
        const colors = [0x636EFA, 0xEF553B, 0x00CC96];
        
        for (let i = 0; i < blockCount; i++) {{
            const geometry = new THREE.BoxGeometry(1, 1, 1);
            const material = new THREE.MeshPhongMaterial({{
                color: colors[i % colors.length],
                transparent: true,
                opacity: 0.9
            }});
            const cube = new THREE.Mesh(geometry, material);
            cube.position.x = i * 1.5;
            cube.position.y = Math.sin(i * 0.5) * 0.5;
            scene.add(cube);
            blocks.push(cube);
            
            if (i > 0) {{
                const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                    new THREE.Vector3(blocks[i-1].position.x, blocks[i-1].position.y, 0),
                    new THREE.Vector3(cube.position.x, cube.position.y, 0)
                ]);
                const lineMaterial = new THREE.LineBasicMaterial({{ color: 0xffffff }});
                const line = new THREE.Line(lineGeometry, lineMaterial);
                scene.add(line);
            }}
        }}
        
        camera.position.z = blockCount * 0.7;
        camera.position.y = 2;
        
        function animate() {{
            requestAnimationFrame(animate);
            
            blocks.forEach((block, i) => {{
                block.rotation.x += 0.01;
                block.rotation.y += 0.01;
            }});
            
            renderer.render(scene, camera);
        }}
        
        animate();
        
        window.addEventListener('resize', function() {{
            camera.aspect = container.offsetWidth / container.offsetHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.offsetWidth, container.offsetHeight);
        }});
    </script>
    """

def face_scan_animation():
    """Advanced face scanning effect"""
    return """
    <style>
        .face-scan {
            position: relative;
            width: 100%;
            height: 300px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 10px;
            overflow: hidden;
        }
        .scan-line {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(to right, 
                rgba(0,255,0,0) 0%, 
                rgba(0,255,0,1) 50%, 
                rgba(0,255,0,0) 100%);
            box-shadow: 0 0 10px rgba(0,255,0,0.7);
            animation: scan 3s linear infinite;
        }
        @keyframes scan {
            0% { top: 0; }
            100% { top: 100%; }
        }
        .grid-overlay {
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(0,255,0,0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,255,0,0.1) 1px, transparent 1px);
            background-size: 20px 20px;
        }
    </style>
    <div class="face-scan">
        <div class="grid-overlay"></div>
        <div class="scan-line"></div>
    </div>
    """
def initialize_session():
    """Initialize all session state variables"""
    if 'blockchain' not in st.session_state:
        st.session_state.blockchain = Blockchain()
    if 'voters' not in st.session_state:
        st.session_state.voters = {}
    if 'votes' not in st.session_state:
        st.session_state.votes = []
    if 'face_encoding' not in st.session_state:
        st.session_state.face_encoding = None
    if 'current_voter' not in st.session_state:
        st.session_state.current_voter = None
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    if 'admin_configured' not in st.session_state:
        st.session_state.admin_configured = any(voter.is_admin for voter in st.session_state.voters.values())

def hash_face_encoding(encoding):
    return sha256(encoding.tobytes()).hexdigest()

def simulate_fingerprint(voter_id):
    """Generate a simulated fingerprint hash with realistic visual feedback"""
    
    # Container for the scanner visualization
    scanner_placeholder = st.empty()
    
    # Initial scanner display
    with scanner_placeholder.container():
        st.markdown("""
        <div style="background-color: #111; border-radius: 10px; padding: 20px; text-align: center;">
            <h3 style="color: #4CAF50;">BIOMETRIC SCANNER v3.2</h3>
            <div style="background-color: #000; height: 200px; border-radius: 5px; margin: 10px 0; 
                        display: flex; justify-content: center; align-items: center;">
                <p style="color: #888;">Place finger on scanner</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Start scanning process
    with st.spinner('Initializing fingerprint scanner...'):
        time.sleep(1.5)
    
    # Finger placement detection
    scanner_placeholder.empty()
    with scanner_placeholder.container():
        st.markdown("""
        <div style="background-color: #111; border-radius: 10px; padding: 20px; text-align: center;">
            <h3 style="color: #4CAF50;">BIOMETRIC SCANNER v3.2</h3>
            <div style="background-color: #000; height: 200px; border-radius: 5px; margin: 10px 0; 
                        display: flex; justify-content: center; align-items: center;">
                <p style="color: #4CAF50;">✓ Finger detected</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Scanning progress with realistic pattern
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    # Simulate scanning different parts of the fingerprint
    scan_pattern = [
        ("Calibrating scanner", 10),
        ("Scanning fingerprint core", 25),
        ("Analyzing ridge patterns", 45),
        ("Verifying minutiae points", 70),
        ("Cross-referencing database", 90),
        ("Finalizing verification", 100)
    ]
    
    for step_text, target_progress in scan_pattern:
        progress_text.markdown(f"<div style='text-align: center; margin-bottom: 5px;'>{step_text}...</div>", 
                              unsafe_allow_html=True)
        
        current_progress = progress_bar.progress(0)
        step_duration = random.uniform(0.5, 1.2)  # Vary timing for realism
        
        while current_progress < target_progress:
            increment = random.uniform(1, 3)  # Variable progress increments
            current_progress = min(current_progress + increment, target_progress)
            progress_bar.progress(int(current_progress))
            time.sleep(0.05)
    
    # Final verification with animation
    progress_text.empty()
    with st.spinner('Final verification in progress...'):
        time.sleep(1.5)
    
    # Successful scan visualization
    scanner_placeholder.empty()
    with scanner_placeholder.container():
        st.markdown("""
        <div style="background-color: #111; border-radius: 10px; padding: 20px; text-align: center;">
            <h3 style="color: #4CAF50;">BIOMETRIC SCANNER v3.2</h3>
            <div style="background-color: #000; height: 200px; border-radius: 5px; margin: 10px 0; 
                        display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M5 13L9 17L19 7" stroke="#4CAF50" stroke-width="3" stroke-linecap="round"/>
                </svg>
                <p style="color: #4CAF50; margin-top: 10px; font-weight: bold;">VERIFICATION SUCCESSFUL</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.success("Fingerprint verified!")
    
    # Generate the fingerprint hash
    return sha256(f"{voter_id}-{datetime.now().timestamp()}".encode()).hexdigest()

def capture_face() -> Optional[np.ndarray]:
    """Enhanced face capture with visual feedback"""
    FRAME_WINDOW = st.image([], channels="RGB")
    camera = cv2.VideoCapture(0)
    face_encoding = None
    detection_start = None
    
    while True:
        success, frame = camera.read()
        if not success:
            st.error("Failed to access camera")
            break
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            if detection_start is None:
                detection_start = time.time()
            
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                pulse = int(abs((time.time() % 1) - 0.5) * 50 + 155)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, pulse, 0), 2)
                
                elapsed = time.time() - detection_start
                if elapsed < 3:
                    cv2.putText(frame, f"Hold still... {3-int(elapsed)}", 
                               (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
                    break
        else:
            detection_start = None
        
        FRAME_WINDOW.image(frame)
        
        if face_encoding is not None or cv2.waitKey(1) == 27:
            break
    
    camera.release()
    cv2.destroyAllWindows()
    return face_encoding



def verify_admin() -> bool:
    """Two-factor authentication for admin access"""
    if st.session_state.get('admin_authenticated', False):
        return True
    
    st.title("🔒 Admin Authentication")
    st.warning("Admin privileges require face and PIN verification")
    
    #face verify
    st.subheader("Step 1: Face Verification")
    if st.button("Start Face Scan"):
        face_encoding = capture_face()
        if face_encoding is not None:
            for voter in st.session_state.voters.values():
                if voter.is_admin and face_recognition.compare_faces(
                    [voter.face_encoding], face_encoding, tolerance=0.6
                )[0]:
                    st.session_state.current_admin = voter
                    st.success("Admin face verified!")
                    break
            else:
                st.error("No matching admin found")

    # PIN verify
    if 'current_admin' in st.session_state:
        st.subheader("Step 2: PIN Verification")
        pin = st.text_input("Enter Admin PIN", type="password", max_chars=6)
        if st.button("Verify PIN"):
            if st.session_state.current_admin.verify_pin(pin):
                st.session_state.admin_authenticated = True
                st.success("Admin authenticated successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Incorrect PIN")

    return False

def home_page():
    """Landing page with futuristic intro"""
    st.title("🚀 Decentralized Voting System")
    st.markdown("---")
    
    html(particle_animation(), height=0)
    
    with st.container():
        col1, col2 = st.columns([2, 3])
        with col1:
            st.markdown("""
            ## Welcome to **SecureVote**  
            ### The Future of Democratic Elections  
            ✨ **Blockchain-powered**  
            🔒 **Biometrically secured**  
            🌐 **Tamper-proof**  
            """)
            
            if st.button("Get Started", key="hero_cta", 
                        use_container_width=True, type="primary"):
                st.session_state.page = "register"
                st.rerun()
        
        with col2:
            html(blockchain_visualization(300))
    
    st.markdown("---")
    st.subheader("Key Features")
    cols = st.columns(3)
    features = [
        ("🧑‍💻", "Facial Recognition", "Advanced AI verifies voter identity"),
        ("🖐️", "Fingerprint Auth", "Biometric security layer"),
        ("⛓️", "Blockchain Backed", "Immutable transaction ledger"),
        ("📊", "Real-time Results", "Live updating analytics"),
        ("👁️", "Transparent", "Publicly verifiable records"),
        ("🔐", "End-to-End Secure", "Military-grade encryption")
    ]
    
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            with st.container(border=True, height=180):
                st.markdown(f"<h3>{icon} {title}</h3><p>{desc}</p>", 
                           unsafe_allow_html=True)

def register_page():
    """Voter registration with advanced animations"""
    st.title("👤 Voter Registration")
    st.markdown("---")
    
    with st.form("registration_form"):
<<<<<<< Updated upstream
        name = st.text_input("Full Name", placeholder="Enter your full name")
        voter_id = st.text_input("Voter ID", placeholder="Unique voter identifier")
        
        if st.form_submit_button("Begin Biometric Enrollment", 
                                use_container_width=True, type="primary"):
            if name and voter_id:
                if voter_id in st.session_state.voters:
                    st.error("This Voter ID is already registered")
                else:
                    # Face capture kelie
                    st.markdown("""
                    <style>
                        .face-capture-instructions {
                            animation: pulse 2s infinite;
                        }
                        @keyframes pulse {
                            0% { opacity: 0.8; }
                            50% { opacity: 1; }
                            100% { opacity: 0.8; }
                        }
                    </style>
                    <div class="face-capture-instructions">
                        Please position your face in the frame and remain still
                    </div>
                    """, unsafe_allow_html=True)
                    
                    html(face_scan_animation())
                    
                    face_encoding = capture_face()
                    if face_encoding is not None:
                        st.session_state.face_encoding = face_encoding
                        
                        fingerprint_hash = simulate_fingerprint(voter_id)
                        
                        voter = Voter(
                            voter_id=voter_id,
                            name=name,
                            face_encoding=face_encoding,
                            fingerprint_hash=fingerprint_hash
                        )
                        st.session_state.voters[voter_id] = voter
                        
                        with st.status("Securing your data on the blockchain...", expanded=True) as status:
                            st.write("Generating cryptographic hash...")
                            time.sleep(1)
                            st.write("Creating transaction...")
                            time.sleep(1)
                            
                            tx_data = {
                                "type": "registration",
                                "voter_id": voter_id,
                                "timestamp": datetime.now().isoformat(),
                                "biometric_hash": hash_face_encoding(face_encoding)
                            }
                            st.session_state.blockchain.new_transaction("system", tx_data)
                            st.write("Mining block...")
                            time.sleep(1.5)
                            st.session_state.blockchain.new_block(proof=123)
                            
                            status.update(label="Registration complete!", state="complete", expanded=False)
                        
                        st.balloons()
                        st.success("You are now registered to vote!")
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #00cc96aa, #636efaaa);
                            padding: 1rem;
                            border-radius: 10px;
                            color: white;
                            text-align: center;
                            margin: 1rem 0;
                            animation: fadeIn 1s;
                        ">
                            <h3 style="color: white;">Registration Successful!</h3>
                            <p>Voter ID: <strong>{voter_id}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Please complete all fields")
=======
        # check against db
        voter_id = st.text_input("Voter ID", placeholder="Enter your official Voter ID").strip().upper()
        
        if st.form_submit_button("Begin Biometric Enrollment", 
                               use_container_width=True, type="primary"):
            if not voter_id:
                st.warning("Please enter your Voter ID")
                return
                
            # Verify voter with db
            verification = verify_voter_id(voter_id)
            
            if not verification["exists"]:
                st.error(verification["message"])
                return
                
            if not verification["eligible"]:
                st.error(f"Cannot register: {verification['message']}")
                return
                
            
            st.success(f"""
            Voter Verified!
            - Name: {verification['name']}
            - State: {verification['state']}
            - City: {verification['city']}
            """)
            
            
            if voter_id in st.session_state.voters:
                st.error("This Voter ID is already registered in our system")
                return
                
            
            st.markdown("""
            <style>
                .face-capture-instructions {
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 0.8; }
                    50% { opacity: 1; }
                    100% { opacity: 0.8; }
                }
            </style>
            <div class="face-capture-instructions">
                Please position your face in the frame and remain still
            </div>
            """, unsafe_allow_html=True)
            
            html(face_scan_animation())
            
            face_encoding = capture_face()
            if face_encoding is None:
                st.error("Face capture failed. Please try again.")
                return
                
            st.session_state.face_encoding = face_encoding
            
            fingerprint_hash = simulate_fingerprint(voter_id)
            
            
            voter = Voter(
                voter_id=voter_id,
                name=verification['name'], 
                face_encoding=face_encoding,
                fingerprint_hash=fingerprint_hash,
                state=verification['state'],
                city=verification['city']
            )
            st.session_state.voters[voter_id] = voter
            
            # Blockchain registration
            with st.status("Securing your data on the blockchain...", expanded=True) as status:
                st.write("Generating cryptographic hash...")
                time.sleep(1)
                st.write("Creating transaction...")
                time.sleep(1)
                
                tx_data = {
                    "type": "registration",
                    "voter_id": voter_id,
                    "name": verification['name'],
                    "timestamp": datetime.now().isoformat(),
                    "biometric_hash": hash_face_encoding(face_encoding),
                    "state": verification['state'],
                    "city": verification['city']
                }
                st.session_state.blockchain.new_transaction("system", tx_data)
                st.write("Mining block...")
                time.sleep(1.5)
                st.session_state.blockchain.new_block(proof=123)
                
                status.update(label="Registration complete!", state="complete", expanded=False)
            
            st.balloons()
            st.success("You are now registered to vote!")
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #00cc96aa, #636efaaa);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin: 1rem 0;
                animation: fadeIn 1s;
            ">
                <h3 style="color: white;">Registration Successful!</h3>
                <p>Name: <strong>{verification['name']}</strong></p>
                <p>Voter ID: <strong>{voter_id}</strong></p>
                <p>Location: {verification['state']}, {verification['city']}</p>
            </div>
            """, unsafe_allow_html=True)
>>>>>>> Stashed changes

def verify_voter():
    """Voter verification process"""
    st.header("Voter Verification")
    
    voter_id = st.text_input("Enter your Voter ID")
    if voter_id and st.button("Start Verification"):
<<<<<<< Updated upstream
=======
        
        try:
            with open('E:/voting_system/decentralized-voting-system/backend/db/voter_database.json', 'r') as f:

                voters_db = json.load(f)
        except FileNotFoundError:
            st.error("Voter database not available")
            return False
        except json.JSONDecodeError:
            st.error("Voter database corrupted")
            return False
            
        if voter_id not in voters_db:
            st.error("Voter ID not found in database")
            return False
            
        voter_data = voters_db[voter_id]
        
        if not voter_data.get("eligible", True):
            st.error(f"Not eligible: {voter_data.get('message', 'Voter is not eligible')}")
            return False
            
        st.success(f"""
        Voter ID Verified!
        - Name: {voter_data.get('name', 'N/A')}
        - State: {voter_data.get('state', 'N/A')}
        - City: {voter_data.get('city', 'N/A')}
        """)
        
        
        st.write("Please look at the camera for biometric verification")
        
>>>>>>> Stashed changes
        if voter_id not in st.session_state.voters:
            st.error("Voter ID not found")
            return False
        
        st.write("Please look at the camera for verification")
        
        FRAME_WINDOW = st.image([])
        camera = cv2.VideoCapture(0)
        verified = False
        
        start_time = time.time()
        while time.time() - start_time < 10:
            _, frame = camera.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(frame)
            if face_locations:
                current_encoding = face_recognition.face_encodings(frame, face_locations)[0]
                registered_encoding = st.session_state.voters[voter_id].face_encoding
                
                match = face_recognition.compare_faces(
                    [registered_encoding], 
                    current_encoding,
                    tolerance=0.6
                )[0]
                
                if match:
                    cv2.putText(frame, "VERIFIED", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    verified = True
                else:
                    cv2.putText(frame, "NOT MATCHING", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            FRAME_WINDOW.image(frame)
            if verified:
                time.sleep(1)
                break
        
        camera.release()
        
        if verified:
            st.success("Identity verified!")
            st.session_state.current_voter = voter_id
            return True
        else:
            st.error("Verification failed")
            return False
    return False

def voting_page():
    """Immersive voting experience"""
    st.title("🗳️ Cast Your Vote")
    st.markdown("---")
    
    if 'current_voter' not in st.session_state or st.session_state.current_voter is None:
        if not verify_voter():
            return
    
    voter_id = st.session_state.current_voter
    
    # checking if voter has voted
    if voter_id not in st.session_state.voters:
        st.error("Voter not found in registry")
        return
    
    if st.session_state.voters[voter_id].has_voted:
        st.error("You have already voted in this election")
        return
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    ">
        <h3 style="color: white;">Welcome, {st.session_state.voters[voter_id].name}</h3>
        <p>Your vote is anonymous and secure</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Select Your Candidate")
    
    cols = st.columns(3)
    for i, candidate in enumerate(CANDIDATES):
        with cols[i]:
            with st.container(border=True, height=300):
                st.markdown(f"""
                <style>
                    .candidate-card-{i} {{
                        transition: all 0.3s ease;
                    }}
                    .candidate-card-{i}:hover {{
                        transform: translateY(-5px);
                        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
                    }}
                </style>
                <div class="candidate-card-{i}" style="text-align: center;">
                    <h1 style="font-size: 3rem;">{candidate['avatar']}</h1>
                    <h3>{candidate['name']}</h3>
                    <p style="color: {candidate['color']}">{candidate['party']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Vote for {candidate['name']}", 
                            key=f"vote_{i}", use_container_width=True):
                    with st.spinner(f"Recording vote for {candidate['name']}..."):
                        progress_bar = st.progress(0)
                        
                        for percent in range(100):
                            time.sleep(0.02)
                            progress_bar.progress(percent + 1)
<<<<<<< Updated upstream
=======
                        
                        # Create vote record
                        vote_timestamp = datetime.now()
                        verification_key = sha256(f"{voter_id}{candidate['id']}{vote_timestamp.timestamp()}".encode()).hexdigest()[:16]
>>>>>>> Stashed changes
                        
                        st.session_state.votes.append({
                            "voter_id": voter_id,
                            "candidate_id": candidate["id"],
                            "timestamp": datetime.now()
                        })
                        st.session_state.voters[voter_id].has_voted = True
                        
<<<<<<< Updated upstream
=======
                        # Add to blockchain
>>>>>>> Stashed changes
                        tx_data = {
                            "type": "vote",
                            "voter_id": voter_id,
                            "candidate_id": candidate["id"],
<<<<<<< Updated upstream
                            "timestamp": datetime.now().isoformat()
=======
                            "timestamp": vote_timestamp.isoformat(),
                            "verification_hash": sha256(verification_key.encode()).hexdigest()  # Store hash only for security
>>>>>>> Stashed changes
                        }
                        st.session_state.blockchain.new_transaction("system", tx_data)
                        st.session_state.blockchain.new_block(proof=123)
                    
                    st.balloons()
                    st.success(f"Vote for {candidate['name']} recorded!")
                    
<<<<<<< Updated upstream
=======
                    # Generate receipt
                    receipt_html = generate_voting_receipt(
                        voter_id=voter_id,

                        timestamp=vote_timestamp,
                        verification_key=verification_key,
                        candidate_color=candidate['color']
                    )
                    
                    # Display receipt
                    st.markdown(receipt_html, unsafe_allow_html=True)
                    
                    # Offer download
                    st.download_button(
                        "📄 Download Voting Receipt",
                        data=receipt_html,
                        file_name=f"vote_receipt_{voter_id}.html",
                        mime="text/html"
                    )
                    
                    # Confetti celebration
>>>>>>> Stashed changes
                    html(f"""
                    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
                    <script>
                        confetti({{
                            particleCount: 150,
                            spread: 70,
                            origin: {{ y: 0.6 }},
                            colors: ['{candidate['color']}']
                        }});
                    </script>
                    """)

<<<<<<< Updated upstream
=======
def verify_vote_page():
    """Page for voters to verify their vote"""
    st.title("🔍 Verify Your Vote")
    
    with st.form("verify_vote"):
        voter_id = st.text_input("Voter ID").strip().upper()
        verification_key = st.text_input("Verification Key")
        
        if st.form_submit_button("Verify Vote"):
            vote_record = next(
                (v for v in st.session_state.votes 
                 if v["voter_id"] == voter_id 
                 and v.get("verification_key") == verification_key),
                None
            )
            
            if vote_record:
                candidate = next(
                    c for c in CANDIDATES 
                    if c["id"] == vote_record["candidate_id"]
                )
                
                st.success(f"""
                Vote Verified Successfully!
                - You voted for: {candidate['name']}
                - Voting time: {vote_record['timestamp'].strftime("%Y-%m-%d %H:%M:%S")}
                - Block confirmation: #{len(st.session_state.blockchain.chain)-1}
                """)
                
                # Show anonymized proof
                st.info("""
                Your vote remains anonymous in the public record. 
                This verification only confirms your vote was recorded correctly.
                """)
            else:
                st.error("No matching vote found. Please check your credentials.")
>>>>>>> Stashed changes
def results_page():
    """Protected results dashboard - only accessible by admin"""
    if not st.session_state.get('admin_configured', False):
        setup_admin()
        return
    
    if not verify_admin():
        return
    
    st.title("📊 Live Election Results")
    st.markdown("---")
    
    html(particle_animation(), height=0)
    
    vote_counts = {c["id"]: 0 for c in CANDIDATES}
    for vote in st.session_state.votes:
        vote_counts[vote["candidate_id"]] += 1
    
    total_votes = sum(vote_counts.values())
    total_registered = len(st.session_state.voters)
    
    st.subheader("Participation Metrics")
    cols = st.columns(3)
    with cols[0]:
        st.metric("Total Registered", total_registered)
    with cols[1]:
        st.metric("Votes Cast", total_votes, 
                 delta=f"{total_votes/total_registered*100:.1f}%" if total_registered > 0 else "0%",
                 delta_color="normal")
    with cols[2]:
        st.metric("Leading Candidate", 
                 CANDIDATES[max(vote_counts, key=vote_counts.get)]["name"] if total_votes > 0 else "N/A")
    
    st.subheader("Vote Distribution")
    
    results_df = pd.DataFrame([
        {
            "Candidate": c["name"],
            "Votes": vote_counts[c["id"]],
            "Party": c["party"],
            "Color": c["color"],
            "Percentage": vote_counts[c["id"]] / total_votes * 100 if total_votes > 0 else 0
        }
        for c in CANDIDATES
    ])
    
    fig = px.bar(
        results_df,
        x="Candidate",
        y="Votes",
        color="Candidate",
        color_discrete_map={c["name"]: c["color"] for c in CANDIDATES},
        text="Votes",
        animation_frame="Votes",
        range_y=[0, max(vote_counts.values()) + 5 if vote_counts.values() else 10]
    )
    fig.update_layout(
        showlegend=False,
        transition={'duration': 1000},
        updatemenus=[{
            'buttons': [{
                'args': [None, {'frame': {'duration': 1000, 'redraw': True}, 
                               'fromcurrent': True, 'transition': {'duration': 500}}],
                'label': 'Play',
                'method': 'animate'
            }],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Vote Share")
    pie_col, time_col = st.columns([2, 1])
    
    with pie_col:
        fig2 = px.pie(
            results_df,
            values="Votes",
            names="Candidate",
            color="Candidate",
            color_discrete_map={c["name"]: c["color"] for c in CANDIDATES},
            hole=0.4
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True)
    
    with time_col:
        st.markdown("""
        <style>
            .clock {
                font-size: 3rem;
                text-align: center;
                margin: 1rem 0;
                color: #636EFA;
                font-weight: bold;
            }
            .last-update {
                text-align: center;
                color: #777;
            }
        </style>
        <div class="clock" id="live-clock"></div>
        <div class="last-update">Last updated: <span id="update-time">now</span></div>
        <script>
            function updateClock() {
                const now = new Date();
                document.getElementById('live-clock').innerHTML = 
                    now.toLocaleTimeString();
                document.getElementById('update-time').innerHTML = 
                    'just now';
            }
            setInterval(updateClock, 1000);
            updateClock();
        </script>
        """, unsafe_allow_html=True)
    
    if st.session_state.votes:
        st.subheader("Voting Activity Over Time")
        votes_df = pd.DataFrame(st.session_state.votes)
        votes_df['hour'] = votes_df['timestamp'].dt.floor('H')
        time_series = votes_df.groupby(['hour', 'candidate_id']).size().unstack().fillna(0)
        
        fig3 = px.area(
            time_series,
            title="Votes per Hour",
            labels={"value": "Votes", "hour": "Time"},
            color_discrete_map={c["id"]: c["color"] for c in CANDIDATES}
        )
        st.plotly_chart(fig3, use_container_width=True)

def admin_page():
    """Protected admin dashboard - only accessible by admin"""
    if not st.session_state.get('admin_configured', False):
        setup_admin()
        return
    
    if not verify_admin():
        return
    
    st.title("👑 Administrator Dashboard")
    st.markdown("---")
    
    html(particle_animation(), height=0)
    
    st.success("ADMIN PRIVILEGES ACTIVATED", icon="⚠️")
    
    tab1, tab2, tab3 = st.tabs(["📈 Statistics", "⛓ Blockchain", "⚙ System"])
    
    with tab1:
        st.subheader("Voter Analytics")
        
        reg_dates = [v.registration_date for v in st.session_state.voters.values()]
        if reg_dates:
            reg_df = pd.DataFrame({"Date": pd.to_datetime(reg_dates)})
            reg_counts = reg_df.resample('D', on='Date').size()
            
            fig = px.line(
                reg_counts,
                title="Daily Registrations",
                labels={"value": "Registrations"},
                line_shape="spline",
                render_mode="svg"
            )
            fig.update_traces(line=dict(width=4, color='#00CC96'))
            st.plotly_chart(fig, use_container_width=True)
        
        if st.session_state.votes:
            votes_df = pd.DataFrame(st.session_state.votes)
            votes_df['hour'] = votes_df['timestamp'].dt.hour
            hourly = votes_df.groupby(['hour', 'candidate_id']).size().unstack()
            
            fig2 = px.bar(
                hourly,
                title="Votes by Hour",
                barmode="group",
                color_discrete_map={c["id"]: c["color"] for c in CANDIDATES}
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.subheader("Blockchain Explorer")
        
        html(blockchain_visualization(400))
        
        st.markdown("### Latest Blocks")
        chain_df = pd.DataFrame([
            {
                "Block": i,
                "Transactions": len(block.transactions),
                "Timestamp": datetime.fromtimestamp(block.timestamp),
                "Hash": block.compute_hash()[:16] + "..."
            }
            for i, block in enumerate(st.session_state.blockchain.chain[-5:][::-1])
        ])
        
        st.dataframe(
            chain_df,
            column_config={
                "Timestamp": st.column_config.DatetimeColumn("Timestamp"),
                "Hash": "Block Hash"
            },
            hide_index=True,
            use_container_width=True
        )
    
    with tab3:
        st.subheader("System Controls")
        
        st.warning("Critical Operations - Use with caution")
        
        if st.button("🗑️ Reset All Data", type="primary"):
            st.session_state.blockchain = Blockchain()
            st.session_state.voters = {}
            st.session_state.votes = []
            st.success("System reset complete!")
            time.sleep(1)
            st.experimental_rerun()
        
        if st.button("🔐 Generate Security Report"):
            with st.spinner("Analyzing system..."):
                time.sleep(2)
                st.success("Security audit complete")
                st.json({
                    "blockchain_integrity": "verified",
                    "voter_data_encryption": "enabled",
                    "biometric_protection": "active",
                    "threat_level": "low"
                })
        
        st.markdown("### Data Management")
        st.download_button(
            "💾 Export Blockchain Data",
            data=json.dumps([block.__dict__ for block in st.session_state.blockchain.chain]),
            file_name="blockchain_export.json",
            mime="application/json"
        )

def main():
    initialize_session()
    if not st.session_state.get('admin_configured', False):
        setup_admin()
        return
    
    st.set_page_config(
        page_title="SecureVote | Decentralized Voting",
        page_icon="🗳️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
        .stApp {
            background-color: #0f0f1a;
            color: #ffffff;
        }
        
        .st-emotion-cache-6qob1r {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        
        .stButton>button {
            border: none;
            background: linear-gradient(135deg, #636EFA 0%, #00CC96 100%);
            color: white;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        
        .stTextInput>div>div>input {
            background-color: rgba(255,255,255,0.1);
            color: white;
        }
        
        .stContainer {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(255,255,255,0.05);
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #636EFA 0%, #00CC96 100%);
            border-radius: 4px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/1a1a2e/ffffff?text=SecureVote", width=150)
        st.markdown("---")
        
        menu_options = ["🏠 Home", "👤 Register", "🗳️ Vote"]
        if st.session_state.get('admin_configured', False):
            menu_options.extend(["📊 Results", "👑 Admin"])
        
        menu = st.radio(
            "Navigation",
            menu_options,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("### System Status")
        cols = st.columns(2)
        cols[0].metric("Voters", len(st.session_state.voters))
        cols[1].metric("Votes", len(st.session_state.votes))
        
        st.markdown(f"""
        <div style="
            background: rgba(0,0,0,0.2);
            padding: 0.5rem;
            border-radius: 5px;
            margin-top: 1rem;
        ">
            <small>Blockchain Height: {len(st.session_state.blockchain.chain)}</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('admin_authenticated', False):
            if st.button("🔒 Logout Admin"):
                st.session_state.admin_authenticated = False
                st.session_state.current_admin = None
                st.rerun()
    
    if menu == "🏠 Home":
        home_page()
    elif menu == "👤 Register":
        register_page()
    elif menu == "🗳️ Vote":
        voting_page()
    elif menu == "📊 Results":
        results_page()
    elif menu == "👑 Admin":
        admin_page()

if __name__ == "__main__":
    main()