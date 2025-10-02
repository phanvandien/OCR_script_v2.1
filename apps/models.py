# from django.db import models

# class Result(models.Model):
#     sbd = models.CharField(max_length=10, blank=True)
#     ho_ten = models.CharField(max_length=100, blank=True)
#     diem = models.FloatField(default=0.0)
#     image = models.ImageField(upload_to='ocr_sessions/', null=True, blank=True)
#     is_viewed = models.BooleanField(default=False)
#     session_id = models.CharField(max_length=36, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.sbd} - {self.ho_ten}"