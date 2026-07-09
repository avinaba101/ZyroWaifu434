# 1. Python का लेटेस्ट स्टेबल और लाइटवेट इमेज इस्तेमाल करें
FROM python:3.10-slim

# 2. सिस्टम के ज़रूरी टूल्स इंस्टॉल करें (जैसे git, ffmpeg आदि)
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. वर्किंग डायरेक्टरी सेट करें
WORKDIR /usr/src/app

# 4. requirements.txt फ़ाइल को कॉपी करें
COPY requirements.txt ./

# 5. बिना किसी एरर के सारे Python पैकेजेस इंस्टॉल करें
RUN pip install --no-cache-dir -r requirements.txt

# 6. प्रोजेक्ट के बाकी सारे कोड को कॉपी करें
COPY . .

# 7. बोट की मुख्य फ़ाइल (main.py) को रन करने की कमांड
CMD ["python", "-m", "TEAMZYRO.__main__"]

