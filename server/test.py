from job import TranslationJobs

translation_jobs = TranslationJobs()
translation_1 = translation_jobs.create_job(processing_time=1, error_threshold=0.01)
translation_2 = translation_jobs.create_job(processing_time=0.00, error_threshold=0.01)
translation_3 = translation_jobs.create_job(
    processing_time=1000.0, error_threshold=0.99
)

print("Translation 1:")
translation_jobs.get_job_status(translation_1)  # Should return pending
print("Translation 2:")
translation_jobs.get_job_status(translation_2)  # Should return completed
print("Translation 3:")
translation_jobs.get_job_status(translation_3)  # Should return error
