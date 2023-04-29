from django.test import TestCase


#teste de codificação
import codecs

filename = '2642 BRADESCO 15062022(Bloqueado).csv'
encodings = ['utf-8', 'iso-8859-1', 'windows-1252']

for encoding in encodings:
    try:
        with codecs.open(filename, 'r', encoding=encoding) as f:
            f.read()
        print(f'O arquivo está codificado em {encoding}.')
        break
    except UnicodeDecodeError:
        print(f'A codificação {encoding} não funciona.')
