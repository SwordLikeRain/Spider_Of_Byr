import os


# 调用Fliter处理每个文件夹

# for i in range(230307, 230332):
#     s=os.popen('python Fliter.py db{}\\20{}_Whisper.txt 0'.format(i,i))

# 将文件夹处理后结果合并

file=open('db2023_03_total.txt','w', encoding='utf8')
for i in range(230301,230332):
    for line in open('db{}\\20{}_Whisper_after.txt'.format(i, i), encoding='utf8'):
        file.writelines(line)
file.close()

# 将合并后结果继续用Fliter处理
# os.popen('python Fliter.py database-17.txt 0')

# for i in range(230101,230132):
#     print(i)