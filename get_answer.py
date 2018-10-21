import requests
from bs4 import BeautifulSoup
import json

import time

import threading

__DOMAIN__ = 'http://{}/'.format(input('请输入服务器ip: '))

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
# req_sess = requests.session()
#
#
# __DATI_TEST__ = __DOMAIN__ + 'redir.php?catalog_id=6&cmd=dati&mode=test'
#
#
# for tkbh in tikubh:
#     res = req_sess.get(__DOMAIN__ + 'redir.php?catalog_id=6&cmd=testing&tikubh={}'.format(tkbh))
#     res.encoding = 'gbk'
#     # print(res.text)
#
#     # 提交答卷
#     res = req_sess.post(__DATI_TEST__, {
#         'runpage': '0',
#         'page': '0',
#         'direction': '',
#         'tijiao': '1',  # 1:提交答卷
#         'postflag': '1',
#         'mode': 'test'
#     })
#     res.encoding = 'gbk'
#     bs = BeautifulSoup(res.text, 'html.parser')
#     ans_url = bs.select('div.nav a')[0]['href']
#     print(__DOMAIN__ + ans_url)
#
#     # requests.get(__DOMAIN__ + ans_url)
#
#     # break


__DAJUAN_CHAKAN__ = __DOMAIN__ + 'redir.php?catalog_id=6&cmd=dajuan_chakan&huihuabh={}&mode=test'

__ANS_FILE_NAME__ = 'answer.json'

t_lock = threading.Lock()


def get_ti(bh1):
    global ans_lst

    # 查看答案
    res = requests.get(__DAJUAN_CHAKAN__.format(bh1))
    res.encoding = 'gbk'

    if '要查看的答卷不存在！' in res.text:
        return

    bs = BeautifulSoup(res.text, 'html.parser')

    # 取得所有试题
    shiti = bs.select('.shiti')

    if len(shiti) == 0:
        return

    try:
        t_lock.acquire()

        # 原有题目
        old_ans_count = len(ans_lst)

        for st in shiti:
            timu = st.find('strong').text.strip()

            if timu == '':
                continue

            ans_pos = st.text.find('标准答案：')
            if ans_pos == -1:
                continue

            ans = st.text[ans_pos + 5:].strip()

            if timu in ans_lst:
                continue

            if ans == '正确':
                ans = '1'
            elif ans == '错误':
                ans = '0'

            ans_lst[timu] = ans

        # 如果有新增题目 才打印
        if len(ans_lst) - old_ans_count > 0:
            print('[+] 编号{}, 当前{}题'.format(bh1, len(ans_lst)))

    finally:
        t_lock.release()


# 自己答的题目模板
# huihuabh = [
#     27867,
#     27868,
#     27869,
#     27870,
#     27871,
#     27872,
#     27873,
#     27874,
#     27875,
#     27876
# ]

with open(__ANS_FILE_NAME__, 'r', encoding='utf8') as f2:
    ans_lst = json.load(f2)
    old_ans_len = len(ans_lst)

threads = []
# for bh in huihuabh:
for bh in range(3000, 29999):
    t = threading.Thread(target=get_ti, args=(bh,))
    threads.append(t)
for t in threads:
    time.sleep(0.1)
    t.start()
    while len(threading.enumerate()) > 100:
        pass
for t in threads:
    t.join()

print('[+] 原有{}题'.format(old_ans_len))
new_timu_count = len(ans_lst) - old_ans_len
print('[+] 新增{}题'.format(new_timu_count))

if new_timu_count:
    # # 有新题目才 提示 写入文件
    if input('是否写入文件[0/1]: ') == '1':
        with open(__ANS_FILE_NAME__, 'w', encoding='utf8', newline='\n') as f1:
            json.dump(ans_lst, f1, ensure_ascii=False, indent=4)
            print('[+] 写入成功')
    else:
        print('[-] 放弃写入')
