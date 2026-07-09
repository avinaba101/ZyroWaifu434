# हम यहाँ Debian 12 (Bookworm) आधारित लेटेस्ट और स्टेबल Node इमेज का इस्तेमाल कर रहे हैं
FROM node:18-bookworm-slim

# सिस्टम पैकेजेस को बिना किसी पुराने सर्वर एरर के अपडेट और इंस्टॉल करने के लिए
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["node", "index.js"]
