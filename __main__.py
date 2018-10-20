import json
import requests
from bs4 import BeautifulSoup

__DOMAIN__ = 'http://{}/'
# __INDEX__ = __DOMAIN__ + 'index.php'
__LOGIN__ = __DOMAIN__ + 'exam_login.php'
__LOGOUT__ = __DOMAIN__ + 'exam_login.php?cmd=logout'
# 选择考试试卷
__KAISHI_KAOSHI__ = __DOMAIN__ + 'redir.php?catalog_id=6&cmd=kaoshi_chushih&kaoshih=16354'
# 考试题目
__KS__ = __DOMAIN__ + 'redir.php?catalog_id=6&cmd=dati'
# 遵守承诺
__CHENGNUO__ = __DOMAIN__ + 'redir.php?catalog_id=6&cmd=tijiao&mode=exam'

if __name__ == '__main__':
    ip = input('请输入服务器ip: ')
    __DOMAIN__ = __DOMAIN__.format(ip)

    # 题库答案
    with open('answer.json', 'r', encoding='gbk') as f_ans:
        ans_lst = json.load(f_ans)
    isChange = False

    # 账号信息
    stu_no = input('学号: ')
    default_password = stu_no[-4:]  # 默认密码为学号后4位
    password = input('密码(默认{},可不填): '.format(default_password))
    if password == '':
        password = default_password

    _login_data = {
        'xuehao': stu_no,
        'password': password,
        'postflag': '1',
        'cmd': 'login',
        'role': '0',
        '%CC%E1%BD%BB': '%B5%C7%C2%BC'
    }

    req_sess = requests.session()

    # 登录
    req_sess.post(__LOGIN__, _login_data)
    print('[+] 账号登录成功')

    # 选择 开始考试
    res = req_sess.get(__KAISHI_KAOSHI__)
    res.encoding = 'gbk'

    # 异常处理
    if '你已经用完了所有的考试机会，不允许再参与该考试' in res.text:
        print('[-] 你已经用完了所有的考试机会，不允许再参与该考试')
        exit()

    # 题目编号
    ti_no = 0

    # 最后统一提交数据
    _data_last = {
        'runpage': '0',
        'page': '0',
        'direction': '1',
        'tijiao': '0',
        'postflag': '1',
        'autosubmit': '0'
    }

    for page in range(-1, 3):
        # 翻页时用的数据模板
        _data = {
            'runpage': '0',
            'page': page,
            'direction': '1',
            'tijiao': '0',
            'postflag': '1',
            'autosubmit': '0'
        }

        res = req_sess.post(__KS__, _data)
        res.encoding = 'gbk'

        bs = BeautifulSoup(res.text, 'html.parser')

        # 拿题目
        for ti in bs.select('.shiti h3'):
            ti_no += 1  # 题号加1

            # 去除题号
            start = ti.text.find('、')
            timu = ti.text[start + 1:].strip()

            # 答案不存在
            if timu not in ans_lst:
                print('\t' + ti.text)

                # 遍历答案
                for opts in ti.parent.select('li'):
                    value = opts.find('input')['value']
                    label = opts.find('label').text.strip()
                    print('\t\t{}: {}'.format(value, label))

                input_ans = input('\t答案: ')

                ans_lst[timu] = input_ans
                isChange = True

                print()

            _data_last['ti_{}'.format(ti_no)] = ans_lst[timu]

    print('[+] 题目作答完毕！')
    is_submit = input('是否顺便帮您提交试卷？否则自行网页提交[0|1]: ')

    # 提交试卷 1
    if is_submit == '1':
        _data_last['tijiao'] = '1'

    req_sess.post(__KS__, _data_last)
    print('[+] 作答记录已保存')

    # 提交试卷 2
    if is_submit == '1':
        # 我遵守以上承诺
        _chengnuo_data = {
            'button': '+%CE%D2%B3%D0%C5%B5%D7%F1%CA%D8%D2%D4%C9%CF%B3%D0%C5%B5%CA%E9%C4%DA%C8%DD+',
            'postflag': '1',
            'mode': 'exam'
        }
        res = req_sess.post(__CHENGNUO__, _chengnuo_data)
        print('[+] 试卷已提交')

        res.encoding = 'gbk'
        bs = BeautifulSoup(res.text, 'html.parser')
        print(bs.select('.shuoming')[0].text.strip())
    else:
        print('[-] 请自行登录网页提交您的试卷,否则成绩无效！')

    if isChange:
        with open('answer.json', 'w', encoding='gbk') as f_ans:
            json.dump(ans_lst, f_ans, ensure_ascii=False, indent=4)
            print('[+] 题库答案已更新')

    requests.get(__LOGOUT__)
    print('[+] 账号退出成功')
