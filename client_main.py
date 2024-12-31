from library.client import TranslationClient
import time


def status_callback(status):
    print(f"Current status: {status}")


def status_callback_with_interval(status):
    print(f"Status at {time.strftime('%H:%M:%S')}: {status}")


def test_get_status(client: TranslationClient):
    try:
        print("Creating jobs...")
        job_1 = client.create_job(processing_time=0.01, error_probability=0.01)
        print(f"Created job 1: {job_1}")
        print("\nWaiting for job 1...")
        status_1 = client.get_status(job_id=job_1)  # Should return complete
        print(f"\nJob 1 final status: {status_1}")

        job_2 = client.create_job(processing_time=20, error_probability=0.01)
        print(f"Created job 2: {job_2}")
        print("\nWaiting for job 2...")
        status_2 = client.get_status(job_id=job_2)  # should return pending
        print(f"\nJob 2 final status: {status_2}")

        job_3 = client.create_job(processing_time=1500, error_probability=0.99)
        print(f"Created job 3: {job_3}")
        print("\nWaiting for job 3...")
        status_3 = client.get_status(job_id=job_3)  # Should always return error
        print(f"\nJob 3 final status: {status_3}")

    except Exception as e:
        print(f"Error occurred: {e}")


def test_wait_for_completion(client: TranslationClient):
    try:
        print("Creating jobs...")
        job_1 = client.create_job(processing_time=10, error_probability=0.01)
        print(f"Created job 1: {job_1}")
        print("\nWaiting for job 1...")
        status_1 = client.wait_for_completion(
            job_id=job_1, callback=status_callback
        )  # Will take 10 seconds, returns completed
        print(f"\nJob 1 final status: {status_1}")

        job_2 = client.create_job(processing_time=20, error_probability=0.01)
        print(f"Created job 2: {job_2}")
        print("\nWaiting for job 2...")
        status_2 = client.wait_for_completion(
            job_id=job_2, callback=status_callback
        )  # Will take 20 seconds, returns completed
        print(f"\nJob 2 final status: {status_2}")

        job_3 = client.create_job(processing_time=1500, error_probability=0.99)
        print(f"Created job 3: {job_3}")
        print("\nWaiting for job 3...")
        status_3 = client.wait_for_completion(
            job_id=job_3, callback=status_callback
        )  # Should always return error
        print(f"\nJob 3 final status: {status_3}")

    except Exception as e:
        print(f"Error occurred: {e}")


def test_wait_for_completion_with_interval(client: TranslationClient):
    try:
        print("Creating jobs...")

        job_1 = client.create_job(processing_time=10, error_probability=0.01)
        print(f"Created job 1: {job_1}")
        print("\nWaiting for job 1...")
        status_1 = client.wait_for_completion_with_interval(
            job_id=job_1, callback=status_callback_with_interval, interval=1.0
        )  # 1 second between checks
        print(f"\nJob 1 final status: {status_1}")

        job_2 = client.create_job(processing_time=20, error_probability=0.01)
        print(f"Created job 2: {job_2}")
        print("\nWaiting for job 2...")
        status_2 = client.wait_for_completion_with_interval(
            job_id=job_2, callback=status_callback_with_interval, interval=10.0
        )  # 10 seconds between checks
        print(f"\nJob 2 final status: {status_2}")

        job_3 = client.create_job(processing_time=110, error_probability=0.01)
        print(f"Created job 3: {job_3}")
        print("\nWaiting for job 3...")
        status_3 = client.wait_for_completion_with_interval(
            job_id=job_3, callback=status_callback_with_interval, interval=60.0
        )  # 1 minute between checks
        print(f"\nJob 3 final status: {status_3}")

        job_4 = client.create_job(processing_time=1500, error_probability=0.99)
        print(f"Created job 4: {job_4}")
        print("\nWaiting for job 4...")
        status_4 = client.wait_for_completion_with_interval(
            job_id=job_4, callback=status_callback_with_interval, interval=60.0
        )  # 1 minute between checks, should return error
        print(f"\nJob 4 final status: {status_4}")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(2)
    client = TranslationClient()
    print("====== Testing get_status ======")
    test_get_status(client=client)
    print("====== Testing wait_for_completion ======")
    test_wait_for_completion(client=client)
    print("====== Testing wait_for_completion_with_interval ======")
    test_wait_for_completion_with_interval(client=client)
