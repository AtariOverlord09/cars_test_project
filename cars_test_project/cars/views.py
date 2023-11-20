import logging
import requests
from threading import Thread, Lock
import xml.etree.ElementTree as ET

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.db import transaction

from .forms import MarkForm
from .models import Mark, Model

logger = logging.getLogger(__name__)
update_lock = Lock()


def index(request):
    form = MarkForm()
    template = 'cars/index.html'

    if request.method == 'POST':
        form = MarkForm(request.POST)
        if form.is_valid():
            selected_mark = form.cleaned_data['mark']
            models = Model.objects.filter(mark=selected_mark)
            return render(request, template, {'form': form, 'models': models})

    return render(request, template, {'form': form})


def update_catalog_task():
    try:
        with update_lock:
            logger.info("Запуск обновления каталога.")

            with transaction.atomic():
                Mark.objects.all().delete()
                Model.objects.all().delete()

                url = 'https://auto-export.s3.yandex.net/auto/price-list/catalog/cars.xml'

                response = requests.get(url)
                root = ET.fromstring(response.content)

                for mark_element in root.findall('.//mark'):
                    mark_name = mark_element.get('name').strip()
                    mark_instance = Mark.objects.create(name=mark_name)

                    for folder_element in mark_element.findall('.//folder'):
                        model_name = folder_element.get('name').split(',')[0].strip()
                        Model.objects.get_or_create(
                            mark=mark_instance,
                            name=model_name,
                        )

            logger.info("Каталог успешно обновлен.")
    except Exception as error:
        logger.error(f"Ошибка обновления каталога: {str(error)}")


@csrf_exempt
def update_catalog(request):
    # Отправляем мгновенный ответ пользователю
    response = HttpResponse("Обновление каталога...")

    # Пытаемся захватить блокировку, если не удается, возвращаем сообщение об уже запущенном обновлении
    if not update_lock.acquire(blocking=False):
        response.status_code = 409
        response.content = "Обновление каталога уже запущено."
        return response

    # Запускаем обновление каталога в отдельном потоке
    update_thread = Thread(target=update_catalog_task)
    update_thread.start()

    # Освобождаем блокировку
    update_lock.release()

    return response
