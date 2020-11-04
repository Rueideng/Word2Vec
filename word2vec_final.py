import nltk
import string
from gensim.models import word2vec
import re
import time
from math import isnan
import csv
from pymongo import MongoClient
from nltk.stem import WordNetLemmatizer

uri = f'mongodb://使用者名稱:名稱@IP:27017/'

client = MongoClient(uri)       # 連線本地MongoDB資料庫
# ---------------------------------------------------    從mongo中取資料  ---------------------------------------------------

wordnet_lemmatizer = WordNetLemmatizer()
def get_tokens(text): #把字詞變小寫去除不必要的標點符號與文字
    lowers = re.sub(r'\n|(NULL)|®|\d|[^\w]|[ΆΈ-ώ]|[^a-zA-Z]', ' ', text).lower() # 全部變小寫並清洗
    # print("lowers=",lowers)
    #remove the punctuation using the character deletion step of translate
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation) #string.punctuation
    no_punctuation = lowers.translate(remove_punctuation_map)
    tokens = nltk.word_tokenize(no_punctuation)#分詞
    tokens = [wordnet_lemmatizer.lemmatize(t) for t in tokens]  # put words into base form
    return tokens



#=======================================================================
#儲存所有的待訓練字句
def safetoken(word):
    segSaveFile = 'segDone_test.txt'
    with open(segSaveFile, 'ab+') as saveFile:
        words=word.encode('utf-8')
        saveFile.write(words)
        saveFile.write('\n'.encode())

#=======================================================================
#訓練word2vec並儲存
def model_word2vec():
    # sentences = word2vec.LineSentence(sentence)
    #匯出路徑
    output1 = "./word2vec.model"
    output2 = "./vector.model"
    #載入訓練資料
    sentences = word2vec.LineSentence("segDone_test.txt")
    #開始時間
    start_time = time.time()
    # 訓練word2vec
    model = word2vec.Word2Vec(sentences, min_count=1, size=25, iter=10, sg=0, workers=4, window=10)
    # 訓練花費時間
    print("--- spend %s seconds ---" % (time.time() - start_time))
    # 儲存模型
    model.save(output1)
    # 儲存向量模型
    model.wv.save_word2vec_format(output2, binary=False)
# =======================================================================
# 載入模型
def load_model():
    model = word2vec.Word2Vec.load("./word2vec.model")
    print('關鍵字:','sweet')
    print(model.wv.similar_by_word('sweet')[:5])
    print('關鍵字:', 'wonderful')
    print(model.wv.similar_by_word('wonderful')[:5])
    print('關鍵字:', 'vanilla')
    print(model.wv.similar_by_word('vanilla')[:5])
    print('關鍵字:', 'fruit')
    print(model.wv.similar_by_word('fruit')[:5])
    print(model.wv.similarity('human', 'user'))
    select = "y"
    while select == "y":
        input_string = input('關鍵字:')
        print(model.wv.similar_by_word(input_string)) #顯示輸入的關鍵字的同義字
        # for co in model.wv.similar_by_word(input_string): #取出同義字
        #     print(co[0])


        select = input("輸入: 繼續 y | 停止 n =")

# =======================================================================
# 判斷是否為空 使用isnan 因為從mongo裡面是空的 抓回來只有顯示nan但無法判斷
def isnan(num):
    return num != num



# =======================================================================
#從mongo載入訓練資料
def loadMongofile_add():
    db = client.Whiskey  # DB名
    collections = db.Whiskey_pic  # 桶子名
    word=""
    list_w=""
    for item in collections.find():
        whiskey_name = item['whiskey_name']
        # print("酒名:  ",whiskey_name)
        whiskey_comment_all = item['comment']
        # print("所有使用者評論:    ", whiskey_comment_all)

        whiskey_comment = ""
        # 所有使用者個別的評論

        for item_c in whiskey_comment_all:
            w_c = item_c['text']
            # print(w_c)
            # ---------------------------------------------------    去除null，將每款酒評論合併  ---------------------------------------------------
            if w_c == 'null' or w_c == "":
                continue
            # print(w_c)
            # else:
            #     whiskey_comment = whiskey_comment + w_c
        # if whiskey_comment == "":
        # if whiskey_comment == "":
        #       pass
        # else:
            # print(whiskey_comment)
            tokens=get_tokens(w_c)
            # print(tokens)

            tks = ""
            for tk in tokens:
                tks = tks + " " + tk
            word=word +"\n"+tks
            # print(word)
    safetoken(word)

def loadMongofile_cocktail():
    db = client.cocktail  # DB名
    collections = db.all_cocktail  # 桶子名
    word = ""
    list_w = ""

    for item in collections.find():
        cocktail_name = item['name']
        print("酒名:", cocktail_name)
        cocktail_comment_all = item['comment']
        print("所有使用者評論:", cocktail_comment_all)
        print(type(cocktail_comment_all))
        try:
            if isnan(float(cocktail_comment_all)) == True:
                continue
        except:
            if cocktail_comment_all == 'null' or cocktail_comment_all == "" or cocktail_comment_all == " nan" or cocktail_comment_all == "None":
                continue
            else:
                # print( cocktail_comment_all == "")
                cocktail_all = cocktail_comment_all.replace("user", "").replace("name", "").replace("text", "")
                tokens = get_tokens(cocktail_all)
                # print(tokens)

                tks = ""
                for tk in tokens:
                    tks = tks + " " + tk
                word = word + "\n" + tks
    print(word)
    safetoken(word)

if __name__ == "__main__":
    # loadMongofile_add()
    # loadMongofile_cocktail()
    # model_word2vec()
    load_model()




