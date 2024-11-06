TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ... other context processors ...
                'hospital.context_processors.notification_count',
            ],
        },
    },
] 