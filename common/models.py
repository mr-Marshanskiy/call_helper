from django.db import models


class ExampleFirstModel(models.Model):
    char_field = models.CharField('Char field', max_length=255)
    text_field = models.TextField('Text field'),

    small_int_field = models.SmallIntegerField('Integer field'),
    int_field = models.IntegerField('Integer field'),
    big_int_field = models.BigIntegerField('Integer field'),

    positive_small_int_field = models.PositiveSmallIntegerField('Integer')
    positive_int_field = models.PositiveIntegerField('Integer field'),
    positive_big_int_field = models.PositiveBigIntegerField('Integer field'),