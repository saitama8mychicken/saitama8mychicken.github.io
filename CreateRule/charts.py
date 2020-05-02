import pandas as pd
import matplotlib.pyplot as plt
from django.conf import settings
from CreateRule.models import *
import io
import base64
import urllib.parse


def chart(df, output=dict()):
    plt.clf()
    try:
        if output.get('type') == 'plot':
            plt.plot(df[output.get('x_axis')], df[output.get('y_axis')])
        elif output.get('type') == 'bar':
            plt.bar(df[output.get('x_axis')], df[output.get('y_axis')])
        elif output.get('type') == 'area':
            plt.plot(df[output.get('x_axis')], df[output.get('y_axis')])
        elif output.get('type') == 'boxplot':
            plt.boxplot(df[output.get('x_axis')], df[output.get('y_axis')])
        else:
            print('unable to process')
        fig = plt.gcf()
        # convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
    except:
        fig = plt.gcf()
        # convert graph into dtring buffer and then we convert 64 bit code into image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)


    return uri

