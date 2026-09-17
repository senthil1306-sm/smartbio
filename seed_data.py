import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database.session import SessionLocal, Base, engine
from app.seed_demo_helper import perform_seed

def main():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("Generating realistic demo data and synthetic hull imagery...")
        vessel, count = perform_seed(db)
        print(f"Successfully seeded {count} inspections for vessel '{vessel.vessel_name}' (ID: {vessel.id}).")
    finally:
        db.close()

if __name__ == "__main__":
    main()
