import time
import xlwt
import requests
from lxml import etree
# 基本的域名
BASE_DOMAIN = 'https://www.dy2018.com/'
# 请求页面时应该发送的数据headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
}

# 爬虫函数
def spider(self, stPer, stmovie_infos):
    # 爬虫的网页
    base_url = "https://www.dy2018.com/html/gndy/dyzz/index_{}.html"
    movies = []  # 定义存储的队列，存储全部电影信息
    detail_urls = [] # 定义存储的队列，存储全部电影地址
    # 爬虫每一页的数据
    for page in range(1, int(stPer.page)+1):
        # 设置当前网页地址
        url = base_url.format(page)
        if page == 1: # 特殊处理，第一页没有“_1”
            url = "https://www.dy2018.com/html/gndy/dyzz/index.html"
        # 爬虫当前网页地址的所有电影的详细网址
        self.label_5.setText("爬虫第 " + str(page) + " 页中。。。")
        one_page_urls = get_detail_urls(url)
        detail_urls = detail_urls + one_page_urls
    stmovie_infos.total = len(detail_urls)
    # 更新爬虫进度状态
    if stmovie_infos.total == 0:
        self.label_5.setText("未发现电影，退出爬虫")
        self.cancel_button()
        return None
    else:
        self.label_5.setText("共发现 " + str(stmovie_infos.total) + " 部电影")
    # 对每一个电影网址爬虫数据
    for detail_url in detail_urls:
        # 更新当前爬虫的电影是第几部
        stmovie_infos.current += 1
        # 爬虫到电影数据
        movie = get_movie_data(detail_url)
        # 更新爬虫进度状态
        self.label_5.setText(movie['title'])
        # 避免死机
        time.sleep(0.1)
        percent = stmovie_infos.current / stmovie_infos.total * 100
        # 更新进度条
        self.progressBar.setValue(percent)
        # 该电影的数据是否符合筛选规则
        if pass_rules(movie, stPer):
            # 符合则加入存储队列
            movies.append(movie)
            # 更新符合条件的电影数
            stmovie_infos.value += 1
        #    print("符合条件")
    # 更新爬虫进度状态
    self.label_5.setText("正保存至movie.excel。。。")
    # 保存到excel表+
    save_movies(movies)
    # 更新爬虫进度状态
    self.label_5.setText("已保存至movie.excel文件")
    # 恢复窗口数据：
    # 设置button状态为“开始”
    self.pushButton.setText("开始")
    # button背景颜色设置为white
    self.pushButton.setStyleSheet("background-color: white")
    # 更新button状态
    self.button_status = True
    print("结束线程spider")

def save_movies(movies):
    i, j = 0, 0
    # 生成一个xlwt.Workbook对象
    xls = xlwt.Workbook()
    # 调用对象的add功能
    sheet = xls.add_sheet('sheet1', cell_overwrite_ok=True)
    # 创建我们第一行的标头数据
    for data in movies:
        for key in data.keys():
            sheet.write(i, j, key)
            j += 1
        break
    for data in movies:
        i += 1
        j = 0
        for value in data.values():
            sheet.write(i, j, value)
            j += 1
    xls.save('movie.xls')

# 爬虫当前页面网址并返回所有电影详细网址
def get_detail_urls(url):
    # 爬虫网址，返回数据到response
#    print("爬虫网址：" + url)
    response = requests.get(url, headers=HEADERS)
    # 解析数据response
    html = etree.HTML(response.text)
    # 建立筛选数据的规则：
    # 当前页面有很多table，筛选出带有属性class='tbspan'的table
    # 在这种table下筛选出a标签中的href属性
    detail_urls = html.xpath("//table[@class='tbspan']//a//@href")
    # 为每一个网址加上基础域名https://www.dy2018.com，组成完整的网址
    detail_urls = list(map(lambda url:BASE_DOMAIN+url, detail_urls))
    # 返回所有电影的详细网址
    return detail_urls

# 爬虫电影地址的数据
def get_movie_data(url):
    # 字典存储电影的数据
    movie = {}
    # 爬虫网址，返回数据到responsetitle
    response = requests.get(url, headers=HEADERS)
    # 解析数据response，电影天堂以gbk编码
    html = etree.HTML(response.content.decode('gbk'))
    # 爬虫电影标题
    title_list = html.xpath("//div[@class='title_all']//h1/text()")
    # 列表转换为字符串
    title = ''.join(title_list)
    movie['title'] = title
#    print("爬虫到：" + title)
    # 爬虫其他电影数据:
    infos = html.xpath("//div[@id='Zoom']//text()")
    # enumerate: 将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出下标和数据
    for index, info in enumerate(infos):
        if info.startswith("◎片　　名"):                    # 让字符串以指定的字符串开头
            info = info.replace("◎片　　名", "").strip()    # 去除空字符
            movie['name'] = info                            # 存储电影名
        elif info.startswith("◎类　　别"):
            info = info.replace("◎类　　别", "").strip()
            movie['type'] = info
        elif info.startswith("◎产　　地"):
            info = info.replace("◎产　　地", "").strip()
            movie['country'] = info
        elif info.startswith("◎年　　代"):
            info = info.replace("◎年　　代", "").strip()
            movie['age'] = info
        elif info.startswith("◎片　　长"):
            info = info.replace("◎片　　长", "").strip()
            movie['length'] = info
        elif info.startswith("◎豆瓣评分"):
            info = info.replace("◎豆瓣评分", "").strip()
            if info[1] == '.':
                movie['rating'] = float(info[0:3])
            else:
                movie['rating'] = "暂无评分"
    # 获取下载地址，[0]是以字符串形式赋值给download_url
    download_url = html.xpath("//td[@bgcolor='#fdfddf']/a/@href")[0]
    # 截取出磁力下载地址，“&tr=http”前的字符串既是磁力下载地址
    n = download_url.find("&tr=http")
    movie['download'] = download_url[:n]
    return movie

# 判断该电影的数据是否符合筛选规则
def pass_rules(movie, stPer):
    if 'type' not in movie or 'country' not in movie or \
        'age' not in movie or 'rating' not in movie or  \
        'length' not in movie:
        return False
    if "全部" not in stPer.type and 'type' in movie:
        if movie['type'] not in stPer.type:
            return False
    if "全部" not in stPer.country and 'country' in movie:
        if movie['country'] not in stPer.country:
            return False
    if "全部" not in stPer.age and 'age' in movie:
        if movie['age'] not in stPer.age:
            return False
    if "ALL" not in stPer.rating and 'rating' in movie:
        if movie['rating'] == "暂无评分":
            return False
        elif float(movie['rating']) < float(stPer.rating):
            return False
    if "ALL" not in stPer.length and 'length' in movie:
        if stPer.length == ">2h":
            length = 120
        elif stPer.length == "1h-2h":
            length = 60
        else:
            length = 0
        if float(movie['length']) < length:
            return False
    return True
