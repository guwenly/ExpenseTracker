import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import bcrypt
import os
import jwt
import datetime
import logging
from dotenv import load_dotenv

load_dotenv()

# Database setup
engine = create_engine(os.getenv('DATABASE_URL'))
Session = sessionmaker(bind=engine)
Base = declarative_base()

# JWT configuration
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = datetime.timedelta(minutes=5)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

Base.metadata.create_all(engine)

def hash_password(password):
    return bcrypt.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)

def register_user(username, password):
    username = username.lower()  # Convert username to lowercase
    session = Session()
    if session.query(User).filter_by(username=username).first():
        return False
    new_user = User(username=username, password_hash=hash_password(password))
    session.add(new_user)
    session.commit()
    session.close()
    return True

def authenticate_user(username, password):
    username = username.lower()  # Convert username to lowercase
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    if user and verify_password(password, user.password_hash):
        return user.id
    return None

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user_id = authenticate_user(username, password)
        if user_id:
            token = create_token(user_id)
            st.session_state.token = token
            st.session_state.user = username.lower()  # Store lowercase username
            st.session_state.user_id = user_id
            st.success(f"Logged in as {username.lower()}")
            logging.info(f"Authenticated user: {username.lower()}")
            
            # Store token in sessionStorage
            st.write("""
            <script>
            sessionStorage.setItem('jwt_token', '""" + token + """');
            </script>
            """, unsafe_allow_html=True)
            
            return True
        else:
            st.error("Invalid username or password")
    return False

def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.user_id = None
    
    # Clear token from sessionStorage
    st.write("""
    <script>
    sessionStorage.removeItem('jwt_token');
    </script>
    """, unsafe_allow_html=True)
    
    st.success("Logged out successfully")

def register():
    st.subheader("Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register"):
        if register_user(username, password):
            st.success("Registration successful. You can now log in.")
        else:
            st.error("Username already exists. Please choose a different username.")

def is_authenticated():
    if 'token' not in st.session_state or not st.session_state.token:
        # Check if token exists in sessionStorage
        token = st.query_params.get('jwt_token')
        if token:
            user_id = decode_token(token)
            if user_id:
                st.session_state.token = token
                st.session_state.user_id = user_id
                logging.info("Token retrieved from sessionStorage")
                return True
        logging.info("No valid token found")
        return False
    
    user_id = decode_token(st.session_state.token)
    if user_id:
        new_token = create_token(user_id)
        st.session_state.token = new_token
        
        # Update token in sessionStorage
        st.write(f"""
        <script>
        sessionStorage.setItem('jwt_token', '{new_token}');
        </script>
        """, unsafe_allow_html=True)
        
        logging.info("Token refreshed")
        return True
    logging.info("User not authenticated")
    return False

def authentication_required(func):
    def wrapper(*args, **kwargs):
        if is_authenticated():
            return func(*args, **kwargs)
        else:
            st.warning("Please log in to access this page.")
            login()
    return wrapper
