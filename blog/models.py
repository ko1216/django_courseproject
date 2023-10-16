from django.db import models


NULLABLE = {'blank': True, 'null': True}


class Blog(models.Model):
    title = models.CharField(max_length=150, verbose_name='Заголовок')
    slug = models.CharField(max_length=150, verbose_name='slug')
    text = models.TextField(**NULLABLE, verbose_name='Содержимое')
    preview = models.ImageField(**NULLABLE, upload_to='preview', verbose_name='Изображение')
    created_at = models.DateTimeField(**NULLABLE, auto_now=True, verbose_name='Создано')
    last_update = models.DateTimeField(**NULLABLE, auto_now_add=True, verbose_name='Last Update')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    views_count = models.IntegerField(default=0, verbose_name='Просмотры')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
