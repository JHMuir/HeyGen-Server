from job import TranslationServer

translation_server = TranslationServer()
translation_1 = translation_server.create_job(processing_time=1, error_probability=0.01)
translation_2 = translation_server.create_job(
    processing_time=0.00, error_probability=0.01
)
translation_3 = translation_server.create_job(
    processing_time=1000.0, error_probability=0.99
)

print("Translation 1:")
translation_server.get_job_status(translation_1)  # Should return pending
print("Translation 2:")
translation_server.get_job_status(translation_2)  # Should return completed
print("Translation 3:")
translation_server.get_job_status(translation_3)  # Should return error
