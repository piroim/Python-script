from module.imports import *

# class ParseResult:
    

class HTMLParser:
    def __init__(self, url, data):
        self.url = url
        self.data = data
        self.soup = BeautifulSoup(data, 'html.parser')
        self._inputs_in_forms = set() #Input 태그 추출 시 중복 방지를 위해 사용

    def parse_all_elements(self):
        print(f"{colors('[*] 모든 요소 추출 함수 실행', 'green')}")
        forms = self.parser_form()
        inputs = self.parser_inputs()
        
        results = {
            'url': self.url,
            'forms': forms,
            'inputs': inputs
        }
        print("="*60)
        print_result(results)
        save_test(results)

    #form 태그 추출 함수
    def parser_form(self):
        print(f"{colors('[*] form 태그 추출 함수 실행', 'green')}")
        forms = []

        #enumerate는 Index 설정을 위해 사용
        for idx, form in enumerate(self.soup.find_all('form'), 1):
            form_data = {
                'index': idx,
                'id': form.get('id', ''),
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(  ),
                'inputs': [], #아래에 있는 for문에서 inputs 리스트에 추가
                'status_code': None,
                'req_url': urljoin(self.url, form.get('action', ''))
            }
            #form 태그 내 input 태그 추출
            for form_inp in form.find_all(['input']):
                self._inputs_in_forms.add(id(form_inp))
                form_data['inputs'].append({
                    'tag': form_inp.name,
                    'id': form_inp.get('id', ''),
                    'name': form_inp.get('name', ''),
                    'value': form_inp.get('value', ''),
                })
            
            #Request 요청 전송 및 상태코드 반환
            if form_data['method'] == 'POST':
                #POST요청은 데이터가 생성되거나 수정되는 경우가 있기 때문에 요청 전송 X
                #상태코드를 확인할 수 없는데...음 이건 확인 필요
                print(f"POST TEST: {form_data['req_url']}")
                
            elif form_data['method'] == 'GET':
                # print(f"GET TEST: {form_data['req_url']}")
                #[수정필요] 세션의 헤더 값을 너무 많이 업데이트해서, 코드 복잡도 증가
                session = HTTPSession()
                session.headers.update(get_headers())
                session.headers.update({'Cookie': 'PHPSESSID=2m1k4p037ncv91iadrmp1dpro4'})
                get_res = session.get(url=form_data['req_url'], params=form_data['inputs'][0].get('name'), headers=get_headers(), proxies=get_proxy())
                # print(f"[{get_res.status_code}] {self.url} {form_data['inputs'][0].get('name')}")
                form_data['status_code'] = get_res.status_code
                print(f"get_res url : {get_res.url}")
            else:
                print(f"{colors('[*] 메서드 오류', 'red')}")
            # print(f"self._inputs_in_forms: {self._inputs_in_forms}")
            #마지막 단계 forms 리스트에 저장
            forms.append(form_data)

        """
            form 태그는 form_data 리스트에 저장되어 있고,
            form_inp 태그는 form_data['inputs'] 리스트에 저장되어 있음
            -> 출력 및 데이터를 사용할 때는 form 리스트와 form_inp 리스트를 사용
        """
        # save_test(forms)
        return forms

    """ form 태그 외부의 Input 태그 수집 """
    def parser_inputs(self):
        # print(f"{colors('[*] form 태그 외부의 Input 태그 수집 함수 실행', 'green')}")
        if not self._inputs_in_forms:
            self.parser_form()
        inputs = []
        for inp in self.soup.find_all(['input']):
            if id(inp) not in self._inputs_in_forms:
                inputs.append({
                    'tag': inp.name,
                    'id': inp.get('id', ''),
                    'name': inp.get('name', ''),
                    'value': inp.get('value', ''),
                    'req_url': self.url + '?' + inp.get('name', '')
                })
        return inputs

def save_test(results):
    if results['forms']:
        for form in results['forms']:
            print(f"[{form['method']}] {form['req_url']} [{form['status_code']}]")
            with open("ext_form.md", "a", encoding="utf-8") as f:
                f.write(f"[{form['method']}] {form['req_url']} [{form['status_code']}]\n")
    if results['inputs']:
        for input in results['inputs']:
            print(f"[GET] {input['req_url']}")
            with open("ext_form.md", "a", encoding="utf-8") as f:
                f.write(f"[GET] {input['req_url']}\n")

def print_result(results):
    print(f"{colors('='*60, 'green')}")
    print(f"{colors('[*] 결과 출력', 'green')}")
    print(f"{colors('='*60, 'green')}")

    if results['forms']:
        for form in results['forms']:
            print(f"[{form['method']}] {form['req_url']} [{form['status_code']}]")
            for form_inp in form['inputs']:
                print(f" └ <{form_inp['tag']} name='{form_inp['name']}' id='{form_inp['id']}' value='{form_inp['value']}'>")
        
    if results['inputs']:
        for input in results['inputs']:
            print(f"[GET] {input['req_url']}")
            # print(f"<{input['tag']} name='{input['name']}' id='{input['id']}' value='{input['value']}'>")


def form_ext2(url, data):
    parser = HTMLParser(url, data) 
    parser.parse_all_elements()