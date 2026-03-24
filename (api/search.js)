import express from 'express';
import TelegramBot from 'node-telegram-bot-api';
import mongoose from 'mongoose';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(express.json());
app.use(cors());
app.use(express.static('../public'));

// MongoDB (premium tekshiruvi)
mongoose.connect(process.env.MONGODB_URI);
const UserSchema = new mongoose.Schema({
  userId: { type: Number, unique: true },
  username: String,
  premiumUntil: Date
});
const User = mongoose.model('User', UserSchema);

// Telegram Bot
const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });

bot.on('message', async (msg) => {
  if (msg.web_app_data) {
    const data = JSON.parse(msg.web_app_data.data);
    if (data.action === 'search') {
      // Sening VKMUSICXBOT logikang – shu yerga o'z kodingni qo'y
      bot.sendMessage(msg.chat.id, `🔍 Ищу: ${data.query}\n\n🎵 Треки:\n1. ${data.query} - Artist1\n2. ${data.query} - Remix\n3. ${data.query} - 8D\n\n▶️ Нажмите для прослушивания`);
    } else if (data.action === 'manual_paid') {
      bot.sendMessage(YOUR_ADMIN_ID, `💳 Ручная оплата от @${data.user}`);
    }
  }
});

// FAKE search (real API siz)
app.get('/api/search', (req, res) => {
  const { query } = req.query;
  const fakeTracks = [
    { title: `${query} - Original`, artist: 'Artist 1', duration: '3:25', premium: false },
    { title: `${query} - 8D Remix`, artist: 'DJ Neo', duration: '4:12', premium: true },
    { title: `${query} - Speed Up`, artist: 'Remix Pro', duration: '2:58', premium: false },
    { title: `${query} - Bass Boost`, artist: 'Club Mix', duration: '3:45', premium: true }
  ];
  res.json({ success: true, tracks: fakeTracks });
});

app.get('/api/checkPremium', async (req, res) => {
  const userId = parseInt(req.query.userId);
  const user = await User.findOne({ userId });
  const isPremium = user && new Date(user.premiumUntil) > new Date();
  res.json({ isPremium });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server: ${PORT}`));
