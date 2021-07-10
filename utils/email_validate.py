from validate_email import validate_email


def check_validate_email(email):
    return validate_email(email, check_mx=True, verify=True)


check_email = check_validate_email('test@yandex.ru')

if check_email:
    print('Почта существует!')
else:
    print('Почта не существует!')
