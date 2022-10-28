import logging
from dynaconf.utils.boxing import DynaBox

from application.core.config import settings
from application.core.helpers import load_module


def update_scheduler_jobs(scheduler):
    """
    Добавляет или модифицирует задания для APScheduler по настройкам в конфигурационном файле
    """
    # Получим список заданий из конфига модуля
    tasks: DynaBox = settings.get("scheduler.tasks")
    if not tasks:
        logging.debug(f"В настройках нет ветки 'scheduler.tasks' c заданиями для планировщика")
        return

    # Пробежимся по заданиям и добавим/модифицируем их в scheduler
    for _task in tasks:
        # Сделаем копию задания, чтобы не повредить глобальный конфиг и выделим из него параметры триггера
        task: DynaBox = _task.copy()
        trigger_args: DynaBox = task.pop("trigger_args")

        # Если задание с таким id уже существует, то обновим его триггер
        if scheduler.get_job(task.id, jobstore=task.jobstore):
            scheduler.reschedule_job(task.id, trigger=task.trigger, jobstore=task.jobstore, **trigger_args)
            logging.debug(f"Обновлено задание планировщика: {task.id}, триггер {task.trigger}, {trigger_args}")
            continue
        # Или просто добавим его в планировщик
        scheduler.add_job(**task, **trigger_args)
        logging.debug(f"Добавлено задание планировщика: {task.id}, триггер {task.trigger}, {trigger_args}")


def run_scheduler():
    """
    Создает планировщик и добавляет в него задания из конфигурационных файлов

    Returns:
        Сокет: Его можно сохранить, чтобы ограничить запуск планировщика в нескольких потоках

    """
    scheduler_properties: DynaBox = settings.get("SCHEDULER")
    if not scheduler_properties:
        logging.warning("SCHEDULER property is not set. Scheduler won't be instantiated")
        return None

    # Создадим экземпляр планировщика
    scheduler = load_module(
        scheduler_properties.get("package", "apscheduler.schedulers.background"),
        scheduler_properties.get("type", "BackgroundScheduler"),
        scheduler_properties.get("args", ()),
        scheduler_properties.get("kwargs", {}),
    )

    # Обновим задания и запустим планировщик
    if scheduler:
        update_scheduler_jobs(scheduler)
        scheduler.start()

    return scheduler
