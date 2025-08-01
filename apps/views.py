import os
import zipfile
import io
import json
import time
import re
import base64
import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from openpyxl.utils import get_column_letter
from .forms import UploadZipForm

# --- Gemini + LLM Setup ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- Pydantic models ---
from pydantic import BaseModel, Field
from typing import List

class Attribute(BaseModel):
    Name_subject: str
    Id_subject: str
    Major: str
    Sbd: str
    Thi: float

class Table(BaseModel):
    items: List[Attribute]

prompt_text = """
Trích xuất danh sách sinh viên từ ảnh bảng điểm bên dưới.
Trích xuất các trường thông tin: Tên học phần, Mã học phần, Ngành học, SBD, Thi
Trả về kết quả theo định dạng JSON:
{
  "items": [
    { 
    "Name_subject": "", 
    "Id_subject": "", 
    "Major": "", 
    "Sbd": "", 
    "Thi": 8.5 
    }
  ]
}
"""

def extract_structured_data_from_image_bytes(image_bytes, llm_model, filename="", max_retries=3, delay=2):
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = "jpeg" if filename.lower().endswith(("jpg", "jpeg")) else "png"
    data_uri = f"data:image/{mime_type};base64,{image_b64}"

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt_text},
            {"type": "image_url", "image_url": {"url": data_uri}}
        ]
    )

    for attempt in range(max_retries):
        try:
            response = llm_model.invoke([message])
            if hasattr(response, 'content'):
                content = response.content.strip().replace('```json', '').replace('```', '')
                data = json.loads(content)
                return Table.model_validate(data)
            return None
        except Exception as e:
            print(f"Retry {attempt + 1}/{max_retries} failed for {filename}: {e}")
            time.sleep(delay * (2 ** attempt))
    return None

def process_images_in_zip(zip_file_obj, api_key):
    all_data = []
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        google_api_key=api_key
    )

    with zipfile.ZipFile(zip_file_obj, 'r') as zf:
        for entry in zf.infolist():
            if entry.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                with zf.open(entry.filename) as file:
                    image_bytes = file.read()
                    time.sleep(3)
                    result = extract_structured_data_from_image_bytes(image_bytes, llm, filename=entry.filename)
                    if result and result.items:
                        for item in result.items:
                            all_data.append(item.model_dump())
    return all_data

def upload_file(request):
    if request.method == 'POST':
        form = UploadZipForm(request.POST, request.FILES)
        if form.is_valid():
            zip_file = request.FILES['zip_file']
            excel_filename = form.cleaned_data.get('excel_filename') or "ocr_ketqua.xlsx"
            subject_filter = form.cleaned_data.get('search_subject', '').lower()
            major_filter = form.cleaned_data.get('search_major', '').lower()
            id_filter = form.cleaned_data.get('search_id', '').lower()

            if not zipfile.is_zipfile(zip_file):
                return render(request, 'apps/upload.html', {'form': form, 'error_message': 'File ZIP không hợp lệ.'})

            extracted_data = process_images_in_zip(zip_file, settings.GOOGLE_API_KEY)
            df = pd.DataFrame(extracted_data)

            if not df.empty:
                df['Sbd'] = df['Sbd'].astype(str)
                df['Thi'] = pd.to_numeric(df['Thi'], errors='coerce').fillna(0.0)

                if subject_filter:
                    df = df[df['Name_subject'].str.lower().str.contains(subject_filter)]
                if id_filter:
                    df = df[df['Id_subject'].str.lower().str.contains(id_filter)]
                if major_filter:
                    df = df[df['Major'].str.lower().str.contains(major_filter)]

                df_display = df[['Sbd', 'Thi']] if not df.empty else pd.DataFrame(columns=['Sbd', 'Thi'])

                request.session['extracted_data'] = df.to_dict(orient='records')
                request.session['df_data'] = df_display.to_json(orient='records')
                request.session['excel_filename'] = excel_filename

                return redirect('result_page')
            else:
                return render(request, 'apps/upload.html', {'form': form, 'error_message': 'Không có dữ liệu phù hợp.'})
        else:
            return render(request, 'apps/upload.html', {'form': form})
    else:
        return render(request, 'apps/upload.html', {'form': UploadZipForm()})

def result_page(request):
    df_data_json = request.session.get('df_data')
    if not df_data_json:
        return redirect('upload_file')
    df = pd.read_json(io.StringIO(df_data_json), orient='records')
    df['Sbd'] = df['Sbd'].astype(str)
    return render(request, 'apps/results.html', {
        'df_columns': df.columns.tolist(),
        'df_rows': df.values.tolist(),
        'has_data': not df.empty
    })

def download_excel(request):
    extracted_data = request.session.get('extracted_data')
    excel_filename = request.session.get('excel_filename', 'ocr_ketqua.xlsx')
    if not extracted_data:
        return redirect('upload_file')

    df = pd.DataFrame(extracted_data)
    df['Sbd'] = df['Sbd'].astype(str)
    df['Thi'] = pd.to_numeric(df['Thi'], errors='coerce').fillna(0.0)

    output_cols = ['TT', 'Lớp môn nhập AAIS', 'Tài khoản', 'SBD', 'Lớp', 'MSSV', 'Họ và tên', 'Ngày sinh', 'X', 'QT', 'KT', 'Thi', 'Điểm học phần', 'Thang điểm chữ', 'Thang điểm 4', 'Ghi chú']
    rows = []
    for idx, row in df.iterrows():
        new_row = {col: None for col in output_cols}
        new_row['TT'] = idx + 1
        new_row['SBD'] = row['Sbd']
        new_row['Thi'] = row['Thi']
        rows.append(new_row)
    df_final = pd.DataFrame(rows, columns=output_cols)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Sheet1')
        ws = writer.sheets['Sheet1']
        for i in range(2, ws.max_row + 1):
            ws[f'{get_column_letter(output_cols.index("Thi") + 1)}{i}'].number_format = '0.0'
            ws[f'{get_column_letter(output_cols.index("SBD") + 1)}{i}'].number_format = '@'
    buffer.seek(0)

    for k in ['extracted_data', 'df_data', 'excel_filename']:
        request.session.pop(k, None)

    return HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition': f'attachment; filename="{excel_filename}"'})
