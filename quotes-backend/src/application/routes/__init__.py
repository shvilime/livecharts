# Словарик, для хранения начальных цен и подсчета изменений
PRICES: dict = dict.fromkeys([f"ticker_{str(i).zfill(2)}" for i in range(0, 100)], 0)
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
