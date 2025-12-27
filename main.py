"""
Main entry point
"""
from datetime import datetime, date, time, timedelta
import json
import os

from apscheduler.schedulers.blocking import BlockingScheduler
from src.driver import DataSyncClient
from utility.helpers import compose_table_name
from src.config import FinancialQueries

def job_per_day(syncer: DataSyncClient):
    _job_for_others(syncer)
    _job_for_cinema_ticket_daily(syncer)
    _job_monday(syncer)
    _message_after_job(syncer)
    
def _job_monday(syncer: DataSyncClient):
    if date.today().weekday() == 0:
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        syncer.upload_data(FinancialQueries('C07', 'day', yesterday), compose_table_name(syncer.config.get_name('C07')))
    else:
        pass

def job_per_hour(syncer: DataSyncClient):
    _job_for_cinema_tickets_hourly(syncer)

def _job_for_cinema_tickets_hourly(syncer: DataSyncClient):
    today = date.today().strftime("%Y-%m-%d")
    dt_5am = datetime.combine(date.today(), time(6, 0, 0))
    table_name = syncer.config.get_name('C01')

    list_of_ids = syncer.lark_client.get_table_records_id_after_date(table_name, dt_5am, syncer._get_primary_timestamp_column_name('C01'))
    syncer.lark_client.delete_records_by_id(table_name, list_of_ids)
    query_data_today = FinancialQueries('C01', 'day', today)
    syncer.upload_data(query_data_today, table_name)
    _message_after_tickets_job(syncer)

def _job_for_cinema_ticket_daily(syncer: DataSyncClient):
    dt_5am = datetime.combine(date.today() - timedelta(days=14), time(6, 0, 0))

    table_name = syncer.config.get_name('C01')
    list_of_ids = syncer.lark_client.get_table_records_id_before_date(table_name, dt_5am, syncer._get_primary_timestamp_column_name('C01'))
    syncer.lark_client.delete_records_by_id(table_name, list_of_ids)

def _job_for_others(syncer: DataSyncClient):
    syncer.sync_all_yesterday()
    syncer.sync_screening_data()


def _message_after_tickets_job(syncer: DataSyncClient):
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")[:-3]

    message = json.dumps({
        "text": (f'{timestamp}' f' <b>影票数据同步成功</b>')
    })

    syncer.lark_client.send_message_to_chat_group(
        message,
        syncer.lark_client.get_chat_group_id_by_name('服务器状态')
    )

def _message_after_job(syncer: DataSyncClient):
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")[:-3]

    message = json.dumps({
        "text": (f'{timestamp}' f' <b>其他数据同步成功</b>')
    })

    syncer.lark_client.send_message_to_chat_group(
        message,
        syncer.lark_client.get_chat_group_id_by_name('服务器状态')
    )

def _message_init(syncer: DataSyncClient):
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")[:-3]

    message = json.dumps({
        "text": (f'{timestamp}' f' <b>服务器启动中</b>')
    })

    syncer.lark_client.send_message_to_chat_group(
        message,
        syncer.lark_client.get_chat_group_id_by_name('服务器状态')
    )

if __name__ == "__main__":
    global_syncer = DataSyncClient(".env", "config.json")
    # try:
    #     _message_init(global_syncer)
    #     scheduler = BlockingScheduler()

    #     scheduler.add_job(job_per_day, 'cron', hour=8, minute=15, args=[global_syncer])
    #     scheduler.add_job(
    #         job_per_hour,
    #         'cron',
    #         hour='0,8-23',
    #         minute=0,
    #         args=[global_syncer]
    #     )
    #     scheduler.start()
    # except Exception as e:
    #     os._exit(1)

        

