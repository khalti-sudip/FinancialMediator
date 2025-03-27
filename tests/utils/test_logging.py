"""
Tests for the logging utility functions.
"""

import logging
import pytest
from core.utils.logging import get_logger, log_info, log_error, log_warning, log_debug, log_critical

def test_get_logger():
    """Test getting a logger instance."""
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test"

def test_log_info(caplog):
    """Test logging an info message."""
    logger = get_logger("test")
    message = "Test info message"
    attributes = {"key": "value"}
    
    with caplog.at_level(logging.INFO):
        log_info(logger, message, attributes=attributes)
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "INFO"
    assert record.message == message
    assert record.attributes == attributes

def test_log_error(caplog):
    """Test logging an error message with exception."""
    logger = get_logger("test")
    message = "Test error message"
    exception = ValueError("Test error")
    attributes = {"key": "value"}
    
    with caplog.at_level(logging.ERROR):
        log_error(logger, message, exception=exception, attributes=attributes)
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "ERROR"
    assert record.message == message
    assert record.attributes == attributes
    assert record.exc_info[1] == exception

def test_log_warning(caplog):
    """Test logging a warning message."""
    logger = get_logger("test")
    message = "Test warning message"
    attributes = {"key": "value"}
    
    with caplog.at_level(logging.WARNING):
        log_warning(logger, message, attributes=attributes)
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "WARNING"
    assert record.message == message
    assert record.attributes == attributes

def test_log_debug(caplog):
    """Test logging a debug message."""
    logger = get_logger("test")
    message = "Test debug message"
    attributes = {"key": "value"}
    
    with caplog.at_level(logging.DEBUG):
        log_debug(logger, message, attributes=attributes)
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "DEBUG"
    assert record.message == message
    assert record.attributes == attributes

def test_log_critical(caplog):
    """Test logging a critical message with exception."""
    logger = get_logger("test")
    message = "Test critical message"
    exception = ValueError("Test critical error")
    attributes = {"key": "value"}
    
    with caplog.at_level(logging.CRITICAL):
        log_critical(logger, message, exception=exception, attributes=attributes)
        
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "CRITICAL"
    assert record.message == message
    assert record.attributes == attributes
    assert record.exc_info[1] == exception
