import os
import logging
from celery import Celery
from markitdown import MarkItDown

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery("markitdown_worker", broker=REDIS_URL, backend=REDIS_URL)

# Output directory (mounted in Kubernetes)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/data/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize MarkItDown once per worker
converter = MarkItDown()

@app.task(name="convert_to_markdown")
def convert_to_markdown(file_path: str) -> str:
    """
    Convert a PDF or DOCX file to Markdown using MarkItDown.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Starting conversion: {file_path}")
        result = converter.convert(file_path)
        markdown = result.text_content

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(OUTPUT_DIR, f"{base_name}.md")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown)

        logger.info(f"File successfully converted: {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Failed to convert {file_path}: {e}", exc_info=True)
        raise