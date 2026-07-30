from pathlib import Path
from html.parser import HTMLParser

void_elements = set(
    [
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'
    ]
)

class PrettyHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.lines = []
        self.indent = 0
        self.last_output = ''
        self.preserve = False
        self.preserve_tag = None

    def _newline(self):
        if self.last_output.endswith('\n'):
            return
        self.lines.append('\n')
        self.last_output = '\n'

    def _indent(self):
        if self.last_output.endswith('\n'):
            indent_str = '  ' * self.indent
            self.lines.append(indent_str)
            self.last_output = indent_str

    def handle_decl(self, decl):
        self._newline()
        self.lines.append(f'<!{decl}>')
        self.last_output = self.lines[-1]

    def handle_starttag(self, tag, attrs):
        self._newline()
        self._indent()
        attr_str = ''.join(
            f' {name}' + (f'="{value}"' if value is not None else '')
            for name, value in attrs
        )
        self.lines.append(f'<{tag}{attr_str}>')
        self.last_output = self.lines[-1]
        if tag not in void_elements:
            if tag in ('script', 'style'):
                self.preserve = True
                self.preserve_tag = tag
                self.indent += 1
                self._newline()
            else:
                self.indent += 1

    def handle_startendtag(self, tag, attrs):
        self._newline()
        self._indent()
        attr_str = ''.join(
            f' {name}' + (f'="{value}"' if value is not None else '')
            for name, value in attrs
        )
        self.lines.append(f'<{tag}{attr_str}>')
        self.last_output = self.lines[-1]

    def handle_endtag(self, tag):
        if tag in void_elements:
            return
        if tag in ('script', 'style'):
            self.preserve = False
            self.preserve_tag = None
            self.indent = max(self.indent - 1, 0)
            self._newline()
            self._indent()
            self.lines.append(f'</{tag}>')
            self.last_output = self.lines[-1]
        else:
            self.indent = max(self.indent - 1, 0)
            self._newline()
            self._indent()
            self.lines.append(f'</{tag}>')
            self.last_output = self.lines[-1]

    def handle_data(self, data):
        if not data:
            return
        if self.preserve:
            self.lines.append(data)
            self.last_output = data[-1] if data else self.last_output
            return
        text = data.strip()
        if not text:
            return
        self._newline()
        self._indent()
        self.lines.append(text)
        self.last_output = text

    def handle_comment(self, data):
        self._newline()
        self._indent()
        self.lines.append(f'<!--{data}-->')
        self.last_output = self.lines[-1]

    def handle_entityref(self, name):
        self.lines.append(f'&{name};')
        self.last_output = self.lines[-1]

    def handle_charref(self, name):
        self.lines.append(f'&#{name};')
        self.last_output = self.lines[-1]

    def handle_pi(self, data):
        self._newline()
        self._indent()
        self.lines.append(f'<?{data}>')
        self.last_output = self.lines[-1]


if __name__ == '__main__':
    path = Path('index.html')
    text = path.read_text(encoding='utf-8')
    parser = PrettyHTML()
    parser.feed(text)
    output = ''.join(parser.lines).lstrip('\n') + '\n'
    Path('index.formatted.html').write_text(output, encoding='utf-8')
    print('written', len(output), 'bytes')
