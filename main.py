from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import numpy as np
import time
import pandas as pd
from tensorflow import keras
from selenium.webdriver import ChromeOptions

model = keras.models.load_model("model_2")

app = Flask(__name__)
api = Api(app)
CORS(app)

chrome_options = ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")

chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")


class status (Resource):
    # print(url)
    def get(self, url):
        driver = Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        wait = WebDriverWait(driver, 10)

        if url != "favicon.ico":
            url = "https://www.youtube.com/watch?v=" + url
            driver.get(url)

            for item in range(10):  # by increasing the highest range you can get more content
                wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
                time.sleep(3)

            comment_list = []
            for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#comment #content-text"))):
                comment_list.append(comment.text)

            df = pd.DataFrame(comment_list)
            data = model.predict(df)
            labels = ['Other', 'Positive', 'Question', 'Suggestion']
            ret = {'Positive': [], 'Question': [], 'Suggestion': [], 'Other': []}
            for i in range(len(data)):
                ret[labels[np.argmax(data[i])]].append(comment_list[i])
            return ret


api.add_resource(status, '/<path:url>')
# api.add_resource(Sum, '/add/<path:a>')

if __name__ == '__main__':
    app.run(debug=True)
