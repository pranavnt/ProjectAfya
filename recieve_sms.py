import numpy as np
import pandas as pd

data = pd.read_csv('WHO_FAQ2.csv')

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text
import re

def preprocess_sentences(input_sentences):
    return [re.sub(r'(covid-19|covid)', 'coronavirus', input_sentence, flags=re.I)
            for input_sentence in input_sentences]

module = hub.load('https://tfhub.dev/google/universal-sentence-encoder-multilingual-qa/3')

responseEncodings = module.signatures['response_encoder'](
        input=tf.constant(preprocess_sentences(data.Answer)),
        context=tf.constant(preprocess_sentences(data.Context)))['outputs']

def returnAnswer(question):
    testQuestion = [question]

    # Encode test questions
    questionEncodings = module.signatures['question_encoder'](
    tf.constant(preprocess_sentences(testQuestion)))['outputs']

    return str(data.Answer[np.argmax(np.inner(questionEncodings, responseEncodings), axis=1)])

from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a MMS message."""
    # Start our TwiML response
    resp = MessagingResponse()

    messageSent = request.form['Body']
    # Add a text message

    if messageSent.lower() == 'hi' or messageSent.lower() == 'hello':
        msg = resp.message("Hi, my name is Afya, and I'm an chatbot who can answer your questions about COVID-19. Ask away!")
    else:
        newAnswer = returnAnswer(str(messageSent))
        querystring = {"text":newAnswer}
        msg = resp.message(mewAnswer)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
