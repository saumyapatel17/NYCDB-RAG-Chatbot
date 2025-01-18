import os
from app.ingestion import DocumentIngestor
from app.initialiseDB import VectorDBSetup
import app.clients as client
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

def setup_database():
    """
    One-time initialization of the database with all CSV files and their metadata.
    """
    data_dir = os.environ.get("DATA_DIR")
    metadata_dir = os.environ.get("METADATA_DIR")
    db_initialized_flag = "db_initialized.flag"

    if not os.path.exists(db_initialized_flag):
        client_manager = client.ClientManager()
        vector_db_instance = VectorDBSetup(client_manager)
        document_ingestor_instance = DocumentIngestor()
        
        try:
            collection = vector_db_instance.initialize_vectorDB()
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            
            for csv_file in csv_files:
                csv_path = os.path.join(data_dir, csv_file)
                metadata_path = os.path.join(metadata_dir, csv_file)
                
                if os.path.exists(metadata_path):
                    document_ingestor_instance.ingest_documents(
                        collection, csv_path, metadata_path
                    )
                else:
                    print(f"Warning: No metadata file found for {csv_file}")
            
            with open(db_initialized_flag, 'w') as f:
                f.write('initialized')
            
            print("Database initialized successfully with all CSV files and metadata.")
        except Exception as e:
            print(f"Error during database initialization: {e}")
    else:
        print("Database already initialized. Skipping initialization step.")

if __name__ == "__main__":
    setup_database()
