# tasks.py
from celery import shared_task
import os
import json
import logging
from django.conf import settings
from .views import process_zip_file, redis_client, update_progress

logger = logging.getLogger('apps')

@shared_task
def process_images_task(session_id, temp_file_path, processing_type, excel_filename):
    """Process images from ZIP file"""
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            api_key = settings.GOOGLE_API_KEY
        
        logger.info(f"Starting task for session {session_id}")
        logger.info(f"File path: {temp_file_path}")
        
        extracted_data, image_results = process_zip_file(
            temp_file_path, 
            api_key, 
            processing_type, 
            session_id, 
            max_images=50
        )
        
        result = {
            'success': True,
            'data': extracted_data,
            'image_results': image_results,
            'processing_type': processing_type,
            'excel_filename': excel_filename,
            'session_id': session_id,
            'total_images': len(image_results),
            'successful_images': sum(1 for r in image_results if r['success']),
            'total_records': len(extracted_data)
        }
        
        redis_client.set(
            f"result:{session_id}", 
            json.dumps(result, ensure_ascii=False), 
            ex=7200
        )
        
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Cleaned up: {temp_file_path}")
        
        success_count = sum(1 for r in image_results if r['success'])
        update_progress(
            session_id, 
            len(image_results), 
            len(image_results), 
            f"Xong! {success_count}/{len(image_results)} ảnh"
        )
        
        logger.info(f"Task completed: {success_count}/{len(image_results)} images")
        return f"Success: {success_count}/{len(image_results)}"
        
    except Exception as e:
        logger.error(f"Task error: {e}")
        
        error_result = {
            'success': False,
            'error': str(e),
            'data': [],
            'image_results': [],
            'processing_type': processing_type,
            'session_id': session_id
        }
        
        redis_client.set(
            f"result:{session_id}", 
            json.dumps(error_result, ensure_ascii=False), 
            ex=3600
        )
        
        update_progress(session_id, 0, 0, f"Lỗi: {str(e)}")
        raise e