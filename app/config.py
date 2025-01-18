CHUNK_SIZE = 500 # maximum size of each chunk
BATCH_SIZE = 100  # number of documents processed and inserted into the ChromaDB collection in each batch
TEMPERATURE = 0.7 # controls the randomness of the model’s output
MAX_TOKENS = 1024  # Max token limit
TOP_P = 1 # cumulative probability of the token selection
N_CHUNKS = 2 # no of similar chunks (context) to be retrieved from vectorDB
CONFIDENCE_THRESHOLD = 0.6 # filters semantic search results by only including documents with a similarity (distance) score greater than or equal to a specified value, ensuring relevance