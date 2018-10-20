import requests
from bs4 import BeautifulSoup
import json

domain = ''

# tikubh = [
#     1436,
#     1467,
#     1471,
#     1484,
#     1485,
#     1486,
#     4199,
#     4200,
#     6422,
#     21675
# ]
#
#
# req_sess = requests.session()
#
#
# for tkbh in tikubh:
#     res = req_sess.get('http://{}/redir.php?catalog_id=6&cmd=testing&tikubh={}'.format(domain, tkbh))
#     res.encoding = 'gbk'
#     # print(res.text)
#
#     # 提交答卷
#     res = req_sess.post('http://' + domain + '/redir.php?catalog_id=6&cmd=dati&mode=test', {
#         'runpage': '0',
#         'page': '0',
#         'direction': '',
#         'tijiao': '1',
#         'postflag': '1',
#         'mode': 'test'
#     })
#     res.encoding = 'gbk'
#     bs = BeautifulSoup(res.text, 'html.parser')
#     ans_url = bs.select('div.nav a')[0]['href']
#     print('http://' + domain + '/' + ans_url)
#
#     # requests.get('http://' + domain + '/' + ans_url)
#
#     # break


huihuabh = [
    27867,
    27868,
    27869,
    27870,
    27871,
    27872,
    27873,
    27874,
    27875,
    27876
]

ans_list = {}

for bh in huihuabh:
    print('--- {} ---'.format(bh))

    res = requests.get('http://{}/redir.php?catalog_id=6&cmd=dajuan_chakan&huihuabh={}&mode=test'.format(domain, bh))
    res.encoding = 'gbk'

    # print(res.text)

    bs = BeautifulSoup(res.text, 'html.parser')

    shiti = bs.select('.shiti')

    for st in shiti:
        timu = st.find('strong').text

        start = st.text.find('标准答案：')
        ans = st.text[start + 5:].strip()

        if timu in ans_list:
            print(timu)
            continue

        if ans == '正确':
            ans = 1
        elif ans == '错误':
            ans = 0

        ans_list[timu] = ans

print(ans_list)

with open('answer.json', 'w', encoding='gbk') as f1:
    json.dump(ans_list, f1, ensure_ascii=False, indent=2)
