        import os
        from sqlalchemy import create_engine, text
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        from dotenv import load_dotenv

        load_dotenv()

        SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
        engine = create_engine(SQLALCHEMY_DATABASE_URL)

        # Enable the pgvector extension
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
            conn.commit()

        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
        

