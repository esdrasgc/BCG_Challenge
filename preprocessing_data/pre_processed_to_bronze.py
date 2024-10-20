import re
from pathlib import Path

## For the next step, meaningless strings from the documents will be removed, below a list of them for each doc
strings_to_remove = {
    'agro' : None,
    'curitiba' : None,
    'enfrentamento' : None,
    'federal' : None,
    'itabirito' : None,

    'joao_pessoa' : ["""AOSSEP
OÃOJ
ED
ACITÁMILC
OÃÇA
ED
ONALP""",
"""AOSSEP
OÃOJ
ED ACITÁMILC
OÃÇA ED
ONALP"""],

    'nacional' : None,

    'sao_paulo' : ['PARTE I - O PLANEJAMENTO DA ADAPTAÇÃO E DA RESILIÊNCIA',
                               'PARTE II – CICLO DE ELABORAÇÃO DO PLANO',
"""seõiger
e
soipícinum
arap
acitámilc
aicnêiliser
e
oãçatpada
ed
aiuG"""],

}

data_path = Path().cwd().parent / 'data'

input_txt_processed_dir = data_path / 'pre-processed'
output_bronze_dir = data_path / 'bronze'

output_bronze_dir.mkdir(parents=True, exist_ok=True)


for name, info in strings_to_remove.items():
    output_text_path = output_bronze_dir / f'{name}.txt'
    ## read the text from the file
    text = (input_txt_processed_dir / (name + '.txt')).read_text(encoding='utf-8')
    ## remove the strings
    if info is not None:
        for string in info:
            text = text.replace(string, '')

    ## remove the '--- Page X ---' strings
    text = '\n'.join([line for line in text.split('\n') if not '--- Page' in line])

    ## substitute the r'\n+' for '\n'
    text = re.sub(r'\n+', '\n', text)

    ## write the text to the output file
    output_text_path.write_text(text, encoding='utf-8')
