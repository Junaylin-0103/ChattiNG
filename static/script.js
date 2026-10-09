const socket = io();

const MAX_TEXT_LENGTH = 2000;
const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
const MAX_AUDIO_SIZE = 8 * 1024 * 1024;

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function appendMessage(data) {
    const chat = document.getElementById("chat");
    if (!chat) return;

    let html = '<div class="message"><strong>' + escapeHtml(data.user) + '</strong>:';

    if (data.type === "text") {
        html += '<div>' + escapeHtml(data.content) + '</div>';
    } else if (data.type === "image") {
        html += '<img src="' + data.content + '" alt="image" />';
    } else if (data.type === "voice") {
        html += '<audio controls src="' + data.content + '"></audio>';
    }

    if (data.created_at) {
        html += '<small>' + escapeHtml(data.created_at) + '</small>';
    }

    html += '</div>';
    chat.insertAdjacentHTML("beforeend", html);
    chat.scrollTop = chat.scrollHeight;
}

function sendText() {
    const input = document.getElementById("text");
    const msg = input.value.trim();

    if (!msg) return;
    if (msg.length > MAX_TEXT_LENGTH) {
        alert("文本消息过长");
        return;
    }

    socket.emit("message", { type: "text", content: msg });
    input.value = "";
}

function sendImage() {
    const file = document.getElementById("image").files[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
        alert("只能发送图片文件");
        return;
    }

    if (file.size > MAX_IMAGE_SIZE) {
        alert("图片不能超过 5MB");
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        socket.emit("message", { type: "image", content: reader.result });
        document.getElementById("image").value = "";
    };
    reader.readAsDataURL(file);
}

function sendVoice() {
    const file = document.getElementById("voice").files[0];
    if (!file) return;

    if (!file.type.startsWith("audio/")) {
        alert("只能发送音频文件");
        return;
    }

    if (file.size > MAX_AUDIO_SIZE) {
        alert("音频不能超过 8MB");
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        socket.emit("message", { type: "voice", content: reader.result });
        document.getElementById("voice").value = "";
    };
    reader.readAsDataURL(file);
}

socket.on("connect", () => {
    socket.emit("load_history");
});

socket.on("history", data => {
    const chat = document.getElementById("chat");
    if (!chat) return;
    chat.innerHTML = "";
    if (!data.messages) return;
    data.messages.forEach(msg => appendMessage(msg));
});

socket.on("message", data => {
    appendMessage(data);
});

socket.on("error", data => {
    alert(data.message || "发生错误");
});
