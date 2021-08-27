import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validate_submission_syntehsis(code):
    entrada, objetivo, saida = False, False, False

    for item in code.split("\n"):
        if "//" in item:  # avoid variables with same name
            chars = [c for c in list(item) if c is not ' ']
            chars_len = len(chars)

            if "Objetivo" in item and chars_len > 16:
                objetivo = True
            elif "Entrada" in item and chars_len > 13:
                entrada = True
            elif "Saída" in item and chars_len > 11:
                saida = True

            if objetivo and entrada and saida:
                return

    if not (objetivo or entrada or saida):
        raise ValidationError('Você não preencheu a Síntese do seu algoritmo. Por favor, escreva o Objetivo,  '
                              'a Entrada e a Saída.')
    elif not objetivo:
        raise ValidationError('Você não preencheu o Objetivo do seu algoritmo. Por favor, escreva o Objetivo.')
    elif not entrada:
        raise ValidationError('Você não preencheu a Entrada do seu algoritmo. Por favor, escreva a Entrada.')
    elif not saida:
        raise ValidationError('Você não preencheu a Saída do seu algoritmo. Por favor, escreva a Saída.')


def validate_registration_number(registration):
    number = registration.replace('/', '')
    try:
        return int(number)
    except ValueError:
        raise ValidationError("Existe uma matrícula inválida: " + number)


def validate_student_email(email):
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError("Existe um email inválido: " + email)
    return email


def validate_full_name(full_name):
    if any(char.isdigit() for char in full_name):
        raise ValidationError("Existe um nome inválido: " + full_name)
    return full_name


def validate_students(cd, students):
    from django.core.validators import EmailValidator
    EmailValidator(message="Um dos emails é um email inválido.")
    # 0 = registration; 1 = full_name; 2 = email (optional)
    cd['students'] = []
    for s in students:
        student_data = re.split('\s*;\s*', s)
        registration_number = validate_registration_number(student_data[0])
        full_name = validate_full_name(student_data[1])
        if len(student_data) < 3:
            email = str(registration_number) + "@aluno.unb.br"
        elif len(student_data) == 3:
            email = validate_student_email(student_data[2])
        else:
            raise ValidationError('Foram passados mais de 3 argumentos para o aluno ' + full_name)

        cd['students'].append([email, full_name, registration_number])
    print(cd['students'])
    return cd
