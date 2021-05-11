import pandas as pd
import requests
import json
import streamlit as st
import numpy as np
import datetime
from datetime import timedelta
from datetime import datetime
import plotly.graph_objects as go


def ValCuota(nombre,desde):

    if nombre=='Risky Norris':
        url='https://fintual.cl/api/real_assets/186/days?from_date='+desde

    elif nombre=='Moderate Pit':
        url='https://fintual.cl/api/real_assets/187/days?from_date='+desde

    elif nombre=='Conservative Clooney':
        url='https://fintual.cl/api/real_assets/188/days?from_date='+desde


    r = requests.get(url)
    j=r.json()
    df=pd.json_normalize(j['data'])
    df=df[['attributes.date','attributes.price']]
    df.columns=['fecha','precio']

    df['fecha']=pd.to_datetime(df.fecha)
    df.sort_values(by='fecha',inplace=True,ascending=False)
    df.reset_index(inplace=True,drop=True)
    df['diff']=df.precio-df.precio.shift(-4)
    df['prom']=df[::-1].precio.rolling(30).mean()[::-1]
    df['desvest']=df[::-1].precio.rolling(30).std()[::-1]
    df['bolup']=df.prom+2.5*df.desvest
    df['boldown']=df.prom-2.5*df.desvest
    df['flip']=df['diff'].apply(lambda x: 1 if x<0 else 0)
    df['DM']=df[::-1].flip.rolling(9).sum()[::-1]

    return df


@st.cache(allow_output_mutation=True)
def Mono(df):

        fig = go.Figure(width=800, height=400)

        fig.add_trace(go.Scatter(x=df.fecha,
                                y=df.precio,
                                mode='lines',
                                name='Valor Cuota'
                            )
                    )

        fig.add_trace(go.Scatter(x=df.fecha,
                                y=df.bolup,
                                line=dict(color='red',dash='dash'),
                                name='Bol Up'
                                )
                    )

        fig.add_trace(go.Scatter(x=df.fecha,
                            y=df.boldown,
                            line=dict(color='red',dash='dash'),
                            name='Bol Down'
                        )
                    )


        annotations = []


        annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.1,
                              xanchor='center', yanchor='top',
                              text='Fuente: API Fintual',
                              font=dict(family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                              showarrow=False))



        fig.update_layout(annotations=annotations,title='Evolución Valor Cuota ')

        return fig

hoy=datetime.today()
anno_pasado=hoy-timedelta(days=365)#Desde el año pasado, como referencia

inicio= st.sidebar.date_input('Fecha de inicio',value=anno_pasado)
inicio = inicio.strftime("%Y-%m-%d")

nombre_fondo=st.sidebar.selectbox('Elige tu fondo',('Risky Norris','Moderate Pit','Conservative Clooney'))


data = ValCuota(nombre_fondo,inicio)

st.plotly_chart(Mono(data))
#st.write(data[['fecha','precio']])
