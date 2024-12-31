from library.client import TranslationClient
import time


def status_callback(status):
    print(f"Current status: {status}")


def test_translation():
    with TranslationClient() as client:
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


if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(2)
    test_translation()
