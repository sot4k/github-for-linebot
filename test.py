import time
start_time = time.time()

elapsed_time = int(time.time() - start_time)

elapsed_hour = elapsed_time // 3600
elapsed_minute = (elapsed_time % 3600) // 60
elapsed_second = (elapsed_time % 3600 % 60)

print('勉強おわりました！お疲れさまでした！　勉強時間は、',str(elapsed_hour).zfill(2) + ":" + str(elapsed_minute).zfill(2) + ":" + str(elapsed_second).zfill(2),'でした！')