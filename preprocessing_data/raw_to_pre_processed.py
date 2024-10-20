import pdfplumber
from pathlib import Path


metadata_pdfs = {
    'nacional': {'filename': "plano-acao-adaptacao-climatica-nacional.pdf", 'start_page' : 6, 'line_number' : None, 'skip_lines' : 1},
    'agro': {'filename' : "plano-acao-climatica-agro.pdf", 'start_page' : 20, 'skip_lines' : 1},
    'curitiba' : {'filename' : 'plano-acao-climatica-curitiba.pdf', "start_page" : 16},
    'federal' : {'filename': 'plano-acao-climatica-federal.pdf', 'start_page' : 31},
    'itabirito' : {'filename' : 'plano-acao-climatica-itabirito.pdf', "start_page" : 19},
    'joao_pessoa' : {'filename' : "plano-acao-climatica-joao-pessoa.pdf", "start_page" : 14},
    'sao_paulo' : {'filename' : "plano-acao-climatica-sp-regiao.pdf", "start_page" : 11}, 
    'enfrentamento' : {'filename' : 'plano-enfrentamento-mudanca-climatica-nacional.pdf', "start_page" : 1} 
}

def extract_text_from_pdf(pdf_path: Path, output_txt_path: Path, start_page : int = 1, has_line_number : bool = False, skip_lines : int = 0):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page_number, page in enumerate(pdf.pages[start_page-1:], start=1):
                # Extract text from the current page
                text = page.extract_text()
                if text:
                    # Optionally, add page breaks or headers
                    full_text += f"\n\n--- Page {page_number} ---\n\n"
                    if has_line_number:
                        text = '\n'.join([' '.join(line.split(' ')[1:]) for line in text.split('\n')[skip_lines:]])
                    elif skip_lines != 0:
                        text = '\n'.join(text.split('\n')[skip_lines:])

                    # remove last line from each page (contains the page number)
                    full_text += '\n'.join(text.split('\n')[:-1])
            # Write the extracted text to the output file
            output_txt_path.write_text(full_text, encoding='utf-8')
        print(f"Text successfully extracted to {output_txt_path}")
    except Exception as e:
        print(f"An error occurred while processing {pdf_path.name}: {e}")

data_path = Path().cwd().parent / 'data'
input_pdf_directory = data_path / 'raw'
output_text_directory = data_path / 'pre-processed'

output_text_directory.mkdir(parents=True, exist_ok=True)

for name, metadata in metadata_pdfs.items():
    txt_filename = name + '.txt'
    output_txt_path = output_text_directory / txt_filename
    extract_text_from_pdf(input_pdf_directory / metadata['filename'], output_txt_path, start_page = metadata['start_page'],has_line_number= 'line_number' in metadata, skip_lines= metadata['skip_lines'] if 'skip_lines' in metadata else 0)
