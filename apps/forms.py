from django import forms

class UploadZipForm(forms.Form):
    zip_file = forms.FileField(label='Tải lên file ZIP chứa ảnh bảng điểm')
    excel_filename = forms.CharField(label='Tên file Excel (ví dụ: bang_diem.xlsx)', max_length=100, required=False)
    #search_subject = forms.CharField(label='Tìm kiếm tên học phần', max_length=100, required=False)
    #search_major = forms.CharField(label='Tìm kiếm ngành học', max_length=100, required=False)