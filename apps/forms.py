# apps/forms.py
from django import forms
import os
from django.conf import settings

class UploadZipForm(forms.Form):
    PROCESSING_CHOICES = [
        ('transcript', 'Bảng điểm'),
        ('certificate', 'Văn bằng'),
    ]
    
    zip_file = forms.FileField(
        label='Tải lên file ZIP chứa ảnh',
        help_text='Hỗ trợ định dạng: JPG, JPEG, PNG. Tối đa 100MB.',
        widget=forms.FileInput(attrs={
            'accept': '.zip',
            'class': 'form-control'
        })
    )
    
    processing_type = forms.ChoiceField(
        choices=PROCESSING_CHOICES,
        initial='transcript',
        widget=forms.RadioSelect,
        label='Loại xử lý',
        help_text='Chọn loại dữ liệu cần trích xuất'
    )
    
    excel_filename = forms.CharField(
        label='Tên file Excel kết quả',
        max_length=100,
        required=False,
        initial='ocr_ketqua.xlsx',
        widget=forms.TextInput(attrs={
            'placeholder': 'Ví dụ: bang_diem.xlsx',
            'class': 'form-control'
        })
    )
    
    # Only show API key field if not configured in settings
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Check if API key is already configured
        api_key_configured = bool(
            getattr(settings, 'GOOGLE_API_KEY', None) or 
            os.environ.get('GOOGLE_API_KEY')
        )
        
        if not api_key_configured:
            self.fields['api_key'] = forms.CharField(
                label='Google API Key',
                max_length=200,
                required=True,
                widget=forms.TextInput(attrs={
                    'placeholder': 'Nhập Google Gemini API Key',
                    'class': 'form-control'
                }),
                help_text='API key để sử dụng Google Gemini cho OCR. Liên hệ admin nếu chưa có.'
            )
    
    def clean_zip_file(self):
        zip_file = self.cleaned_data['zip_file']
        if not zip_file.name.lower().endswith('.zip'):
            raise forms.ValidationError('Vui lòng tải lên file ZIP.')
        if zip_file.size > 100 * 1024 * 1024:  # 100MB
            raise forms.ValidationError('File ZIP quá lớn. Tối đa 100MB.')
        return zip_file
    
    def clean_excel_filename(self):
        excel_filename = self.cleaned_data.get('excel_filename', '').strip()
        if not excel_filename:
            excel_filename = 'ocr_ketqua.xlsx'
            
        if not excel_filename.lower().endswith('.xlsx'):
            excel_filename += '.xlsx'
            
        if len(excel_filename) > 100:
            raise forms.ValidationError('Tên file quá dài. Tối đa 100 ký tự.')
            
        return excel_filename
    
    def clean_api_key(self):
        if 'api_key' not in self.cleaned_data:
            return None
            
        api_key = self.cleaned_data['api_key'].strip()
        if len(api_key) < 10:
            raise forms.ValidationError('API key không hợp lệ.')
        return api_key