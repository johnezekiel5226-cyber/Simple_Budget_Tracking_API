from .views import ExportCSVView, ExportPDFView

urlpatterns = [
    path('', include(router.urls)),
    path('metrics/', MetricsView.as_view()),

    # Export endpoints
    path('export/csv/', ExportCSVView.as_view(), name='export-csv'),
    path('export/pdf/', ExportPDFView.as_view(), name='export-pdf'),

    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
]
