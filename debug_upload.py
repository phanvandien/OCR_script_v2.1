import os
import sys
import django

sys.path.append('/home/dienpv/OCR_script')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','ocr.settings')
django.setup()

from django.conf import settings
import zipfile
import tempfile

def test_file_operations():
  print("Django Settings")
  print(f"BASE_DIR: {settings.BASE_DIR}")
  print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
  print(f"MEDIA_URL: {settings.MEDIA_URL}")

  print("\n Directory Check")
  media_root = settings.MEDIA_ROOT
  temp_dir = os.path.join(media_root, 'temp')

  print(f"MEDIA_ROOT exists: {os.path.exists(media_root)}")
  print(f"temp dir exists: {os.path.exists(temp_dir)}")
  if not os.path.exists(temp_dir):
      print("Creating temp directory...")
      os.makedirs(temp_dir, exist_ok=True)
      print(f"temp dir created: {os.path.exists(temp_dir)}")

  print(f"temp dir permissions: {oct(os.stat(temp_dir).st_mode)[-3:]}")

  print("\n File Write Test")
  test_file = os.path.join(temp_dir, 'test.txt')
  try:
     with open(test_file, 'w') as f:
         f.write("test content")
     print(f"Can write to: {test_file}")
     os.remove(test_file)
     print("Can deleted test file")
  except Exception as e:
     print(f"Cannot write to temp dir: {e}")

  print("\n ZIP Creation Test ")
  zip_path = os.path.join(temp_dir, "test.zip")
  try:
     with zipfile.ZipFile(zip_path, 'w') as zf:
         zf.writestr('test.txt','test content')
     print(f"Created test ZIP: {zip_path}")
     print(f"ZIP exists: {os.path.exists(zip_path)}")
     print(f"ZIP size: {os.path.getsize(zip_path)} bytes")

     with zipfile.ZipFile(zip_path, 'r') as zf:
         files = zf.namelist()
         print(f"ZIP contents:{files}")

     os.remove(zip_path)
     print("ZIP test completed")

  except Exception as e:
     print(f"ZIP test failed: {e}")

if __name__=="__main__":
   test_file_operations()
