"""
Test script para probar los schemas de Pydantic
"""

import sys
import os
from datetime import datetime, timedelta
from loguru import logger

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from schema import TaskCreate
from utils.logger import logs_config

def config_test_logging():
    """Configure loguru for this test"""
    # Get project root (2 levels up from src/database/)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    logs_config(project_root, "test_schemas.log")

def test_task_create():
    """Test TaskCreate with different cases"""
    logger.info("🧪 Testing TaskCreate...")
    
    # Test 1: Normal case
    try:
        task = TaskCreate(
            title="  Comprar leche  ",  # With spaces
            description="  En el súper de la esquina  ",
            due_date=datetime.now() + timedelta(days=1)
        )
        logger.success(f"✅ Test 1 OK: title='{task.title}', description='{task.description}'")
    except Exception as e:
        logger.error(f"❌ Test 1 FAILED: {e}")
    
    # Test 2: Without description
    try:
        task = TaskCreate(
            title="Llamar al médico",
            due_date=datetime.now() + timedelta(days=2)
        )
        logger.success(f"✅ Test 2 OK: title='{task.title}', description={task.description}")
    except Exception as e:
        logger.error(f"❌ Test 2 FAILED: {e}")
    
    # Test 3: Empty title (should fail)
    try:
        task = TaskCreate(
            title="   ",  # Only spaces
            due_date=datetime.now()
        )
        logger.error(f"❌ Test 3 FAILED: Should have failed but didn't")
    except ValueError as e:
        logger.success(f"✅ Test 3 OK: Correctly rejected empty title: {e}")
    except Exception as e:
        logger.error(f"❌ Test 3 FAILED: Wrong error type: {e}")
    
    # Test 4: Title too long (should fail)
    try:
        long_title = "x" * 201  # 201 characters
        task = TaskCreate(
            title=long_title,
            due_date=datetime.now()
        )
        logger.error(f"❌ Test 4 FAILED: Should have failed but didn't")
    except Exception as e:
        logger.success(f"✅ Test 4 OK: Correctly rejected long title: {type(e).__name__}")
    
    # Test 5: Description with only spaces (should clean to None)
    try:
        task = TaskCreate(
            title="Test",
            description="   ",  # Only spaces
            due_date=datetime.now()
        )
        logger.success(f"✅ Test 5 OK: Empty description cleaned to: {task.description}")
    except Exception as e:
        logger.error(f"❌ Test 5 FAILED: {e}")

def test_dict_conversion():
    """Test dictionary conversion"""
    logger.info("🧪 Testing dict conversion...")
    
    try:
        task = TaskCreate(
            title="  Test task  ",
            description="  Test description  ",
            due_date=datetime(2025, 6, 1, 10, 30)
        )
        
        task_dict = task.model_dump()
        logger.success("✅ Dict conversion OK:")
        for key, value in task_dict.items():
            logger.debug(f"   {key}: {value}")
            
    except Exception as e:
        logger.error(f"❌ Dict conversion FAILED: {e}")

def main():
    """Run all tests"""
    config_test_logging()
    
    logger.info("=== TESTING PYDANTIC SCHEMAS ===")
    test_task_create()
    test_dict_conversion()
    logger.info("=== TESTS COMPLETED ===")

if __name__ == "__main__":
    main()