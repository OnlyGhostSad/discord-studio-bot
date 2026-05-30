# Discord - Studio Bot & Server Setup

Bu klasör tüm Discord ile ilgili dosyaları içerir.

## 📁 Dosyalar

### Bot Dosyaları
- `bot.js` - Node.js Discord bot (Gemini AI)
- `package.json` - Node.js bağımlılıkları
- `Procfile` - Render deployment

### Konfigürasyon
- `.env` - Gizli ayarlar (TOKEN, API KEY, vb) - **GİTHUB'A YÜKLENMEZ**

### Dokümantasyon
- `README.md` - Bu dosya

## 🚀 Hızlı Başlangıç

### 1. Bot Kurulumu (Lokal)

```bash
# Node.js bağımlılıklarını yükle
npm install

# .env dosyasını doldur (token ve API key)

# Botu çalıştır
npm start
```

### 2. Render'da Deploy

1. GitHub'a push et
2. Render.com'da yeni Web Service oluştur
3. Repository'yi seç
4. Environment variables ekle (.env'deki değerler)
5. Deploy et!

## 📝 Komutlar

### Herkes Kullanabilir
| Komut | Açıklama |
|-------|----------|
| `/help` | Tüm komutları göster |
| `/help-ai <soru>` | AI'ya kurallar hakkında sor |
| `/rules` | Studio kurallarını göster |
| `/info` | Studio hakkında bilgi |

### Moderatör Komutları
| Komut | Açıklama |
|-------|----------|
| `/assign-role <member> <role>` | Üyeye rol ata |
| `/mute <member> <dakika>` | Üyeyi sustur |
| `/kick <member> <sebep>` | Üyeyi sunucudan çıkar |
| `/ban <member> <sebep>` | Üyeyi yasakla |

### Sahip Komutları
| Komut | Açıklama |
|-------|----------|
| `/announce <mesaj>` | Duyuru gönder |
| `/update <info>` | Güncelleme paylaş |

## 🔐 Güvenlik

- `.env` dosyası **GİTHUB'A YÜKLENMEZ** (.gitignore'da)
- Token'ları asla paylaşma
- API key'leri gizli tut

## 🎯 Özellikler

### Bot
- 🤖 AI Asistan (Gemini)
- 📋 Kurallar Sistemi
- 💬 Help AI Komutu
- 👤 Otomatik Rol Atama
- 🔇 Mute/Kick/Ban Komutları
- 📢 Duyuru Sistemi
- 🔄 Güncelleme Paylaşımı
- 🌐 Web Server (Render'da canlı kalması için)

### Komut Özellikleri
- Slash commands (/)
- Ephemeral replies (gizli mesajlar)
- Embed mesajlar
- Moderator permissions
- Owner-only commands

## 💡 İpuçları

- Bot'u Render'da çalıştırmak için Procfile gerekli
- Web server otomatik olarak port 8000'de açılır
- AI asistan kuralları öğrenmiş şekilde cevap verir
- Tüm komutlar slash command olarak çalışır

## 🆘 Sorun Giderme

**Bot çalışmıyor:**
- `.env` dosyası dolduruldu mu?
- Token'lar doğru mu?
- `npm install` çalıştırdın mı?

**Komutlar görünmüyor:**
- Bot'u restart et
- Slash commands 1-2 dakika sürebilir

**Render'da deploy başarısız:**
- Environment variables doğru mu?
- Node.js 18.x kullanıyor mu?

---

**Hazır!** Discord bot Node.js'e çevrildi. 🚀
