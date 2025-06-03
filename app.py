import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="חיזוי מגמת הזהב - Plus500", layout="centered")
st.title("🔮 חיזוי מגמה לזהב בפלוס 500")
st.write("ניתוח מגמה בטווח של חצי שעה קדימה לפי ניתוח טכני אמיתי")

@st.cache_data
def get_gold_data():
    gold = yf.download("GC=F", period="1d", interval="5m")
    return gold

def analyze_trend(df):
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_15'] = df['Close'].rolling(window=15).mean()
    df['RSI'] = compute_rsi(df['Close'], 14)
    df['MACD'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
    df['Signal'] = df['MACD'].ewm(span=9).mean()

    df = df.dropna().copy()

    if df.empty:
        return "אין מספיק נתונים", 0, df

    latest = df.iloc[[-1]]

    sma5 = latest['SMA_5'].values[0]
    sma15 = latest['SMA_15'].values[0]
    macd = latest['MACD'].values[0]
    signal = latest['Signal'].values[0]
    rsi = latest['RSI'].values[0]

    # דיאגנוסטיקה
    st.write("⚙️ בדיקת ערכים אחרונים:")
    st.write(f"SMA_5: {sma5} ({type(sma5)})")
    st.write(f"SMA_15: {sma15} ({type(sma15)})")
    st.write(f"MACD: {macd} ({type(macd)})")
    st.write(f"Signal: {signal} ({type(signal)})")
    st.write(f"RSI: {rsi} ({type(rsi)})")

    trend = "המתן"
    confidence = 50

    if isinstance(sma5, (int, float, np.float64)) and \
       isinstance(sma15, (int, float, np.float64)) and \
       isinstance(macd, (int, float, np.float64)) and \
       isinstance(signal, (int, float, np.float64)) and \
       isinstance(rsi, (int, float, np.float64)):

        if sma5 > sma15 and macd > signal and rsi < 70:
            trend = "קנייה"
            confidence = 80
        elif sma5 < sma15 and macd < signal and rsi > 30:
            trend = "מכירה"
            confidence = 80

    return trend, confidence, df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

try:
    df = get_gold_data()
    trend, confidence, df = analyze_trend(df)

    st.subheader("📈 גרף מחיר הזהב (5 דקות אחרונות)")
    st.line_chart(df['Close'])

    st.subheader("📊 המלצת מערכת:")
    st.write(f"**תחזית לעוד חצי שעה:** {trend}")
    st.write(f"**רמת ביטחון:** {confidence}%")

    if trend == "קנייה":
        st.success("המערכת ממליצה לבצע פעולת קנייה.")
    elif trend == "מכירה":
        st.error("המערכת ממליצה לבצע פעולת מכירה.")
    else:
        st.warning("אין המלצה מובהקת. המתן לאיתות ברור.")

except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")
