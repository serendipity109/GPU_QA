from fastapi import FastAPI
from tqdm import tqdm
import logging
import psycopg2
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def init_logging():
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(levelname)s %(processName)s --- [%(threadName)s] %(name)s : %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    logger_level = logging.INFO
    ch = logging.StreamHandler()
    ch.setLevel(logger_level)
    ch.setFormatter(formatter)
    handlers = [ch]
    logging.basicConfig(level=logger_level, handlers=handlers)

init_logging()

logger = logging.getLogger(__name__)

app = FastAPI()

conn = psycopg2.connect(database="airflow", user="airflow", password="airflow", host="127.0.0.1", port="5432")
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS GPU (名稱 varchar(255), 價格 varchar(255), 類型 varchar(255),款式 varchar(255),品牌名稱 varchar(255),記憶體 varchar(255),適用於 varchar(255), 保固期 varchar(255), 晶片 varchar(255), 商品規格 varchar(255));""")
conn.commit()

@app.post("/crawl")
async def crawl(word='顯卡'):
    driver = webdriver.Remote(
        command_executor='http://0.0.0.0:4448/wd/hub',
        desired_capabilities=DesiredCapabilities.CHROME,
    )
    home_page = f'https://www.momoshop.com.tw/search/searchShop.jsp?keyword={word}&searchType=1&curPage=1&_isFuzzy=0&showType=chessboardType'
    driver.get(home_page)
    doc = pq(driver.page_source)
    
    logger.info('Start crawling item urls.')
    items_url = []
    for item in doc('.listArea ul li a.goodsUrl').items():
        items_url.append(item.attr('href'))

    product_names = []
    item_dict = {}
    logger.info('Start crawling items information.')

    for url in tqdm(items_url):
        item_page = f'https://www.momoshop.com.tw{url}'
        driver.get(item_page)
        doc = pq(driver.page_source)
        product_name = doc('#osmGoodsName')[0].text
        product_names.append(product_name)
        price = doc('ul.prdPrice .special span').text()
        table = []; table_dict = {}; key_list = set()
        spec = doc('.attributesArea')
        for th in spec('tbody tr th').items():
            if th.attr('rowspan'):
                nrows = int(th.attr('rowspan'))
                for i in range(nrows-1):
                    table.append([th.text()])
            table.append([th.text()])
        for i, td in enumerate(spec('tbody tr td ul').items()):
            table[i].append(td('li').text())
        for k, v in table:
            if k in table_dict.keys():
                table_dict[k] += f" {v}"
            else:
                table_dict[k] = v
            key_list.add(k)
        item_dict[product_name] = table_dict
        item_dict[product_name]['價格'] = price

    logger.info('Storing data into Postgresql.')
    query = "INSERT INTO GPU (名稱, 價格, 類型, 款式, 品牌名稱, 記憶體, 適用於, 保固期, 晶片, 商品規格) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    for key in item_dict.keys():
        item = item_dict[key]
        miss_keys = list(set(['名稱', '價格', '類型', '款式', '品牌名稱', '記憶體', '適用於', '保固期', '晶片', '商品規格'])-set(item.keys()))
        if '商品規格' in item.keys():
            if len(item['商品規格']) > 250:
                item['商品規格'] = item['商品規格'][:250] + '...'
        for miss_key in miss_keys:
            item[miss_key] = ''
        val = (key, item['價格'], item['類型'], item['款式'],item['品牌名稱'],item['記憶體'],item['適用於'],item['保固期'],item['晶片'],item['商品規格'])
        cur.execute(query,val)
        conn.commit()
    cur.execute("""SELECT * FROM gpu;""")
    table = cur.fetchall()
    driver.quit()
    cur.close()
    conn.close()
    return table
