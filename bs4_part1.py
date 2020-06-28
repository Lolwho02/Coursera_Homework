from bs4 import BeautifulSoup
import unittest


def parse(path_to_file):
    with open(path_to_file, encoding='utf-8') as f:

        soup = BeautifulSoup(f, 'lxml')
        indiv = soup.find(name='div', id='bodyContent')

        imgs = len((indiv.find_all('img', width=lambda x: int(x or 0) > 199)))

        headers_list = []
        headers = 0
        for i in range(1, 7):
            headers_list.append(indiv.find_all(name='h' + str(i)))
        for i in range(6):
            for tag in headers_list[i]:
                if tag.text[0] in 'ETC':
                    headers += 1


        link_found = indiv.find_next('a')
        linkslen = 0
        while True:
            current = 0
            link_found = link_found.next
            if link_found:
                if link_found.name == 'a':
                    current+=1
                else:
                    current = 0
            else:
                break
            linkslen = max(linkslen, current)

        lists = 0
        ul_ol = indiv.find_all(['ul', 'ol'])
        for html_list in ul_ol:
            if not html_list.find_parents(['ul', 'ol']):
                lists += 1
        print([imgs, headers, linkslen, lists])
        return [imgs, headers, linkslen, lists]


parse('wiki/Spectrogram')