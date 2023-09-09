import sqlite3, pymysql, os, base64, cv2, openai, dlib
from werkzeug.datastructures import FileStorage
import numpy as np
import matplotlib.pyplot as plt




base_path= os.path.abspath(os.path.dirname(__file__))
# 這邊的api_key="xxxxx..." 其實就是一個字串而已，這邊用base64編碼小小的加密了一下是因為如果我不加密就直接明碼上傳github的話，會被openAI偵測到，然後這個api_key就會失效
openai.api_key= base64.b64decode('c2stalpINDVOdnMxdXdxZmlYZnlFWTFUM0JsYmtGSm50VGdxbUJpZ1pHTmg4dXpNREtV').decode()


# SQLite
createTableText= {
    "user":'''CREATE TABLE IF NOT EXISTS user(
        ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT
    );''',
    "chat":'''CREATE TABLE IF NOT EXISTS chat(
        ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        msg TEXT,
        type TEXT
    );'''
}
# mySQL
# host= "localhost"
# port= 3306
# user= "root"
# password= "01234567"
# db= "testdb"
# createTableText= {
#     "user":'''CREATE TABLE IF NOT EXISTS user(
#         ID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#         name VARCHAR(100)
#     );''',
#     "chat":'''CREATE TABLE IF NOT EXISTS chat(
#         ID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#         user_id VARCHAR(100),
#         msg VARCHAR(200),
#         type VARCHAR(200)
#     );'''
# }



# 從資料庫中拿資料
def getData(tableName, commamd):
    # SQLite
    conn = sqlite3.connect(base_path+"/data.db")
    # mySQL
    # conn= pymysql.connect(host=host, port=port, user=user, passwd=password, charset="utf8", db=db)
    cursor= conn.cursor()
    cursor.execute(createTableText[tableName])
    result= cursor.execute(commamd)
    # conn.close()
    return result.fetchall()


# 新增資料到資料庫
# data= {"name":"abc", "user_id":123, ...}
def insertData(tableName, data:dict):
    # SQLite
    conn = sqlite3.connect(base_path+"/data.db")
    # mySQL
    # conn= pymysql.connect(host=host, port=port, user=user, passwd=password, charset="utf8", db=db)
    
    cursor= conn.cursor()
    cursor.execute(createTableText[tableName])
    
    values= list(data.values())
    for i,value in enumerate(values):
        if type(value)==str: values[i]="'"+ value.replace("'","''")+ "'"
        elif type(value)==int: values[i]= str(value)
    cursor.execute(f"INSERT INTO {tableName} ({','.join(data.keys())}) VALUES ({','.join(values)});")
    new_data_id= cursor.lastrowid
    conn.commit()
    # conn.close()
    return new_data_id


# 新增檔案
def newFile(new_id, file:FileStorage):
    # 如果沒有該資料夾的話，自動新增一個
    if not os.path.exists(base_path+"/user_images"):
        os.mkdir(base_path+"/user_images")
    # 確認傳進來的圖片檔案是個有副檔名的正常檔案
    if "." in file.filename:
        fileType= file.filename.split(".")[-1]
        # 以user_id為名，重新命名檔案
        newFileName= str(new_id)+ '.'+ fileType
        file.save(base_path+"/user_images/"+newFileName)




detector= dlib.get_frontal_face_detector()
sp= dlib.shape_predictor(base_path+ "/models/dlibDat/shape_predictor_68_face_landmarks.dat")
facerec= dlib.face_recognition_model_v1(base_path+ "/models/dlibDat/dlib_face_recognition_resnet_model_v1.dat")
# 讀取特徵array
def getFeature(img):
    dets= detector(img, 1)
    for det in dets:
        shape= sp(img, det)
        feature= facerec.compute_face_descriptor(img, shape)
        return np.array(feature)

# 讀取及比較人臉圖片
def compareFace(fileCode):
    imgdata = base64.b64decode(fileCode)
    nparr = np.frombuffer(imgdata, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # 測試 直接顯示相片
    # # OpenCV 是 BGR 模式。但是 Matplotib 是 RGB 模式，所以需要用將BGR轉RGB才能用 Matplotib呈現
    # img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # plt.imshow(img2)
    # plt.show()
    
    # 測試 儲存圖片
    # filename = base_path+"/user_images/01.jpg"
    # with open(filename, "wb") as f:
    #     f.write(imgdata)
    
    try:
        feature1= getFeature(img)
        # 如果feature1有抓到人臉物件，才會繼續進行下面的部分，否則直接跳到最下面的return None
        if type(feature1) != type(None):
            # 抓取user_images資料夾裡面的所有圖片，並逐一比對，此為測試用又懶的訓練模型時的笨方法，圖片量大時候很慢
            fileNames= [file for file in os.listdir(base_path+"/user_images/")]
            for fileName in fileNames:
                img = cv2.imread(base_path+"/user_images/"+fileName, cv2.IMREAD_COLOR)
                feature2= getFeature(img)
                # 相減以取得現在偵測到的相片和user_images資料夾及裡面的相片的特徵的歐式距離
                dist= np.linalg.norm(feature1- feature2)
                # 如果特徵相差不大(暫定<0.3)，則return出檔案名稱去除附檔名的部分(即為uesr_id)
                if dist < 0.3:
                    return fileName.split(".")[0]
    except:
        pass
    return None


# 串接chatGPT
def getChatGPTResponse(user_id, text):
    # 提取之前的對話紀錄，以便接續之前的對話
    dialogue= getData("chat", f"SELECT msg,type FROM chat WHERE user_id={user_id};")
    for i,record in enumerate(dialogue):
        if record[1] == "send":
            dialogue[i]= {"role":"user", "content":record[0]}
        elif record[1] == "response":
            dialogue[i]= {"role":"assistant", "content":record[0]}
    # 只取最近的4條紀錄，以避免費用暴增
    if len(dialogue)>=5:
        dialogue= dialogue[:4]
    dialogue.append({"role":"user", "content":text})
    # 向chatGPT api發送訊息
    response= openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages= dialogue
    )
    response= response['choices'][0]['message']['content']
    
    # 儲存對話紀錄
    insertData("chat", {"user_id":user_id, "msg":text, "type":"send"})
    insertData("chat", {"user_id":user_id, "msg":response, "type":"response"})
    return response
