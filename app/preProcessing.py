import os
import pandas as pd
from typing import Dict
from app.config import CHUNK_SIZE

class DocumentProcessor:
    """
    A class to handle various document processing tasks, including reading
    and chunking different types of files (txt, pdf, docx, csv).
    """

    @staticmethod
    def normalize_column_name(column_name: str) -> str:
        """
        Normalize column names by removing spaces, special characters and converting to lowercase.
        """
        return column_name.lower().replace(' ', '_').replace('-', '_')

    def create_column_mapping(self, csv_columns: list, metadata_columns: list) -> dict:
        """
        Create a mapping between CSV columns and metadata columns.
        """
        csv_mapping = {self.normalize_column_name(col): col for col in csv_columns}
        metadata_mapping = {self.normalize_column_name(col): col for col in metadata_columns}
        
        column_mapping = {}
        for norm_col in csv_mapping:
            if norm_col in metadata_mapping:
                column_mapping[csv_mapping[norm_col]] = metadata_mapping[norm_col]
        
        return column_mapping

    def read_metadata_file(self, metadata_file_path: str) -> Dict:
        """
        Reads the metadata CSV file containing column descriptions.
        """
        try:
            metadata_df = pd.read_csv(metadata_file_path)
            metadata_dict = {}
            
            for _, row in metadata_df.iterrows():
                # Store using original column name from metadata
                metadata_dict[row['column_name']] = {
                    'data_type': row['data_type'],
                    'values': row['values'],
                    'full_name': row['full_name'],
                    'description': row['description'],
                    'notes': row['notes']
                }
            
            return metadata_dict
        except Exception as e:
            raise Exception(f"Error reading metadata file: {e}")

    def read_csv_with_metadata(self, file_path: str, metadata_file_path: str) -> str:
        """
        Read CSV file and its metadata, handling column name mismatches.
        """
        try:
            df = pd.read_csv(file_path)
            metadata_dict = self.read_metadata_file(metadata_file_path)
            column_mapping = self.create_column_mapping(
                df.columns.tolist(),
                list(metadata_dict.keys())
            )
            
            # Process each row with metadata
            headers = df.columns.tolist()
            
            # Add metadata header section
            metadata_header = "FILE METADATA:\n"
            for csv_col in headers:
                if csv_col in column_mapping:
                    metadata_col = column_mapping[csv_col]
                    metadata_header += (
                        f"Column: {csv_col}\n"
                        f"Type: {metadata_dict[metadata_col]['data_type']}\n"
                        f"Description: {metadata_dict[metadata_col]['description']}\n"
                        f"Notes: {metadata_dict[metadata_col]['notes']}\n\n"
                    )
                else:
                    metadata_header += (
                        f"Column: {csv_col}\n"
                        f"Type: unknown\n"
                        f"Description: No metadata available\n"
                        f"Notes: No metadata available\n\n"
                    )
            
            data_rows = []
            for _, row in df.iterrows():
                row_items = []
                for header in headers:
                    if header in column_mapping:
                        metadata_col = column_mapping[header]
                        row_items.append(
                            f"{header} ({metadata_dict[metadata_col]['full_name']}): {row[header]}"
                        )
                    else:
                        row_items.append(f"{header}: {row[header]}")
                data_rows.append(", ".join(row_items))
            
            # Combine metadata and data with clear section separation
            return f"{metadata_header}\n\nDATA RECORDS:\n" + "\n".join(data_rows)
            
        except Exception as e:
            print(f"Error details: {str(e)}")
            raise Exception(f"Error processing CSV with metadata: {e}")

    def log_column_mapping(self, csv_columns: list, metadata_columns: list, mapping: dict):
        """
        Debug helper to log column mapping details.
        """
        print("\nColumn Mapping Debug Info:")
        print("CSV Columns:", csv_columns)
        print("Metadata Columns:", metadata_columns)
        print("Mapping:", mapping)


    def read_document(self, file_path: str, metadata_file_path: str) -> str:
        """
        Reads document content based on the file extension.
        """
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        try:
            if file_extension == '.csv':
                return self.read_csv_with_metadata(file_path, metadata_file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except ValueError as e:
            raise ValueError(f"Error processing document: {e}")

    def chunking(self, text: str, chunk_size: int = CHUNK_SIZE) -> list:
        """
        Split text into chunks of a specified size.
        Args:
            text (str): The text to be split.
            chunk_size (int, optional): The maximum size of each chunk. Defaults to CHUNK_SIZE.
        Returns:
            list: A list of text chunks.
        """
        try:
            sentences = text.replace('\n', ' ').split('. ')
            chunks = []
            current_chunk = []
            current_size = 0

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if not sentence.endswith('.'):
                    sentence += '.'

                sentence_size = len(sentence)
                if current_size + sentence_size > chunk_size and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_size = sentence_size
                else:
                    current_chunk.append(sentence)
                    current_size += sentence_size

            if current_chunk:
                chunks.append(' '.join(current_chunk))

            return chunks
        except Exception as e:
            raise RuntimeError(f"Error during text chunking: {e}")
