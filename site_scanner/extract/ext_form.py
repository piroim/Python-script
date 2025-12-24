from module.imports import *

class HTMLParser:
    def __init__(self, url, data):
        self.url = url
        self.data = data
        self.soup = BeautifulSoup(data, 'html.parser')
        self._inputs_in_forms = set() #Input 태그 추출 시 중복 방지를 위해 사용

    #form 태그 추출 함수
    def parser_form(self):
        print("form 태그 추출 함수 실행")
        forms = []

        #enumerate는 Index 설정을 위해 사용
        for idx, form in enumerate(self.soup.find_all('form'), 1):
            form_data = {
                'index': idx,
                'id': form.get('id', ''),
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'inputs': [] #아래에 있는 for문에서 inputs 리스트에 추가
            }

            for form_inp in form.find_all(['input']):
                self._inputs_in_forms.add(id(form_inp))
                form_data['inputs'].append({
                    'tag': form_inp.name,
                    'id': form_inp.get('id', ''),
                    'value': form_inp.get('value', ''),
                })
            forms.append(form_data)

        #출력 테스트
        for form in forms:
            print(f"[{form['method']}] {self.url} ")

            for form_inp in form['inputs']:
                print(f" └ <{form_inp['tag']} name='{form_inp['id']}' value='{form_inp['value']}'>")
        """
            form 태그는 form_data 리스트에 저장되어 있고,
            form_inp 태그는 form_data['inputs'] 리스트에 저장되어 있음
            -> 출력 및 데이터를 사용할 때는 form 리스트와 form_inp 리스트를 사용
        """

def form_ext2(url, data):
    parser = HTMLParser(url, data) 
    parser.parser_form()
