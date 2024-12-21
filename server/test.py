from job import TranslationJob

translation_1 = TranslationJob(processing_time=1, error_threshold=0.01)
translation_2 = TranslationJob(processing_time=0.00, error_threshold=0.01)
translation_3 = TranslationJob(processing_time=1000.0, error_threshold=0.99)

print("Translation 1:")
translation_1.get_status()  # Should return pending
print("Translation 2:")
translation_2.get_status()  # Should return completed
print("Translation 3:")
translation_3.get_status()  # Should return error
