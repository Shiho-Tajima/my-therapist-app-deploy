"""
このファイルは、ファインチューニングの処理を記述するファイルです。
"""

############################################################
# 事前学習済みモデルの用意
############################################################
from openai import OpenAI
from dotenv import load_dotenv
import constants
import time

load_dotenv()

client = OpenAI()

############################################################
# 学習データのモデルへのアップロード
############################################################

file_obj = client.files.create(
    file=open(constants.JSONL_FILE_NAME, "rb"),
    purpose="fine-tune"
)
# ファインチューニングの実行
############################################################
job = client.fine_tuning.jobs.create(
    training_file=file_obj.id,
    model="gpt-4o-mini-2024-07-18"
)

# 完了まで待機

def wait_until_complete(job_id):
    while True:
        job_status = client.fine_tuning.jobs.retrieve(job_id)
        print("ジョブステータス:", job_status.status)
        if job_status.status == "succeeded":
            return job_status.fine_tuned_model
        elif job_status.status == "failed":
            # Retrieve and print error details
            error_details = job_status.error
            if error_details:
                print("エラーコード:", error_details.code)
                print("エラーメッセージ:", error_details.message)
                print("エラーパラメータ:", error_details.param)
            raise Exception("ファインチューニングジョブが失敗しました")
        time.sleep(10)
fine_tuned_model = wait_until_complete(job.id)
print("ファインチューニングされたモデル:", fine_tuned_model)