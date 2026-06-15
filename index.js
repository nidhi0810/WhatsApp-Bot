const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason
} = require("@whiskeysockets/baileys");

const qrcode = require("qrcode-terminal");
const axios = require("axios");

async function startBot() {

    const { state, saveCreds } =
        await useMultiFileAuthState("auth");

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: false
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {

        const { connection, qr, lastDisconnect } = update;

        if (qr) {
            qrcode.generate(qr, {
                small: true
            });
        }

        if (connection === "open") {
            console.log("✅ WhatsApp Connected");
        }

        if (connection === "close") {

            const shouldReconnect =
                lastDisconnect?.error?.output?.statusCode !==
                DisconnectReason.loggedOut;

            console.log("❌ Connection Closed");

            if (shouldReconnect) {
                startBot();
            }
        }
    });

    sock.ev.on("messages.upsert", async ({ messages }) => {

        try {

            const msg = messages[0];

            if (!msg) return;
            if (!msg.message) return;
            if (msg.key.fromMe) return;

            const text =
                msg.message?.conversation ||
                msg.message?.extendedTextMessage?.text;

            if (!text) return;

            const sender = msg.key.remoteJid;
            const phone = msg.key.remoteJidAlt.split("@")[0];
            const name =msg.pushName ||"Unknown";
            
            console.log("Name:", name);
            console.log("Phone:", phone);
            console.log("================================");
            console.log("FROM :", sender);
            console.log("TEXT :", text);
            console.log("================================");
            //console.log(JSON.stringify(msg, null, 2));
            const response = await axios.post(
                "http://localhost:8000/chat",
                {
                    user_id: sender,
                    phone: phone,
                    name: name,
                    message: text
                },
                {
                    timeout: 60000
                }
            );

            const reply =
                response.data.reply ||
                "No response generated.";

            await sock.sendMessage(sender, {
                text: reply
            });

        } catch (err) {

            console.error("BOT ERROR:", err.message);

            try {
                await sock.sendMessage(
                    messages[0].key.remoteJid,
                    {
                        text: "⚠️ AI server unavailable."
                    }
                );
            } catch (_) {}
        }
    });
}

startBot();