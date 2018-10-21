import json
import requests
from bs4 import BeautifulSoup

req_sess = requests.session()


def login(un, pw):
    global req_sess
    _login_data = {
        'xuehao': un,
        'password': pw,
        'postflag': '1',
        'cmd': 'login'
    }
    res = req_sess.post(__LOGIN__, _login_data)
    res.encoding = 'gbk'
    if '登录失败！密码错误或者帐号不存在。' in res.text:
        print('[-] 登录失败！密码错误或者帐号不存在。')
        exit()

    res = req_sess.get(__INDEX__)
    res.encoding = 'gbk'
    bs = BeautifulSoup(res.text, 'html.parser')
    txt = bs.find(class_='explanation').text.strip()
    end_pos = txt.find('，')
    if end_pos != -1:
        print('[+] 账号登录成功')
        print('[+] {}'.format(txt[:end_pos]))
    else:
        print('[-] 账号登录失败')
        exit()


def logout():
    global req_sess
    req_sess.get(__LOGOUT__)
    print('[+] 账号退出成功')


print('{}{}{}'.format('=' * 15, ' ' * 20, '=' * 15))
print('{:^40}'.format('实训(验)室安全考试答题工具'))
print('{}{}{}'.format('=' * 15, ' ' * 20, '=' * 15))

# + 定义URL地址 +
__DOMAIN__ = 'http://{}/'.format(input('服务器IP: '))
__INDEX__ = __DOMAIN__ + 'index.php'
__LOGIN__ = __DOMAIN__ + 'exam_login.php'
__LOGOUT__ = __DOMAIN__ + 'exam_login.php?cmd=logout'
# 选择考试试卷
__KAISHI_KAOSHI__ = __DOMAIN__ + 'redir.php?catalog_id=6&cmd=kaoshi_chushih&kaoshih=16354'
# 考试题目
__KS__ = __DOMAIN__ + 'redir.php?catalog_id=6&cmd=dati'
# 遵守承诺
__CHENGNUO__ = __DOMAIN__ + 'redir.php?catalog_id=6&cmd=tijiao&mode=exam'
# - 定义URL地址 -


# 题库答案
with open('answer.json', 'r', encoding='utf8') as f_ans:
    ans_lst = json.load(f_ans)
    isChange = False

# 账号信息
pre_stu_no = '1824'
stu_no = input('学号: {}'.format(pre_stu_no))
password = input('密码(默认{},可不填): '.format(stu_no))
if password == '':
    password = stu_no

# 拼接学号
stu_no = pre_stu_no + stu_no

# 登录
login(stu_no, password)

if input('是否开始答题[0/1]: ') != '1':
    logout()
    exit()

# 选择 开始考试
res = req_sess.get(__KAISHI_KAOSHI__)
res.encoding = 'gbk'

# 异常处理
if '你已经用完了所有的考试机会，不允许再参与该考试' in res.text:
    print('[-] 你已经用完了所有的考试机会，不允许再参与该考试')
    logout()
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

        # 答案不存在, 需要自己作答
        if timu not in ans_lst:
            print('\t' + ti.text)

            # 遍历输出答案
            for opts in ti.parent.select('li'):
                value = opts.find('input')['value']
                label = opts.find('label').text.strip()
                print('\t\t{}: {}'.format(value, label))

            # 填写答案
            input_ans = input('\t答案: ')

            # 记录答案
            ans_lst[timu] = input_ans
            isChange = True

            print()

        _data_last['ti_{}'.format(ti_no)] = ans_lst[timu]

print('[+] 题目作答完毕！')
is_submit = input('是否顺便帮您提交试卷？否则自行网页提交[0/1]: ')

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
    with open('answer.json', 'w', encoding='utf8', newline='\n') as f_ans:
        json.dump(ans_lst, f_ans, ensure_ascii=False, indent=4)
        print('[+] 题库答案已更新')

logout()
