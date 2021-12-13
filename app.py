import os
import requests
import json
from flask import Flask, render_template, request, redirect, send_file
from s3_functions import list_files, upload_file, show_image
import boto3
import urllib.request

app = Flask(__name__)

LAST_MEME_GEN = ""
BUCKET = os.environ.get('BUCKET_NAME')
TOPIC_ARN = os.environ.get('TOPIC_ARN')
AWS_REGION = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/placement/region').read().decode()

def fetch_meme_string():
    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'iflipsess=6spj49rvv6b86qdtdddu7jn476; __utma=71379083.1268303026.1639146226.1639407255.1639410627.4; __utmc=71379083; __utmz=71379083.1639146226.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _ga=GA1.2.1268303026.1639146226; _fbp=fb.1.1639146239477.931899502; __gads=ID=45eed67a06cfdb8d-228b480de1cc0049:T=1639146241:S=ALNI_MbXJzo8TWwCW8ANbKYmMiwuBJBHuQ; _pbjs_userid_consent_data=3524755945110770; _pubcid=47bf575b-ccaf-4936-a7d2-6976ad872a4e; cto_bidid=L5fmw19aVGp6OSUyQmNGT2NIR3g3d…KTzFHS1pLV3RPVTlDazZrTzlWWGo3R3FjN3c1RHhadFU3Z2g1VDdwbEhSYnhncXlTMUJMRTFXMUJMbWZWU1hsc3o2NWJJTXdYc2NzJTNE; cto_bundle=Dtr3kl8wOEh0TEZHT1VTZWx6SHY3UW5PYU5sY1I3YlVEVUlza0ZiZlAzanVOVXJLUFdvYjdIOWV2QmlaTjBLMmoweXI1bzBOQmZDTnRLN21kQnR6eGZ4NHIyMU93NkJ6cGlMYyUyRlg3JTJCYXpNQjdEZlR4ZzVvdjJTNlpZRXpyQ3FhUmxGdnBLT2dFcU92U0FGZHc3QnRqVzk4aVR6SlRNTFJHNzJtcjVUQWd2QmpTdWdFJTNE; G_ENABLED_IDPS=google; rootkey=J-8iGYIkpx9tXWFedZSdKjhI7bLW8npL; rootemail=john.cenicola%40rackspace.com; __utmb=71379083.1.10.1639410627; __utmt=1',
    }

    post_request = 'use_openai=0&meme_id=14371066&init_text=&__tok=NhUyH5dwAwQpmsuiwrr+7qH4aPxkysLIxykGS4TxAEY=&__cookie_enabled=1'
    response = requests.post(
        "https://imgflip.com/ajax_ai_meme",
        data=post_request,
        headers=headers
    )
    result = json.loads(response.text)
    return result['texts']


@app.route("/")
def home():
    global LAST_MEME_GEN
    return render_template('index.html', last_meme_gen=LAST_MEME_GEN)

@app.route("/queue_meme", methods=['POST'])
def queue_meme():
    global LAST_MEME_GEN
    global AWS_REGION

    LAST_MEME_GEN = fetch_meme_string()
    sns = boto3.client("sns", region_name=AWS_REGION)
    sns.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(LAST_MEME_GEN)
        )
    return redirect("/")

@app.route("/pics")
def list():
    contents = show_image(BUCKET)
    return render_template('collection.html', contents=contents)

if __name__ == '__main__':
    app.run(debug=True)
