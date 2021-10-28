# users/views.py
from django.views.generic.edit import CreateView
# Функция reverse_lazy позволяет получить URL по параметрам функции path()
from django.urls import reverse_lazy
from .forms import CreationForm


# Для обработки формы CreationForm возьмём дженерик CreateView, он
# обрабатывает формы и на основе полученных из формы данных создаёт
# новые записи в БД.
class SignUp(CreateView):  # Создаём свой класс, наследуем его от CreateView
    # C какой формой будет работать этот view-класс
    form_class = CreationForm

    # Какой шаблон применить для отображения веб-формы
    template_name = 'users/signup.html'

    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')
