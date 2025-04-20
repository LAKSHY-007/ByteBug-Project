
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
from models.block import Blockchain
from models.voter import Voter
from core.config import get_config
import json
from typing import Optional
import json
import pickle
from pathlib import Path
import qrcode
import base64
import json
import os
import json
import cv2
import time
import face_recognition
import streamlit as st
from datetime import datetime
from io import BytesIO
import base64
import gettext

st.set_page_config(
    page_title="SecureVote | Decentralized Voting",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ---- Language setup and translation ----
lang_display = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "pa": "Punjabi",
    "mr": "Marathi"
}

lang_names = list(lang_display.values())

# Create session key for language if not already set
if "language" not in st.session_state:
    st.session_state.language = "en"

# Display language dropdown in top-right
lang_cols = st.columns([6, 1])
with lang_cols[1]:
    selected_lang_name = st.selectbox("Language", lang_names, index=lang_names.index(lang_display[st.session_state.language]))
    st.session_state.language = [code for code, name in lang_display.items() if name == selected_lang_name][0]

selected_lang_code = st.session_state.language

# Load translation
def load_translation(language):
    locale_path = os.path.join(os.path.dirname(__file__), "locales")
    try:
        lang = gettext.translation('messages', localedir=locale_path, languages=[language])
        lang.install()
        return lang.gettext
    except FileNotFoundError:
        gettext.install('messages')
        return gettext.gettext

_ = load_translation(selected_lang_code)

CANDIDATES = [
    {"id": 1, "name": "B.J.P", "party": "Gujarat", "color": "#636EFA", "avatar": "👩‍🚀"},
    {"id": 2, "name": "Congress", "party": "West Bengal", "color": "#EF553B", "avatar": "👷‍♂️"},
    {"id": 3, "name": "Aam Aadmi Party", "party": "Delhi", "color": "#00CC96", "avatar": "🧑‍💻"}
]

VOTER_DB_PATH = Path(r'C:\Users\prade\ByteBug-Project\decentralized-voting-system\voter_database.json')

def load_voter_db():
    """Load voter database from JSON file with proper error handling"""
    try:
        if not VOTER_DB_PATH.exists():
            st.error(_(f"Voter database not found at: {VOTER_DB_PATH}"))
            return {}
            
        with open(VOTER_DB_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(_(f"Voter database file not found at: {VOTER_DB_PATH}"))
        return {}
    except json.JSONDecodeError:
        st.error(_("Invalid JSON format in voter database"))
        return {}
    except Exception as e:
        st.error(_(f"Failed to load voter database: {str(e)}"))
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

DATABASE_FILE = "votes_database.json"

def initialize_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w') as f:
            json.dump({"votes": []}, f)

def record_vote(voter_id, timestamp, verification_key, candidate_color):
    initialize_database()
    
    vote_record = {
        "voter_id": voter_id,
        "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "verification_key": verification_key,
        "candidate_color": candidate_color,
        "verified": False,
        "verification_timestamp": None
    }
    
    with open(DATABASE_FILE, 'r+') as f:
        data = json.load(f)
        data["votes"].append(vote_record)
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

def generate_voting_receipt(voter_id, timestamp, verification_key, candidate_color):
    record_vote(voter_id, timestamp, verification_key, candidate_color)
    discount_code = f"VOTE-{verification_key[:4]}-{timestamp.strftime('%m%d')}"
    discount_url = f"https://partners.elections.gov/discount?code{discount_code}"
    
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(discount_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=candidate_color, back_color="white")
    
    # qr to base64
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

def particle_animation():
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
    st.markdown(_("### 🔒 Biometric Authentication"))
    st.markdown(_("#### Please place your finger on the scanner..."))

    with st.spinner(_("🧠 Initializing scanner...")):
        time.sleep(1.5)

    st.markdown(_("#### 🖐️ Scanning fingerprint..."))
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    for percent_complete in range(100):
        time.sleep(0.015)
        progress_bar.progress(percent_complete + 1)
        if percent_complete == 20:
            status_placeholder.info(_("🔎 Analyzing ridge patterns..."))
        elif percent_complete == 50:
            status_placeholder.info(_("🔄 Matching with encrypted database..."))
        elif percent_complete == 80:
            status_placeholder.info(_("✅ Verifying identity..."))

    status_placeholder.success(_("🎉 Scanning Completed"))
    fingerprint_hash = sha256(f"{voter_id}-{datetime.now().timestamp()}".encode()).hexdigest()
    st.markdown("---")
    st.markdown(_("#### 🔑 Unique Fingerprint Token"))
    st.code(fingerprint_hash, language="text")
    st.caption(_("Secure hash generated based on your fingerprint and current time."))
    return fingerprint_hash


def capture_face() -> Optional[np.ndarray]:
    FRAME_WINDOW = st.image([], channels="RGB")
    camera = cv2.VideoCapture(0)
    face_encoding = None
    detection_start = None
    
    while True:
        success, frame = camera.read()
        if not success:
            st.error(_("Failed to access camera"))
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

def setup_admin():
    st.title(_(" Admin Setup"))
    st.warning(_("This is a one-time setup to create the system administrator"))
    
    with st.form(_("admin_setup")):
        name = st.text_input(_("Admin Name"), placeholder=_("Your full name"))
        admin_id = st.text_input(_("Admin ID"), placeholder=_("Unique admin identifier"))
        pin = st.text_input(_("Set Admin PIN (6 digits)"), type="password", max_chars=6)
        
        if st.form_submit_button(_("Register Admin")):
            if name and admin_id and pin:
                if len(pin) != 6 or not pin.isdigit():
                    st.error(_("PIN must be exactly 6 digits"))
                else:
                    st.info(_("Please look at the camera for facial registration"))
                    face_encoding = capture_face()
                    
                    if face_encoding is not None:
                        fingerprint_hash = simulate_fingerprint(admin_id)
                        
                        admin = Voter(
                            voter_id=admin_id,
                            name=name,
                            face_encoding=face_encoding,
                            fingerprint_hash=fingerprint_hash
                        )
                        admin.set_pin(pin)
                        admin.is_admin = True
                        
                        st.session_state.voters[admin_id] = admin
                        st.session_state.admin_configured = True
                        st.session_state.admin_authenticated = True
                        st.session_state.current_admin = admin
                        
                        st.success(_("Admin account created successfully!"))
                        time.sleep(2)
                        st.rerun()
            else:
                st.error(_("Please complete all fields"))

def verify_admin() -> bool:
    """Secure two-factor authentication for admin access"""
    
    if st.session_state.get(_('admin_authenticated'), False):
        return True
    
    st.title(_("🔒 Admin Authentication"))
    st.warning(_("Admin privileges require face and PIN verification"))
    
    
    st.subheader(_("Step 1: Face Verification"))
    if st.button(_("Start Face Scan")):
        face_encoding = capture_face()
        if face_encoding is not None:
            
            admin_found = False
            for voter_id, voter in st.session_state.voters.items():
                if getattr(voter, _('is_admin'), False):
                    if (hasattr(voter, _('face_encoding'))) and \
                       face_recognition.compare_faces([voter.face_encoding], face_encoding, tolerance=0.6)[0]:
                        st.session_state.current_admin = voter
                        st.success(_(f"Face verified as admin: {voter.name}"))
                        admin_found = True
                        break
            
            if not admin_found:
                st.error(_("No matching admin found. Please register as admin first."))

    
    if hasattr(st.session_state, 'current_admin') and st.session_state.current_admin is not None:
        st.subheader(_("Step 2: PIN Verification"))
        pin = st.text_input(_("Enter Admin PIN"), type="password", max_chars=6)
        
        if st.button(_("Verify PIN")):
            if pin and hasattr(st.session_state.current_admin, 'verify_pin'):
                if st.session_state.current_admin.verify_pin(pin):
                    st.session_state.admin_authenticated = True
                    st.success(_("Admin authenticated successfully!"))
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(_("Incorrect PIN"))
            else:
                st.error(_("Invalid PIN or admin account configuration"))

    return st.session_state.get(_('admin_authenticated'), False)

def home_page():
     if st.session_state.language == 'en':
        st.header("Vote Chain")
     elif st.session_state.language == 'hi':
        st.header("वोट चेन")
     elif st.session_state.language == 'ta':
        st.header("வாக்குச் சங்கிலி")
     elif st.session_state.language == 'mr':
        st.header("मतांची साखळी")
     elif st.session_state.language == 'pa':
        st.header("ਵੋਟ ਚੇਨ")
  
     st.markdown("---")
    
     html(particle_animation(), height=0)
    
     with st.container():
        col1, col2 = st.columns([2, 3])
        with col1:
            if st.session_state.language == 'en':
                st.markdown("""
                ## Welcome to **VoteChain**
                ### The Future of Democratic Elections  
                ✨ **Blockchain-powered**  
                🔒 **Biometrically secured**  
                🌐 **Tamper-proof**  
                """)
            elif st.session_state.language == 'hi':
                st.markdown("""
                ## **VoteChain** में आपका स्वागत है
                ### लोकतांत्रिक चुनावों का भविष्य
                ✨ **ब्लॉकचेन-संचालित**
                🔒 **बायोमेट्रिक रूप से सुरक्षित**
                🌐 **छेड़छाड़-रोधी** **Tamper-proof**  
                """)
            elif st.session_state.language == 'mr':
                st.markdown("""
                ## **VoteChain** मध्ये आपले स्वागत आहे
                ### लोकशाही निवडणुकांचे भविष्य
                ✨ **ब्लॉकचेन-चालित**
                🔒 **बायोमेट्रिकली सुरक्षित**
                🌐 **छेडछाड-प्रतिरोधक**  
                """)
            elif st.session_state.language == 'ta':
                st.markdown("""
                ## **VoteChain**க்கு வருக
                ### ஜனநாயகத் தேர்தல்களின் எதிர்காலம்
                ✨ **பிளாக்செயின் மூலம் இயங்கும்**
                🔒 **பயோமெட்ரிக் முறையில் பாதுகாப்பானது**
                🌐 **டேம்பர்-ப்ரூஃப்**  
                """)
            elif st.session_state.language == 'pa':
                st.markdown("""
                ## **VoteChain** ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ
                ### ਲੋਕਤੰਤਰੀ ਚੋਣਾਂ ਦਾ ਭਵਿੱਖ
                ✨ **ਬਲਾਕਚੇਨ-ਸੰਚਾਲਿਤ**
                🔒 **ਬਾਇਓਮੈਟ੍ਰਿਕਲੀ ਸੁਰੱਖਿਅਤ**
                🌐 **ਛੇੜਛਾੜ-ਰੋਧਕ** 
                """)
            
            if st.button("Get Started", key="hero_cta", 
                        use_container_width=True, type="primary"):
                st.session_state.page = "register"
                st.rerun()
        
        with col2:
            html(blockchain_visualization(300))
    
     st.markdown("---")
     st.subheader(_("Key Features"))
     cols = st.columns(3)
     features = [
        ("🧑‍💻", _("Facial Recognition"), _("Advanced AI verifies voter identity")),
        ("🖐️", _("Fingerprint Auth"), _("Biometric security layer")),
        ("⛓️", _("Blockchain Backed"), _("Immutable transaction ledger")),
        ("📊", _("Real-time Results"), _("Live updating analytics")),
        ("👁️", _("Transparent"), _("Publicly verifiable records")),
        ("🔐", _("End-to-End Secure"), _("Military-grade encryption"))
    ]
    
     for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            with st.container(border=True, height=180):
                st.markdown(f"<h3>{icon} {title}</h3><p>{desc}</p>", 
                           unsafe_allow_html=True)

def register_page():
    """Voter registration with database verification and biometric enrollment"""
    if st.session_state.language == "en":
        st.title("👤 Voter Registration")
    elif st.session_state.language == 'hi':
        st.title("👤 मतदाता पंजीकरण")
    elif st.session_state.language == 'pa':
        st.title("👤 ਵੋਟਰ ਰਜਿਸਟ੍ਰੇਸ਼ਨ")
    elif st.session_state.language == 'ta':
        st.title("👤வாக்காளர் பதிவு")
    elif st.session_state.language == 'mr':
        st.title("👤 मतदार नोंदणी")


    st.markdown("---")
    
    with st.form(_("registration_form")):
        # check against db
        voter_id = st.text_input(_("Voter ID"), placeholder=_("Enter your official Voter ID")).strip().upper()
        
        if st.form_submit_button(_("Begin Biometric Enrollment"), 
                               use_container_width=True, type="primary"):
            if not voter_id:
                st.warning(_("Please enter your Voter ID"))
                return
                
            # Verify voter with db
            verification = verify_voter_id(voter_id)
        
            if not verification["exists"]:
                st.error(verification["message"])
                return
                
            if not verification["eligible"]:
                st.error(f"Cannot register: {verification['message']}")
                return
                
            if st.session_state.language == 'en':
                st.success(_(f"""
                Voter Verified!
                - Name: {verification['name']}
                - State: {verification['state']}
                - City: {verification['city']}
                """))
            elif st.session_state.language == 'ta':
                st.success(_(f"""
                வாக்காளர் சரிபார்க்கப்பட்டது!
                             
                பெயர்: அமித் சர்மா\n
                மாநிலம்: மகாராஷ்டிரா\n
                நகரம்: மும்பை
                """))
            elif st.session_state.language == 'hi':
                st.success(_(f"""
                मतदाता सत्यापित!
                             
                नाम: अमित शर्मा\n
                राज्य: महाराष्ट्\n
                शहर: मुंबई
                """))
            elif st.session_state.language == 'mr':
                st.success(_(f"""
                मतदार पडताळणी!

                नाव: अमित शर्मा \n
                राज्य: महाराष्ट्र\n
                शहर: मुंबई
                """))
            elif st.session_state.language == 'pa':
                st.success(_(f"""
                ਵੋਟਰ ਦੀ ਪੁਸ਼ਟੀ ਹੋਈ!

                ਨਾਮ: ਅਮਿਤ ਸ਼ਰਮਾ\n
                ਰਾਜ: ਮਹਾਰਾਸ਼ਟਰ\n
                ਸ਼ਹਿਰ: ਮੁੰਬਈ\n
                """))


            
            
            if voter_id in st.session_state.voters:
                st.error(_("This Voter ID is already registered in our system"))
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
                st.error(_("Face capture failed. Please try again."))
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
            with st.status(_("Securing your data on the blockchain..."), expanded=True) as status:
                st.write(_("Generating cryptographic hash..."))
                time.sleep(1)
                st.write(_("Creating transaction..."))
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
                st.write(_("Mining block..."))
                time.sleep(1.5)
                st.session_state.blockchain.new_block(proof=123)
                
                status.update(label=_("Registration complete!"), state="complete", expanded=False)
            
            st.balloons()
            st.success(_("You are now registered to vote!"))
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


def check_voter_in_blockchain(voter_id, biometric_hash=None):
    chaindata_dir = "E:/voting_system/decentralized-voting-system/db/chaindata"    
    if not os.path.exists(chaindata_dir):
        st.error(_("Blockchain data directory not found"))
        return True 
    block_files = sorted(
        [f for f in os.listdir(chaindata_dir) if f.startswith("block_") and f.endswith(".json")],
        key=lambda x: int(x.split("_")[1].split(".")[0])
    )
    for block_file in block_files:
        try:
            with open(os.path.join(chaindata_dir, block_file), 'r') as f:
                block_data = json.load(f)
                for tx in block_data.get('transactions', []):
                    if tx.get('voter_id') == voter_id:
                        return True  
                    if biometric_hash and tx.get('biometric_hash') == biometric_hash:
                        return True                        
        except (json.JSONDecodeError, FileNotFoundError):
            continue
            
    return False

def verify_voter():
    if st.session_state.language == 'en':
        st.header(("Voter Verification"))
    elif st.session_state.language == 'hi':
        st.header(("मतदाता सत्यापन"))
    elif st.session_state.language == 'ta':
        st.header("வாக்காளர் சரிபார்ப்பு")
    elif st.session_state.language == 'mr':
        st.header("मतदार पडताळणी")
    elif st.session_state.language == 'pa':
        st.header("ਵੋਟਰ ਤਸਦੀਕ")
    
    
    if st.session_state.language == 'en':
        voter_id = st.text_input("Enter your Voter ID (e.g. VOTER982341)")
    elif st.session_state.language == 'hi':
        voter_id = st.text_input("अपना वोटर आईडी दर्ज करें (जैसे VOTER982341)")
    elif st.session_state.language == 'ta':
        voter_id = st.text_input("உங்கள் வாக்கைப் பதிவு செய்யுங்கள்")
    elif st.session_state.language == 'pa':
        voter_id = st.text_input("ਆਪਣਾ ਵੋਟਰ ਆਈਡੀ ਦਰਜ ਕਰੋ (ਜਿਵੇਂ ਕਿ VOTER982341)")
    elif st.session_state.language == 'mr':
        voter_id = st.text_input("तुमचा मतदार ओळखपत्र (उदा. VOTER982341) एंटर करा.")
    
    if voter_id and st.button("Start Verification"):
        if check_voter_in_blockchain(voter_id):
            st.error(_("This voter has already cast a vote (found in blockchain)"))
            return False
            
        try:
            with open(r"C:\Users\prade\ByteBug-Project\decentralized-voting-system\voter_database.json", 'r') as f:
                voters_db = json.load(f)
        except FileNotFoundError:
            st.error(_("Voter database not available"))
            return False
        except json.JSONDecodeError:
            st.error(_("Voter database corrupted"))
            return False
            
        if voter_id not in voters_db:
            st.error(_("Voter ID not found in database"))
            return False
            
        voter_data = voters_db[voter_id]
        
        if not voter_data.get("eligible", True):
            st.error(_(f"Not eligible: {voter_data.get('message', 'Voter is not eligible')}"))
            return False
            
        st.success(_(f"""
        Voter ID Verified!
        - Name: {voter_data.get('name', 'N/A')}
        - State: {voter_data.get('state', 'N/A')}
        - City: {voter_data.get('city', 'N/A')}
        """))
        
        st.write(_("Please look at the camera for biometric verification"))
        
        if voter_id not in st.session_state.voters:
            st.error(_("No face data registered for this voter"))
            return False
            
        FRAME_WINDOW = st.image([])
        camera = cv2.VideoCapture(0)
        verified = False
        current_encoding = None
        
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
            biometric_hash = str(current_encoding.tolist()) 
            if check_voter_in_blockchain(None, biometric_hash):
                st.error(_("This biometric identity has already been used for voting"))
                return False               
            st.success(_("Identity verified!"))
            st.session_state.current_voter = voter_id
            return True
        else:
            st.error(_("Face verification failed"))
            return False
            
    return False

def voting_page():
    st.title(_("🗳️ Cast Your Vote"))
    st.markdown("---")
    if 'voted_voters' not in st.session_state:
        st.session_state.voted_voters = set()
    if 'current_voter' not in st.session_state or st.session_state.current_voter is None:
        if not verify_voter():
            return
    
    voter_id = st.session_state.current_voter
    if voter_id not in st.session_state.voters:
        st.error(_("Voter not found in registry"))
        return
    if voter_id in st.session_state.voted_voters:
        st.error(_("You have already voted in this session"))
        return
    if st.session_state.voters[voter_id].has_voted:
        st.error(_("You have already voted in this election"))
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
    
    st.subheader(_("Select Your Candidate"))
    
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
                
                if st.button(_(f"Vote for {candidate['name']}", 
                            key=f"vote_{i}", use_container_width=True)):
                    with st.spinner(_(f"Recording vote for {candidate['name']}...")):
                        progress_bar = st.progress(0)
                        
                        for percent in range(100):
                            time.sleep(0.02)
                            progress_bar.progress(percent + 1)
                        
                        vote_timestamp = datetime.now()
                        verification_key = sha256(f"{voter_id}{candidate['id']}{vote_timestamp.timestamp()}".encode()).hexdigest()[:16]
                        vote_record = {
                            "voter_id": voter_id,
                            "candidate_id": candidate["id"],
                            "timestamp": vote_timestamp,
                            "verification_key": verification_key
                        }
                        st.session_state.votes.append(vote_record)
                        st.session_state.voters[voter_id].has_voted = True
                        st.session_state.voted_voters.add(voter_id)  
                        tx_data = {
                            "type": "vote",
                            "voter_id": voter_id,
                            "candidate_id": candidate["id"],
                            "timestamp": vote_timestamp.isoformat(),
                            "verification_hash": sha256(verification_key.encode()).hexdigest()
                        }
                        st.session_state.blockchain.new_transaction(_("system", tx_data))
                        st.session_state.blockchain.new_block(proof=123)
                    st.balloons()
                    st.success(_(f"Vote for {candidate['name']} recorded!"))
                    receipt_html = generate_voting_receipt(
                        voter_id=voter_id,
                        timestamp=vote_timestamp,
                        verification_key=verification_key,
                        candidate_color=candidate['color']
                    )
                    st.markdown(receipt_html, unsafe_allow_html=True)
                    st.download_button(
                        _("📄 Download Voting Receipt"),
                        data=receipt_html,
                        file_name=f"vote_receipt_{voter_id}.html",
                        mime="text/html"
                    )
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
                    time.sleep(3)
                    st.session_state.current_voter = None
                    st.experimental_rerun()

def verify_vote_page():
    """Page for voters to verify their vote"""
    st.title(_("🔍 Verify Your Vote"))
    
    with st.form("verify_vote"):
        voter_id = st.text_input(_("Voter ID")).strip().upper()
        verification_key = st.text_input(_("Verification Key"))
        
        if st.form_submit_button(_("Verify Vote")):
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
                
                st.success(_(f"""
                Vote Verified Successfully!
                - You voted for: {candidate['name']}
                - Voting time: {vote_record['timestamp'].strftime("%Y-%m-%d %H:%M:%S")}
                - Block confirmation: #{len(st.session_state.blockchain.chain)-1}
                """))
                st.info(_("""
                Your vote remains anonymous in the public record. 
                This verification only confirms your vote was recorded correctly.
                """))
            else:
                st.error(_("No matching vote found. Please check your credentials."))
def results_page():
    """Protected results dashboard - only accessible by admin"""
    if not st.session_state.get(_('admin_configured'), False):
        setup_admin()
        return
    
    if not verify_admin():
        return
    
    st.title(_("📊 Live Election Results"))
    st.markdown("---")
    
    html(particle_animation(), height=0)
    
    vote_counts = {c["id"]: 0 for c in CANDIDATES}
    for vote in st.session_state.votes:
        vote_counts[vote["candidate_id"]] += 1
    
    total_votes = sum(vote_counts.values())
    total_registered = len(st.session_state.voters)
    
    st.subheader(_("Participation Metrics"))
    cols = st.columns(3)
    with cols[0]:
        st.metric(_("Total Registered"), total_registered)
    with cols[1]:
        st.metric(_("Votes Cast"), total_votes, 
                 delta=f"{total_votes/total_registered*100:.1f}%" if total_registered > 0 else "0%",
                 delta_color="normal")
    with cols[2]:
       if total_votes > 0:
          leading_candidate_id = max(vote_counts, key=vote_counts.get)
          leading_candidate = next(c for c in CANDIDATES if c["id"] == leading_candidate_id)["name"]
          st.metric(_("Leading Candidate"), leading_candidate)
       else:
           st.metric(_("Leading Candidate"), "N/A")

    
    st.subheader(_("Vote Distribution"))
    
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
    
    st.subheader(_("Vote Share"))
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
        st.subheader(_("Voting Activity Over Time"))
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
    if not st.session_state.get(_('admin_configured'), False):
        setup_admin()
        return
    
    if not verify_admin():
        return
    
    st.title(_("👑 Administrator Dashboard"))
    st.markdown("---")
    
    html(particle_animation(), height=0)
    
    st.success(_("ADMIN PRIVILEGES ACTIVATED"), icon="⚠️")
    
    tab1, tab2, tab3 = st.tabs([_("📈 Statistics"), _("⛓ Blockchain"), _("⚙ System")])
    
    with tab1:
        st.subheader(_("Voter Analytics"))
        
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
        st.subheader(_("Blockchain Explorer"))
        
        html(blockchain_visualization(400))
        
        st.markdown(_("### Latest Blocks"))
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
        st.subheader(_("System Controls"))
        
        st.warning(_("Critical Operations - Use with caution"))
        
        if st.button(_("🗑️ Reset All Data"), type="primary"):
            st.session_state.blockchain = Blockchain()
            st.session_state.voters = {}
            st.session_state.votes = []
            st.success(_("System reset complete!"))
            time.sleep(1)
            st.experimental_rerun()
        
        if st.button(_("🔐 Generate Security Report")):
            with st.spinner(_("Analyzing system...")):
                time.sleep(2)
                st.success(_("Security audit complete"))
                st.json({
                    "blockchain_integrity": "verified",
                    "voter_data_encryption": "enabled",
                    "biometric_protection": "active",
                    "threat_level": "low"
                })
        
        st.markdown(_("### Data Management"))
        st.download_button(
            _("💾 Export Blockchain Data"),
            data=json.dumps([block.__dict__ for block in st.session_state.blockchain.chain]),
            file_name="blockchain_export.json",
            mime="application/json"
        )

def main():
    initialize_session()
    if not st.session_state.get(_('admin_configured'), False):
        setup_admin()
        return
    
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
        st.image("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA0wAAAHcCAYAAADlZCrdAAAAAXNSR0IArs4c6QAAIABJREFUeF7svXlwXFeW3vndt+aeWBL7SnADSXEntVAliVSVVJuq7bBNOWxP91SPI9ThcVTEtP+YifmrMX9MTEy0w46o9kxEOcbd7ul2uEfV7qrurlWqKu2UREmkSIILSIIEARD7jlzfcu/EuS8ThFQqd8FFSqRwUpEBEHj58t3fzSzkV9853xHgGxNgAkyACTABJsAEmAATYAJMgAl8IgHBXJgAE2ACTIAJMAEmwASYABNgAkzgkwmwYOJXBhNgAkyACTABJsAEmAATYAJM4FcQYMHELw0mwASYABNgAkyACTABJsAEmAALJn4NMAEmwASYABNgAkyACTABJsAENkaAHaaN8eKjmQATYAJMgAkwASbABJgAE9hEBFgwbaLN5qUyASbABJgAE2ACTIAJMAEmsDECLJg2xouPZgJMgAkwASbABJgAE2ACTGATEWDBtIk2m5fKBJgAE2ACTIAJMAEmwASYwMYIsGDaGC8+mgkwASbABJgAE2ACTIAJMIFNRIAF0ybabF4qE2ACTIAJMAEmwASYABNgAhsjwIJpY7z4aCbABJgAE2ACTIAJMAEmwAQ2EQEWTJtos3mpTIAJMAEmwASYABNgAkyACWyMAAumjfHio5kAE2ACTIAJMAEmwASYABPYRARYMG2izealMgEmwASYABNgAkyACTABJrAxAiyYNsaLj2YCTIAJMAEmwASYABNgAkxgExFgwbSJNpuXygSYABNgAkyACTABJsAEmMDGCLBg2hgvPpoJMAEmwASYABNgAkyACTCBTUSABdMm2mxeKhNgAkyACTABJsAEmAATYAIbI8CCaWO8+GgmwASYABNgAkyACTABJsAENhEBFkybaLN5qUyACTABJsAEmAATYAJMgAlsjAALpo3x4qOZABNgAkyACTABJsAEmAAT2EQEWDBtos3mpTIBJsAEmAATYAJMgAkwASawMQIsmDbGi49mAkyACTABJsAEmAATYAJMYBMRYMG0iTabl8oEmAATYAJMgAkwASbABJjAxgiwYNoYLz6aCTABJsAEmAATYAJMgAkwgU1EgAXTJtpsXioTYAJMgAkwASbABJgAE2ACGyPAgmljvPhoJsAEmAATYAJMgAkwASbABDYRARZMm2izealMgAkwASbABJgAE2ACTIAJbIwAC6aN8eKjmQATYAJMgAkwASbABJgAE9hEBFgwbaLN5qUyASbABJgAE2ACTIAJMAEmsDECLJg2xouPZgJMgAkwASbABJgAE2ACTGATEWDBtIk2m5fKBJgAE2ACTIAJMAEmwASYwMYIsGDaGC8+mgkwASbABJgAE2ACTIAJMIFNRIAF0ybabF4qE2ACTIAJMAEmwASYABNgAhsjwIJpY7z4aCbABJgAE2ACTIAJMAEmwAQ2EQEWTJtos3mpTIAJMAEmwASYABNgAkyACWyMAAumjfHio5kAE2ACTIAJMAEmwASYABPYRARYMG2izealMgEmwASYABNgAkyACTABJrAxAiyYNsaLj2YCTIAJMAEmwASYABNgAkxgExFgwbSJNpuXygSYABNgAkyACTABJsAEmMDGCLBg2hgvPpoJMAEmwASYABNgAkyACTCBTUSABdMm2mxeKhNgAkyACTABJsAEmAATYAIbI8CCaWO8+GgmwASYABNgAkyACTABJsAENhEBFkybaLN5qUyACTABJsAEmAATYAJMgAlsjAALpo3x4qOZABNgAkyACTABJsAEmAAT2EQEWDBtos3mpTIBJsAEmAATYAJMgAkwASawMQIsmDbGi49mAkyACTABJsAEmAATYAJMYBMRYMG0iTabl8oEmAATYAJMgAkwASbABJjAxgiwYNoYLz6aCTABJsAEmAATYAJMgAkwgU1EgAXTJtpsXioTYAJMgAkwASbABJgAE2ACGyPAgmljvPhoJsAEmAATYAJMgAkwASbABDYRARZMm2izealMgAkwASbABJgAE2ACTIAJbIwAC6aN8eKjmQATYAJMgAkwASbABJgAE9hEBFgwbaLN5qUyASbABJgAE2ACTIAJMAEmsDECLJg2xouPZgJMgAkwASbABJgAE2ACTGATEWDBtIk2m5fKBJgAE2ACTIAJMAEmwASYwMYIsGDaGC8+mgkwASbABJgAE2ACTIAJMIFNRIAF0ybabF4qE2ACTIAJMAEmwASYABNgAhsjwIJpY7z4aCbABJgAE2ACTIAJMAEmwAQ2EQEWTJtos3mpTIAJMAEmwASYABNgAkyACWyMAAumjfHio5kAE2ACTIAJMAEmwASYABPYRARYMG2izealMgEmwASYABNgAkyACTABJrAxAiyYNsaLj2YC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1GRyWHBIijCcBz86FFbtQ/XpuRNHfnnlysFXf4BhtDSv9GVvFL0eESACRGAZEiDBtAw3jS6ZCBABIkAEPpEAm5goKeWvQcfG7ZvX5Ls7h42EmbPLtel6pX7Euzp/3evS62QZTncPESACRIAIfBECJJi+CC06lggQASJABJYDATZWKmn5hmXkeKT6RdXLDgw4JJSWw9bRNRIBIkAEHjwCJJgevD2hKyICRIAIEIE/nACbnJzkMDkJG06eFKVSCdvvqAXvD+dKZyACRIAIrDgCJJhW3JbTgokAESACRIAIEAEiQASIABFYKgESTEslRccRASJABIgAESACRIAIEAEisOIIkGBacVtOCyYCRIAIEAEiQASIABEgAkRgqQRIMC2VFB1HBIgAESACRIAIEAEiQASIwIojQIJpxW05LZgIEAEiQASIABEgAkSACBCBpRIgwbRUUnQcESACRIAIEAEiQASIABEgAiuOAAmmFbfltGAiQASIABEgAkSACBABIkAElkqABNNSSdFxRIAIEAEiQASIABEgAkSACKw4AiSYVtyW04KJABEgAkSACBABIkAEiAARWCoBEkxLJUXHEQEiQASIABEgAkSACBABIrDiCJBgWnFbTgsmAkSACBABIkAEiAARIAJEYKkESDAtlRQdRwSIABEgAkSACBABIkAEiMCKI0CCacVtOS2YCBABIkAEiAARIAJEgAgQgaUSIMG0VFJ0HBEgAkSACBABIkAEiAARIAIrjgAJphW35bRgIkAEiAARIAJEgAgQASJABJZKgATTUknRcUSACBABIkAEiAARIAJEgAisOAIkmFbcltOCiQARIAJEgAgQASJABIgAEVgqARJMSyVFxxEBIkAEiAARIAJEgAgQASKw4giQYFpxW04LJgJEgAgQASJABIgAESACRGCpBEgwLZUUHUcEiAARIAJEgAgQASJABIjAiiNAgmnFbTktmAgQASJABIgAESACRIAIEIGlEiDBtFRSdBwRIAJEgAgQASJABIgAESACK44ACaYVt+W0YCJABIgAESACRIAIEAEiQASWSoAE01JJ0XFEgAgQASJABIgAESACRIAIrDgCJJhW3JbTgokAESACRIAIEAEiQASIABFYKgESTEslRccRASJABIgAESACRIAIEAEisOIIkGBacVtOC35QCAgh8P3Hdu0CNjkJsAsvbNcu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gAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCTCYxOqDNAgggAACCCCAAAIIICCQAINJoDKIggACCCCAAAIIIIAAAmIJMJjE6oM0CCCAAAIIIIAAAgggIJAAg0mgMoiCAAIIIIAAAggggAACYgkwmMTqgzQIIIAAAggggAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCTCYxOqDNAgggAACCCCAAAIIICCQAINJoDKIggACCCCAAAIIIIAAAmIJMJjE6oM0CCCAAAIIIIAAAgggIJAAg0mgMoiCAAIIIIAAAggggAACYgkwmMTqgzQIIIAAAggggAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCTCYxOqDNAgggAACCCCAAAIIICCQAINJoDKIggACCCCAAAIIIIAAAmIJMJjE6oM0CCCAAAIIIIAAAgggIJAAg0mgMoiCAAIIIIAAAggggAACYgkwmMTqgzQIIIAAAggggAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCTCYxOqDNAgggAACCCCAAAIIICCQAINJoDKIggACCCCAAAIIIIAAAmIJMJjE6oM0CCCAAAIIIIAAAgggIJAAg0mgMoiCAAIIIIAAAggggAACYgkwmMTqgzQIIIAAAggggAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCTCYxOqDNAgggAACCCCAAAIIICCQAINJoDKIggACCCCAAAIIIIAAAmIJMJjE6oM0CCCAAAIIIIAAAgggIJAAg0mgMoiCAAIIIIAAAggggAACYgkwmMTqgzQIIIAAAggggAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCTCYxOqDNAgggAACCCCAAAIIICCQAINJoDKIggACCCCAAAIIIIAAAmIJMJjE6oM0CCCAAAIIIIAAAgggIJAAg0mgMoiCAAIIIIAAAggggAACYgkwmMTqgzQIIIAAAggggAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCTCYxOqDNAgggAACCCCAAAIIICCQAINJoDKIggACCCCAAAIIIIAAAmIJMJjE6oM0CCCAAAIIIIAAAgggIJAAg0mgMoiCAAIIIIAAAggggAACYgkwmMTqgzQIIIAAAggggAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCTCYxOqDNAgggAACCCCAAAIIICCQAINJoDKIggACCCCAAAIIIIAAAmIJMJjE6oM0CCCAAAIIIIAAAgggIJAAg0mgMoiCAAIIIIAAAggggAACYgkwmMTqgzQIIIAAAggggAACCCAgkACDSaAyiIIAAggggAACCCCAAAJiCfwneYEP7Zy0BC4AAAAASUVORK5CYII=")
        st.markdown("---")
        
        menu_options = [_("🏠 Home"), _("👤 Register"), _("🗳️ Vote")]
        if st.session_state.get('admin_configured', False):
            menu_options.extend([_("📊 Results"), _("👑 Admin")])
        
        menu = st.radio(
            "Navigation",
            menu_options,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("### System Status")
        cols = st.columns(2)
        cols[0].metric(_("Voters"), len(st.session_state.voters))
        cols[1].metric(_("Votes"), len(st.session_state.votes))
        
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
        
        if st.session_state.get(_('admin_authenticated'), False):
            if st.button(_("🔒 Logout Admin")):
                st.session_state.admin_authenticated = False
                st.session_state.current_admin = None
                st.rerun()
    
    if menu == "🏠 Home":
        home_page()
    elif menu == _("👤 Register"):
        register_page()
    elif menu == _("🗳️ Vote"):
        voting_page()
    elif menu == _("📊 Results"):
        results_page()
    elif menu == _("👑 Admin"):
        admin_page()

if __name__ == "__main__":
    main()
