#=================== 1. ИНИЦИАЛИЗАЦИЯ (GUI + переменные) =================== 
import tkinter as tk
import random
import json
from tkinter.messagebox import showwarning

root = tk.Tk()
root.title("Мой тест на Python — версия 1.0")
root.geometry("600x650")
root.eval('tk::PlaceWindow . center')
root.configure(bg='#f0f4f8')
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

selected_answer = tk.IntVar()
selected_answer.set(-1)

question_number = 0
max_questions = 15

# Списки для хранения состояния
save_radio = []  # Сюда будем класть кнопки, чтобы потом их убирать
save_TF = []     # Сюда пишем True/False для подсчёта

#===================== 2. ЗАГРУЗКА ДАННЫХ ===================== 
try:
    with open('questions.json', 'r', encoding='utf-8') as file:
        questions_data = json.load(file)
except FileNotFoundError:
    showwarning("Ошибка", "Файл questions.json не найден!")
    questions_data = []

# Перемешиваем вопросы один раз при старте
random.shuffle(questions_data)

# Если вопросов меньше, чем хотим показать, уменьшаем лимит
if len(questions_data) < max_questions:
    max_questions = len(questions_data)

if max_questions == 0:
    lbl_error = tk.Label(root, text="Нет вопросов для теста!", font=('Helvetica', 16, 'bold'), bg='#f0f4f8')
    lbl_error.pack(pady=50)
else:
    current_question = questions_data[question_number]
    question_text = current_question['text']
    all_answers = current_question['answers'][:]  # Копия, чтобы не ломать оригинал
    random.shuffle(all_answers)


#=================== 3. СОЗДАНИЕ ИНТЕРФЕЙСА (лейблы) =================== 

# Вывод номера вопроса
lbl_num = tk.Label(
    root, text=f'Вопрос {question_number + 1}',
    font=('Helvetica', 14),
    wraplength=600,
    justify=tk.CENTER,
    bg='#f0f4f8',
    fg='#777777'
)
lbl_num.grid(row=0, column=0, columnspan=2, pady=[50, 10])

# Вывод вопроса
lbl_questions = tk.Label(
    root, text=question_text,
    font=('Helvetica', 16, 'bold'),
    wraplength=600,
    justify=tk.CENTER,
    bg='#f0f4f8'
)
lbl_questions.grid(row=1, column=0, columnspan=2, pady=[0, 50])

# Кнопка «Ответить» (создаём сразу, она не меняется)
btn = tk.Button(root, text='Ответить', command=lambda: check_answer(), padx=20, pady=10)
btn.grid(row=6, column=0, pady=20, columnspan=2)


#================================================= 4. ФУНКЦИИ (логика) ================================================= 

def clear_buttons():
    """Убирает все текущие кнопки с экрана и очищает список ссылок на них."""
    for radio in save_radio:
        radio.grid_forget()  # Скрываем, но не удаляем объект
    save_radio.clear()      # Очищаем список, чтобы старые кнопки не мешали новым


def create_buttons(answers_list):
    """Создаёт ровно столько кнопок, сколько есть ответов в списке."""
    start_row = 2  # Кнопки начинаются со строки 2 (0 — номер, 1 — вопрос)
    
    for idx, ans_data in enumerate(answers_list):
        radio = tk.Radiobutton(
            root,
            text=ans_data['text'],
            value=idx,
            variable=selected_answer,
            indicatoron=0,          # Чтобы кнопка была как плашка, а не кружок
            selectcolor="#2f8acb",
            width=42,
            pady=12,
            relief=tk.FLAT,
            bg='#ffffff'
        )
        radio.grid(row=start_row + idx, column=0, pady=10, columnspan=2)
        save_radio.append(radio)    # Сохраняем ссылку, чтобы потом убрать


def show_question():
    """Обновляет экран под текущий вопрос: текст, кнопки, сброс выбора."""
    global all_answers, question_text
    
    # Готовим ответы: копия + перемешивание
    all_answers = current_question['answers'][:]
    random.shuffle(all_answers)
    question_text = current_question['text']
    
    # Обновляем тексты
    lbl_num.config(text=f'Вопрос {question_number + 1}')
    lbl_questions.config(text=question_text)
    
    # Сначала убираем старые кнопки
    clear_buttons()
    
    # Потом создаём новые — ровно столько, сколько нужно
    create_buttons(all_answers)
    
    # Сбрасываем выбор пользователя
    selected_answer.set(-1)


def result():
    """Считает процент правильных ответов."""
    if len(save_TF) == 0:
        return 0.0
    correct_count = sum(save_TF)
    total_count = len(save_TF)
    return (correct_count / total_count) * 100


def open_warning():
    """Всплывающее окно, если не выбрали ответ."""
    showwarning(title='Предупреждение', message='Выберите вариант ответа')


def check_answer():
    """Проверяет ответ, сохраняет результат и переходит к следующему вопросу."""
    # Проверка: выбрал ли пользователь что-то
    if selected_answer.get() == -1:
        return open_warning()
    
    idx = selected_answer.get()
    chosen_answer = all_answers[idx]
    
    # Записываем результат
    if chosen_answer['is_correct']:
        save_TF.append(True)
    else:
        save_TF.append(False)
    
    next_question()


def next_question():
    """Логика перехода к следующему вопросу или завершения теста."""
    global question_number, current_question
    
    question_number += 1
    
    # Если вопросы кончились — показываем финал
    if question_number >= max_questions:
        lbl_questions.config(
            text=(f'Тест пройден! 🎉\n\nПравильных ответов: {sum(save_TF)} из {len(save_TF)}\n'
                  f'Процент: {result():.1f}%')
        )
        btn.destroy()          # Убираем кнопку «Ответить»
        clear_buttons()        # Убираем кнопки с ответами
        return
    
    # Иначе берём следующий вопрос и показываем его
    current_question = questions_data[question_number]
    show_question()


# Запускаем показ первого вопроса (чтобы кнопки появились сразу при старте)
if max_questions > 0:
    show_question()

root.mainloop()
