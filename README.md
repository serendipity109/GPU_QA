# GPU 型號 QA 問答機器人
問一種顯卡型號，回答他的規格問題。

## 使用說明
* 環境安裝
``` bash
pip install -r requirements.txt
```
* 部署 airflow, Postgresql 資料庫，Selenium 爬蟲服務
  ``` bash
docker-compose up
  ```
* momo 購物網 GPU 資料爬取，Postgresql 資料庫創建資料表、儲存資料
  ``` bash
sh crawler.sh
  ```
* airflow DAG 觸發，資料庫提取顯卡名稱
![](airflow.png)

* FastAPI Swagger UI POST 機器人問答題問
![](fastapi.png)
