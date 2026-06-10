require("dotenv").config();

const OpenAI = require("openai");

const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason
} = require("@whiskeysockets/baileys");

const qrcode = require("qrcode-terminal");

const client = new OpenAI({
    apiKey: process.env.OPENROUTER_API_KEY,
    baseURL: "https://openrouter.ai/api/v1",
    defaultHeaders: {
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "WhatsApp Bot"
    }
});

async function startBot() {

    const { state, saveCreds } =
        await useMultiFileAuthState("./auth");

    const sock = makeWASocket({
        auth: state,
        printQRInTerminal: false
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", async (update) => {

        const {
            connection,
            qr,
            lastDisconnect
        } = update;

        if (qr) {
            qrcode.generate(qr, { small: true });
        }

        if (connection === "open") {
            console.log("✅ WhatsApp Connected");
        }

        if (connection === "close") {

            console.log("❌ Connection Closed");

            const shouldReconnect =
                lastDisconnect?.error?.output?.statusCode !==
                DisconnectReason.loggedOut;

            if (shouldReconnect) {
                console.log("🔄 Reconnecting...");
                startBot();
            } else {
                console.log("Logged out");
            }
        }
    });

    sock.ev.on("messages.upsert", async ({ messages }) => {

        try {

            const msg = messages[0];

            if (!msg.message) return;

            if (msg.key.fromMe) return;

            const sender = msg.key.remoteJid;

            const text =
                msg.message.conversation ||
                msg.message.extendedTextMessage?.text;

            if (!text) return;

            console.log(`📩 ${sender}: ${text}`);

            await sock.sendPresenceUpdate(
                "composing",
                sender
            );

            const completion =
                await client.chat.completions.create({
                    model: "openai/gpt-4o-mini",
                    messages: [
                        {
                            role: "system",
                            content:
                                "You are a helpful WhatsApp assistant."
                        },
                        {
                            role: "user",
                            content: text
                        }
                    ]
                });

            const reply =
                completion.choices[0].message.content;

            await sock.sendMessage(sender, {
                text: reply
            });

            console.log(`🤖 ${reply}`);

        } catch (err) {

            console.error(err);

            try {
                await sock.sendMessage(
                    messages[0].key.remoteJid,
                    {
                        text:
                            "Something went wrong. Please try again."
                    }
                );
            } catch {}
        }
    });
}

startBot();