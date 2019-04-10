import uuid

from django.db import models

# Create your models here.


class SpiderTask(models.Model):

    """

    """
    id = models.AutoField(primary_key=True)
    seeds = models.TextField(help_text="url种子")
    ip = models.TextField(help_text="用户的ip")
    email = models.EmailField(max_length=128)
    user_agent = models.TextField(max_length=256, default='pc')
    encoding = models.CharField(max_length=16, default='utf-8')
    status = models.CharField(help_text='状态：I:插进来，P：处理中', max_length=1, default='I')
    is_grab_out_link = models.BooleanField(default=False) # 是否抓外链
    is_to_single_page = models.BooleanField(default=False) # 是否压缩成单页面
    is_full_site = models.BooleanField(default=False) # 是否全站抓取
    is_ref_model = models.BooleanField(default=False) # 是否盗链模式
    to_framework = models.CharField(max_length=16, default='utf-8')  # 转化为哪种web框架的模版
    file_id = models.UUIDField(default=uuid.uuid4, editable=False)
    result = models.TextField(max_length=128, null=True)
    error = models.TextField(max_length=256, null=True)
    gmt_modified = models.DateTimeField(auto_now=True)
    gmt_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'spider_task'
