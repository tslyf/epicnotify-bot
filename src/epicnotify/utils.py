from typing import Sequence

TIME_INTERVALS = (
    (("год", "года", "лет"), 31557600),
    (("месяц", "месяца", "месяцев"), 2628000),
    (("неделю", "недели", "недель"), 604800),
    (("день", "дня", "дней"), 86400),
    (("час", "часа", "часов"), 60 * 60),
    (("минуту", "минуты", "минут"), 60),
    (("секунду", "секунды", "секунд"), 1),
)


def plural_form(value: int, variants: Sequence[str]):
    variant = 0
    if value % 10 == 1 and value % 100 != 11:
        variant = 0  # *1
    elif value % 10 in range(5, 10) or value % 100 // 10 == 1 or value % 10 == 0:
        variant = 2  # *10, *5, *6, *7, *8, *9, *0
    elif value % 10 in range(2, 5):
        variant = 1  #  *2, *3, *4
    return variants[variant]


def seconds_to_string(seconds: float, length: int = 1) -> str:
    result = []
    for name, count in TIME_INTERVALS:
        value = round(seconds // count)
        if not value:
            continue
        seconds -= value * count
        name = plural_form(value, name)
        result.append(f"{value} {name}")
    ret = " ".join(result[:length])
    return ret if ret else f"0 {TIME_INTERVALS[-1][0][2]}"
