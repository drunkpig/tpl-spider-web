from django.db import models

# Create your models here.


class SpiderTask(models.Model):

    """

    """
    id = models.AutoField(primary_key=True)
    seeds = models.TextField(help_text="url种子")
    ip = models.TextField(help_text="用户的ip")
    user_id_str = models.TextField(max_length=128)
    user_agent = models.TextField(max_length=256, default='pc')
    encoding = models.CharField(max_length=16, default='utf-8')
    status = models.CharField(help_text='状态：I:插进来，P：处理中', max_length=1, default='I')
    is_grab_out_link = models.BooleanField(default=False)
    result = models.TextField(max_length=128)
    gmt_modified = models.DateTimeField(auto_now=True)
    gmt_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        db_table = 'spider_task'
