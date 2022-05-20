from prettytable import PrettyTable

from bot.repository.TaskRepository import TaskRepository
from bot.repository.UserRepository import UserRepository
from bot.model.Submit import Submit
from bot.teletrik.DI import repository


@repository
class SubmitRepository:

    def __init__(self, task_repository: TaskRepository, user_repository: UserRepository):
        Submit.create_table()
        self.task_repository: TaskRepository = task_repository
        self.user_repository: UserRepository = user_repository

    async def create_submit(self, submit_id: str, student_id: str, task_name: str) -> None:
        Submit.create(submit_id=submit_id, student_id=student_id, task_name=task_name, result="?")

    async def update_submit_result(self, submit_id: str, result: str) -> None:
        submit = Submit.get(Submit.submit_id == submit_id)
        submit.result = result
        submit.save()

    async def get_all_results(self) -> list[Submit]:
        return Submit.select()

    async def get_student_submits(self, student_id: str) -> list[Submit]:
        return Submit.select().where(Submit.student_id == student_id)

    async def get_student_submits_by_task(self, student_id: str, task_name: str) -> list[Submit]:
        return Submit.select().where((Submit.student_id == student_id) & (Submit.task_name == task_name))

    async def get_student_result(self, student_id: str) -> dict[str, str]:
        results = {}

        for task in sorted(self.task_repository.get_tasks()):
            results[task] = "undef"

        for task in sorted(self.task_repository.get_tasks()):
            student_result = await self.get_student_submits_by_task(student_id, task)
            status = ""
            cnt = str(len(student_result))
            hasv = False
            for submit in student_result:

                match submit.result:
                    case "+":
                        if status in ["", "-", "?"]:
                            status = "+"

                    case "-":
                        if status in ["?", ""]:
                            status = "-"

                    case "?":
                        hasv = True

            if hasv and status in ["-", ""]:
                status = "?"
            results[task] = status + cnt

        return results

    async def get_student_submits_view(self, student_id: str, task_name: str) -> PrettyTable:
        results = await self.get_student_submits_by_task(student_id, task_name)
        table = PrettyTable()

        table.field_names = ["Id посылки", "Результат"]
        for result in results:
            table.add_row([result.submit_id, result.result])

        return table

    async def get_all_results_view(self):

        def get_class_name(s):
            match s:
                case "+":
                    return "accepted"
                case "-":
                    return "failed"
                case "?":
                    return "unknown"
                case "0":
                    return "none"

        top = \
            """
            <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Статистика</title>
    <style>
        header {
            padding: 0;
            margin: 0;
            display: block;
        }
        body {
            margin-top: 0;
            font-family: monospace, sans-serif;
            font-size: 120%;
        }
        .header-img {
            margin-top: 0;
            position: relative;
            text-align: center;
            vertical-align: top;
        }
        table {
            width: 100%;
            text-align: justify;
            border-spacing: 0;
        }
        .even {
            background: #e9f2fa;
        }
        .odd {
            background: #FFFFFF;
        }
        .accepted {
            color: #009933;
        }
        .failed {
            color: red;
        }
    </style>
</head>
<body>
<header>
    <div class="header-img">
        <img src="https://dl.trikset.com/logos/trik/trik_logo_eng_slogan_ru_big_green.png" alt="" width="35%">
    </div>
</header>
            """

        table = "<table>"

        table += "<thead><tr> "
        table += "<th>Ученики</th>"
        for task_name in sorted(self.task_repository.get_tasks().keys()):
            table += f"<th>{task_name}</th>"
        table += "</tr></thead>"

        cnt = 0
        for student in self.user_repository.get_all_students():
            table += f"<tr class=\"{'even' if cnt % 2 == 0 else 'odd'}\">"
            table += f"<td>{student}</td>"
            student_result = await self.get_student_result(student)

            for result in sorted(student_result.keys()):
                symbol = student_result[result][0]
                class_name = get_class_name(symbol)
                table += f"<td class=\"{class_name}\">{student_result[result]}</td>"
            table += "</tr>"
            cnt += 1

        table += "</table>"

        bottom = "</body></html>"
        return top + table + bottom

    async def get_task_stat_view(self, task_name):

        stat = f"Задача: {task_name}: \n"
        correct_cnt = len(list(Submit.select().where((Submit.task_name == task_name) & (Submit.result == "+"))))
        incorrect_cnt = len(list(Submit.select().where((Submit.task_name == task_name) & (Submit.result == "-"))))
        on_review_cnt = len(list(Submit.select().where((Submit.task_name == task_name) & (Submit.result == "?"))))
        stat += f"Посылок: Правильных {correct_cnt} | Неправильных {incorrect_cnt} | На проверке {on_review_cnt} \n"
        return stat

    async def get_stat_view(self):
        stat = ""
        stat += f"Учеников: {len(self.user_repository.get_all_students())} \n"
        stat += f"Всего попыток: {len(await self.get_all_results())} \n"

        for task_name in sorted(self.task_repository.get_tasks().keys()):
            stat += await self.get_task_stat_view(task_name)

        return stat
