from module.imports import *

@dataclass
class ParseResult:
    forms: list = field(default_factory=list)
    standalone_inputs: list = field(default_factory=list)

class HTMLParser:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, 'html.parser')
        self._inputs_in_forms = set()
    
    """ form 태그, input 태그 수집 (다른 태그 있으면 여기에 추가) """
    def parse_all(self) -> ParseResult:
        return ParseResult(
            forms=self.parse_forms(),
            standalone_inputs=self.parse_standalone_inputs()
        )
    
    def parse_forms(self) -> list:
        forms = []
        
        for idx, form in enumerate(self.soup.find_all('form'), 1):
            action = form.get('action', '')
            #form 태그 정보 수집
            form_data = {
                'index': idx,
                'id': form.get('id', ''),
                'action': action if action else(self.soup.base.get('href', '')),
                'method': form.get('method', 'GET').upper(),
                'inputs': []
            }
            
            #form 태그 내 Input 태그 수집
            for inp in form.find_all(['input', 'textarea']):
                self._inputs_in_forms.add(id(inp))
                form_data['inputs'].append({
                    'tag': inp.name,
                    'type': inp.get('type', ''),
                    'name': inp.get('name', ''),
                    'id': inp.get('id', ''),
                    'value': inp.get('value', ''),
                })
            
            #Code Debug
            forms.append(form_data)
            # print(form.prettify())
        return forms
    
    """ form 태그 외부의 Input 태그 수집 """
    def parse_standalone_inputs(self) -> list:
        if not self._inputs_in_forms:
            self.parse_forms()
        
        inputs = []
        for inp in self.soup.find_all(['input', 'textarea']):
            if id(inp) not in self._inputs_in_forms:
                inputs.append({
                    'tag': inp.name,
                    'type': inp.get('type', ''),
                    'name': inp.get('name', ''),
                    'id': inp.get('id', ''),
                    'value': inp.get('value', ''),
                    'parent_tag': inp.parent.name if inp.parent else None
                })
        return inputs

    def parse_script(self) -> list:
        scripts = []

def print_result(result: ParseResult):
    print(f"\n{col.GREEN}{'='*60}{col.END}")
    print(colors(f"Form : {len(result.forms)}개 | Input : {len(result.standalone_inputs)}개 | Script : 0개", "green"))
    print(f"{col.GREEN}{'='*60}{col.END}")
    
    for form in result.forms:
        print(f"\n[Form #{form['index']}] {form['method']} {form['action']}")
        print(f"  ID: {form['id']}")

        #form 태그 정보 출력


        #form 태그 내 Input 태그 정보 출력
        if form['inputs']:
            print(f"  포함된 Input ({len(form['inputs'])}개):")
            for inp in form['inputs']:
                print(f"    └ <{inp['tag']} name='{inp['name']}' type='{inp['type']}' id='{inp['id']}' value='{inp['value']}'>")

    if result.standalone_inputs:
        print(f"\n[Input]")
        for inp in result.standalone_inputs:
            print(f"  └ <{inp['tag']} name='{inp['name']}' type='{inp['type']}' id='{inp['id']}' value='{inp['value']}'>")
            # print(f"  └ <{inp['tag']}> name='{inp['name']}' type='{inp['type']}' id='{inp['id']}' value='{inp['value']}' (부모: {inp['parent_tag']})")
    
    print('='*60)
    ext_save(result)

# 사용
def form_ext2(data: str):
    parser = HTMLParser(data)
    result = parser.parse_all()
    print(result)
    print_result(result)
