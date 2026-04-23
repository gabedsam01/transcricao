import pytest
from app.logger import logger
import sys

def test_logger_availability():
    # Verify logger is imported and usable
    logger.info("Testing logger availability")

def test_logger_output(capsys):
    # Re-setup to ensure it uses the current sys.stdout which is captured by pytest
    from app.logger import setup_logging
    setup_logging()
    
    # Verify logger output to stdout with configured format
    logger.info("Testing logger output content")
    captured = capsys.readouterr()
    
    # Check if output is in stdout (as configured in setup_logging)
    assert "INFO" in captured.out
    assert "Testing logger output content" in captured.out
    # Check for name/function/line structure (partial check)
    assert "test_logger" in captured.out
    assert "test_logger_output" in captured.out
