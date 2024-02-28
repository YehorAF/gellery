### Photosite

Завантажено лише додатки, які використовує даний проект, а саме: gallery

Для того щоб використовувати дані додатки, необхідно додати у файл urls.py Вашого проекту наступне:

```
from django.urls import path, include


urlpatterns = [
    path("", include("gallery.urls"))
]
```

Також необхідно створити теку user-files у батьківській теці.
