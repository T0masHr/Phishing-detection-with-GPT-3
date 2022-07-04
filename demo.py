import jsonlcrafter
import email_phish_check
import evaluation


MESSAGES_DIR_PATH = r"C:\Users\tomas\OneDrive - Duale Hochschule Baden-Württemberg Stuttgart\Projekt\EmailFiles\smolTest"
ARGUMENTS = "-vv"
jsonlcrafter.main()
email_phish_check.main([ARGUMENTS])
evaluation.main()