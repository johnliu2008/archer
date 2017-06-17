# -*- coding: UTF-8 -*- 
from django.db import models
from django.contrib.auth.models import AbstractUser
from .aes_decryptor import Prpcrypt

# Create your models here.

#角色分两种：
#1.工程师：可以提交SQL上线单的工程师们，username字段为登录用户名，display字段为展示的中文名。
#2.审核人：可以审核并执行SQL上线单的管理者、高级工程师、系统管理员们。
class users(AbstractUser):
    display = models.CharField('显示的中文名', max_length=50)
    role = models.CharField('角色', max_length=20, choices=(('工程师','工程师'),('审核人','审核人')), default='工程师')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = u'用户配置'
        verbose_name_plural = u'用户配置'

#各个线上主库地址。
class master_config(models.Model):
    cluster_name = models.CharField('集群名称', max_length=50)
    master_host = models.CharField('主库地址', max_length=200)
    master_port = models.IntegerField('主库端口', default=3306)
    master_user = models.CharField('登录主库的用户名', max_length=100)
    master_password = models.CharField('登录主库的密码', max_length=300)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.cluster_name
    class Meta:
        verbose_name = u'主库地址'
        verbose_name_plural = u'主库地址'

    def save(self, *args, **kwargs):
        pc = Prpcrypt() #初始化
        self.master_password = pc.encrypt(self.master_password)
        super(master_config, self).save(*args, **kwargs)


#存放各个SQL上线工单的详细内容，可定期归档或清理历史数据，也可通过alter table workflow row_format=compressed; 来进行压缩
class workflow(models.Model):
    workflow_name = models.CharField('工单内容', max_length=50)
    engineer = models.CharField('发起人', max_length=50)
    review_man = models.CharField('审核人', max_length=50)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    finish_time = models.DateTimeField('结束时间', null=True, blank=True)
    status = models.CharField(max_length=50, choices=(('已正常结束','已正常结束'),('人工终止流程','人工终止流程'),('自动审核中','自动审核中'),('等待审核人审核','等待审核人审核'),('执行中','执行中'),('自动审核不通过','自动审核不通过'),('执行有异常','执行有异常')))
    #is_backup = models.IntegerField('是否备份，0为否，1为是', choices=((0,0),(1,1)))
    is_backup = models.CharField('是否备份', choices=(('否','否'),('是','是')), max_length=20)
    review_content = models.TextField('自动审核内容的JSON格式')
    cluster_name = models.CharField('集群名称', max_length=50)     #master_config表的cluster_name列的外键
    reviewok_time = models.DateTimeField('人工审核通过的时间', null=True, blank=True)
    sql_content = models.TextField('具体sql内容')
    execute_result = models.TextField('执行结果的JSON格式')

    def __str__(self):
        return self.workflow_name
    class Meta:
        verbose_name = u'工单管理'
        verbose_name_plural = u'工单管理'


#存放备份结果
class backup_result(models.Model):
    hostname = models.CharField('主机名或IP地址', max_length=70)
    port = models.IntegerField('端口号')
    dbname = models.CharField('库名', max_length=60)
    backup_tool = models.CharField('备份工具，如Xtrabackup, mysqldump，RMAN等', max_length=30)
    backup_strategy = models.CharField('备份策略', max_length=12, choices=(('完全备份', '完全备份'),('增量备份', '增量备份')))
    backup_result = models.CharField('备份结果', max_length=10, choices=(('成功', '成功'),('失败', '失败')))
    start_time = models.DateTimeField('备份开始时间')
    finish_time = models.DateTimeField('备份结束时间', null=True, blank=True)
    duration = models.CharField('备份耗时', max_length=10, default="N/A")
    input_size = models.CharField('输入大小，即数据库大小，单位不限', max_length=20)
    output_size = models.CharField('输出大小，即备份集大小，单位不限', max_length=20)
    comments = models.CharField('备注', max_length=500)

    def __str__(self):
        return self.hostname + '_' + str(self.port)
    class Meta:
        verbose_name = u'备份结果'
        verbose_name_plural = u'备份结果'