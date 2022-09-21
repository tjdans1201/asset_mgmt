from apscheduler.schedulers.blocking import BlockingScheduler
import batchprocess


def run_schedule():
    scheduler = BlockingScheduler()

    scheduler.add_job(
        batchprocess.insert_stock,
        "cron",
        hour="10",
        max_instances=10,
    )

    scheduler.add_job(
        batchprocess.update_investment_principle,
        "cron",
        hour="10",
        second="10",
        max_instances=10,
    )

    scheduler.add_job(
        batchprocess.update_account_asset_info,
        "cron",
        hour="10",
        second="20",
        max_instances=10,
    )

    scheduler.start()


if __name__ == "__main__":
    run_schedule()
