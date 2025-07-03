import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from models import Base


load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection and session manager"""
    
    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'interpol_db')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'postgres')
        
        self.engine = None
        self.SessionLocal = None
        self.session = None
        
    def get_database_url(self):
        """Get database connection URL"""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def create_engine(self):
        """Create SQLAlchemy engine"""
        try:
            database_url = self.get_database_url()
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  
            )
            logger.info("Database engine created successfully")
            return self.engine
        except Exception as e:
            logger.error(f"Error creating database engine: {e}")
            raise
    
    def create_session_factory(self):
        """Create session factory"""
        if not self.engine:
            self.create_engine()
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        logger.info("Session factory created successfully")
        return self.SessionLocal
    
    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            self.create_session_factory()
        
        if not self.session and self.SessionLocal:
            self.session = scoped_session(self.SessionLocal)
        
        return self.session() if self.session else None
    
    def create_tables(self):
        """Create all tables"""
        try:
            if not self.engine:
                self.create_engine()
            
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def close_session(self):
        """Close database session"""
        if self.session:
            self.session.close()
            self.session = None
            logger.info("Database session closed")
    
    def close_engine(self):
        """Close database engine"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            logger.info("Database engine closed")


db_manager = DatabaseManager()


def get_db():
    """Dependency to get database session"""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        if session:
            session.close() 