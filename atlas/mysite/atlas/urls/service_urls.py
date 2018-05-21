"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url
from atlas import views
from atlas import summary, analysis, clustering


urlpatterns = [
    url(r'^product/$', views.searchQuery),
    url(r'^product/add$', views.addProduct),
    url(r'^product/(\w+\s*\w*)/refresh$', views.refreshProduct),
    url(r'^request/$', views.getRequests),
    url(r'^product_list/$', views.getAutoCompleteList),
    url(r'^upload/$', views.uploadFile),
    url(r'^start/$', views.start_analysis),
    url(r'^readdims/$', views.read_dims),

    url(r'^summary_countRevCards/$', summary.getCountRevCardsData),
    url(r'^summary_countRevCardsOverall/$', summary.getCountRevCardsOverallData),
    url(r'^summary_topposneg/$', summary.getTopposnegData),
    url(r'^summary_topposnegOverall/$', summary.getTopposnegOverallData),
    url(r'^summary_brand1/$', summary.getBrandFilter),
    url(r'^summary_source1/$', summary.getSourceFilter),
    url(r'^summary_source1_revmap/$', summary.getSourceRevmap),  # source reverse mapping to get siteCode from siteName
    url(r'^summary_sku1/$', summary.getSkuFilter),
    url(r'^summary_chart1/$', summary.getChart1Data),
    url(r'^summary_common_reviewcount_chart/$', summary.getCommonReviewCountChartData),
    #url(r'^summary_chart2/$', summary.getChart2Data),
    url(r'^summary_chart3/$', summary.getChart3Data),
    url(r'^summary_piechart/$', summary.getPieChartData),
    url(r'^analysis_brand1/$', analysis.getBrandFilter),
    url(r'^analysis_source1/$', analysis.getSourceFilter),
    url(r'^analysis_sku1/$', analysis.getSkuFilter),
    url(r'^analysis_brandsummary_chart/$', analysis.getBrandSummaryChartData),
    url(r'^analysis_chart1/$', analysis.getChart1Data),
    url(r'^analysis_chart2/$', analysis.getChart2Data),
    url(r'^analysis_chart3/$', analysis.getChart3Data),
    url(r'^analysis_common_trig_chart/$', analysis.getCommonTrigChartData),
    url(r'^analysis_chart4/$', analysis.getChart4Data),
    url(r'^analysis_common_driv_chart/$', analysis.getCommonDrivChartData),
    url(r'^analysis_common_senti_chart/$', analysis.getCommonSentiChartData),
    #    url(r'^carrot_clustering/$', clustering.getData),
    url(r'^pivotparser/$', summary.getPivotdata),
    url(r'^assoc_dims/$', summary.getAssocDims),
    url(r'^assoc_levels/$', summary.getAssocLevels),
    url(r'^association/$', summary.getAssociationMapdata),
]

