import re
from models import Lesson

def out(res):
    return (res.stdout or "")

def check_contains(text: str):
    return lambda res: text in out(res)

def check_last_line_equals(expected: str):
    def _fn(res):
        lines = [ln.strip() for ln in out(res).splitlines() if ln.strip() != ""]
        return bool(lines) and lines[-1] == expected
    return _fn

LESSONS = [
    Lesson(
        id="u1_01", unit=1, order=1, title="print",
        goal="Merhaba Deniz yazdır.",
        hint="print('...')",
        expected="Merhaba Deniz",
        starter_code="print('Merhaba Deniz')\n",
        expected_output_example="Merhaba Deniz\n",
        intro="print() ekrana yazı yazdırır. Programın çıktısını görmek için kullanırsın.",
        example="print('Merhaba')",
        quiz={"q":"print() ne yapar?","choices":["Ekrana yazdırır","Değişken oluşturur","Dosya siler"],"answer":0,"explain":"print() konsola/ekrana metin basar."},
        checks=[("Merhaba Deniz", check_contains("Merhaba Deniz"))],
    ),
    Lesson(
        id="u1_02", unit=1, order=2, title="değişken",
        goal="name='Deniz' yazdır.",
        hint="name='Deniz' sonra print(name)",
        expected="Deniz",
        starter_code="name='Deniz'\nprint(name)\n",
        expected_output_example="Deniz\n",
        intro="Değişken, bir değeri isimle saklamaktır.",
        example="x = 5\nprint(x)",
        quiz={"q":"name='Deniz' satırı ne yapar?","choices":["name değişkenine 'Deniz' atar","Ekrana Deniz yazar","Dosya açar"],"answer":0,"explain":"Bu satır atama yapar, ekrana yazdırmaz."},
        checks=[("Son satır Deniz", check_last_line_equals("Deniz"))],
    ),
    Lesson(
        id="u3_01", unit=3, order=1, title="if",
        goal="x=10 iken 'Büyük' yazdır.",
        hint="if x>5: print('Büyük')",
        expected="Büyük",
        starter_code="x=10\n# buraya yaz\n",
        expected_output_example="Büyük\n",
        intro="if koşulu doğruysa bir kod bloğunu çalıştırır.",
        example="x=3\nif x>2:\n    print('ok')",
        quiz={"q":"if ne zaman çalışır?","choices":["Koşul True ise","Her zaman","Koşul False ise"],"answer":0,"explain":"Koşul True olunca iç blok çalışır."},
        checks=[("Büyük", check_contains("Büyük"))],
    ),
]
