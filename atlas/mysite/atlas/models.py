from __future__ import unicode_literals
from django.db import models
from django_unixdatetimefield import UnixDateTimeField


class Meta:
    app_label = 'atlas'


# Create your models here.
class Product(models.Model):
    pid = models.CharField(max_length=100, primary_key=True)
    pCategory = models.CharField(max_length=30)
    pBrand = models.CharField(max_length=30)
    pDescr = models.TextField()
    pRating = models.DecimalField(max_digits=2, decimal_places=1)
    pImgSrc = models.TextField()
    pModel = models.CharField(max_length=30)
    pTitle = models.TextField()
    pURL = models.TextField()
    pPrice = models.CharField(max_length=10)
    siteCode = models.CharField(max_length=2)

    def __unicode__(self):
        return unicode(self.pTitle)


class Review(models.Model):
    rid = models.CharField(max_length=100, primary_key=True)
    pid = models.ForeignKey(Product, on_delete=models.CASCADE)
    rDate = UnixDateTimeField()
    rDate2 = models.DateField(null=True, blank=True)
    rRating = models.DecimalField(max_digits=2, decimal_places=1)
    rText = models.TextField()
    rTitle = models.TextField()
    rURL = models.TextField()
    rUser = models.CharField(max_length=30)

    def __unicode__(self):
        return unicode(self.rTitle)


class Analysis(models.Model):
    rid = models.ForeignKey(Review, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    sentiScore = models.DecimalField(max_digits=4, decimal_places=2,null=True, blank=True)
    trigger = models.CharField(max_length=200,null=True, blank=True)
    driver = models.CharField(max_length=200,null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)


class Uploads(models.Model):
    rid = models.CharField(max_length=100, primary_key=True)
    rDate = UnixDateTimeField(null=True, blank=True)
    rDate2 = models.DateField(null=True, blank=True)
    rRating = models.DecimalField(max_digits=2, decimal_places=1,null=True, blank=True)
    rText = models.TextField()
    rTitle = models.TextField(null=True, blank=True)
    rURL = models.TextField(null=True, blank=True)
    rUser = models.CharField(max_length=30,null=True, blank=True)
    pCategory = models.CharField(max_length=30,null=True, blank=True)

    def __unicode__(self):
        return unicode(self.rTitle)


class UploadAnalyses(models.Model):
    rid = models.ForeignKey(Uploads, on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    sentiScore = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    trigger = models.CharField(max_length=200, null=True, blank=True)
    driver = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.id)