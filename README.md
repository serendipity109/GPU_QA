# GPU 型號 QA 問答機器人
問一種顯卡型號，回答規格問題。

## 使用說明
* 環境安裝
``` bash
pip install -r requirements.txt
```
* 下載模型
[BERT QA](https://drive.google.com/file/d/1_JcO9SZL_mZ3LCHhIP_zBCrsrBnY-H75/view?usp=sharing "BERT QA") 模型，放置於GPU_QA/qa/trained_model/ 
* 部署 airflow, Postgresql 資料庫，Selenium 爬蟲服務

``` bash
docker-compose up
```
  
* momo 購物網 GPU 資料爬取，Postgresql 資料庫創建資料表、儲存資料

``` bash
sh crawler.sh
```
  
* airflow DAG 觸發，資料庫提取顯卡名稱
<div align="center">
    <img src="./images/airflow.png" width="900" height="455">
</div>

* FastAPI Swagger UI POST 機器人問答
``` bash
sh QA.sh
```
<div align="center">
    <img src="./images/api_q.png" width="450" height="150">
    <img src="./images/api_a.png" width="450" height="150">
</div>
