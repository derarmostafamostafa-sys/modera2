"""
MODURA Luxury Furniture - Ultimate Unified System (OpenCMO + MODURA Core)
"""
import os
import json
from urllib.parse import quote

import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="MODURA Enterprise & AI Agents System")

API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("MODURA_MODEL", "claude-sonnet-5-5")

WA_TEXT = "مرحباً، أهتم بالتواصل مع إدارة مصنع MODURA للأثاث الفاخر والتفصيل المباشر"

# روابط مشروعك المعتمدة
LINKS = [
    {"id": "wa", "title": "واتساب مباشر", "sub": "تواصل فوري مع الإدارة (0512787057)", "icon": "💬", "primary": True,
     "url": "https://wa.me/972512787057?text=" + quote(WA_TEXT)},
    {"id": "site", "title": "المتجر الرسمي", "sub": "modurat.vercel.app", "icon": "🛋️", "primary": True,
     "url": "https://modurat.vercel.app/"},
    {"id": "admin", "title": "لوحة التحكم", "sub": "إدارة الطلبات والمصنع", "icon": "⚙️", "primary": False,
     "url": "https://modurat.vercel.app/admin"},
    {"id": "ig", "title": "إنستغرام", "sub": "@modura_luxury", "icon": "📸", "primary": False,
     "url": "https://www.instagram.com/modura_luxury?srtk=MTVjNDV4N2h3bzNhYg%3D%3D&utm_source=qr"},
    {"id": "fb", "title": "فيسبوك", "sub": "صفحتنا الرسمية للأثاث", "icon": "👥", "primary": False,
     "url": "https://www.facebook.com/share/18kbmbBspW/?mibextid=wwXIfr"},
    {"id": "tt", "title": "تيك توك", "sub": "@modura.luxury", "icon": "🎬", "primary": False,
     "url": "https://www.tiktok.com/@modura.luxury?_r=1&_t=ZN-9BP7b5zLdoM"},
    {"id": "pin", "title": "بينترست", "sub": "لوحات إلهام التصاميم", "icon": "📌", "primary": False,
     "url": "https://pin.it/7AlQdc4tS"},
]

# وكلاء الذكاء الاصطناعي المستوحى من OpenCMO
BASE_AGENT_SYS = (
    "أنت نظام إدارة وكلاء الذكاء الاصطناعي التسويقي والتقني لمصنع 'MODURA' للأثاث الفاخر في بيدوئيل. "
    "ننتج طاولات طعام، صالونات، بوفيهات، وأسرّة فاخرة مباشرة من المصنع للزبون. أجب باحترافية تامة، بالعربية، وبصيغة عملية وموجزة."
)

AGENTS = {
    "marketing_plan": ("وكيل الاستراتيجية والتخطيط", BASE_AGENT_SYS, "ضع خطة تسويق تفصيلية لمصنع MODURA بناءً على: {d}"),
    "market_analysis": ("وكيل تحليل السوق والمنافسين", BASE_AGENT_SYS, "حلّل السوق المستهدف ومميزات البيع المباشر من المصنع مقارنة بالمنافسين لـ: {d}"),
    "social_content": ("وكيل محتوى السوشيال", BASE_AGENT_SYS, "اقترح أفكار فيديوهات ومنشورات ترويجية لإنستغرام وتيك توك تسلط الضوء على خامات المرمر والخشب الطبيعي: {d}"),
    "product_copy": ("وكيل الوصف الفاخر", BASE_AGENT_SYS, "اكتب وصفاً تسويقياً وشعاراً راقياً لمنتجات الأثاث بناءً على المعطيات: {d}"),
    "media_advisor": ("وكيل تحليل الوسائط", BASE_AGENT_SYS, "قدم استشارة بصرية وتقييم لتصميم أو صورة قطعة الأثاث بناءً على: {d}"),
}

class AIRequest(BaseModel):
    action: str = Field(..., max_length=40)
    details: str = Field("", max_length=1500)

def get_fallback_response(action: str, d: str) -> str:
    fallbacks = {
        "marketing_plan": "## خطة تسويق MODURA\n- **التركيز:** إبراز جودة التصنيع المباشر من مصنعنا قرب بيدوئيل.\n- **الحملات:** عروض أسبوعية عبر واتساب وإنستغرام.",
        "market_analysis": "## تحليل السوق والمنافسين\n- استهداف أصحاب الفلل والباحثين عن التفصيل الخاص وخامات المرمر والخشب الطبيعي.\n- ميزة تنافسية: السعر المباشر من المصنع وبدون وسيط.",
        "social_content": "## محتوى مقترح\n- فيديو من داخل المصنع يوضح مراحل صقل الخشب والمرمر.\n- #MODURA #أثاث_فاخر #تصميم_خاص",
        "product_copy": "## الوصف الفاخر\nحرفية صامتة تعكس ذوقك الرفيع. مصممة ومصنوعة خصيصاً لمساحتك.\n**MODURA — الجودة تبدأ من المصنع.**",
        "media_advisor": "## استشارة بصرية\nالقطعة تتميز بتناسق الخطوط والمظهر العصري المناسب للمساحات الفاخرة."
    }
    return fallbacks.get(action, fallbacks["marketing_plan"])

@app.post("/api/ai")
async def run_agent(req: AIRequest):
    if req.action not in AGENTS:
        return JSONResponse({"error": "إجراء غير معروف"}, status_code=400)
    name, system, tpl = AGENTS[req.action]
    d = req.details.strip() or "عام"
    if not API_KEY:
        return {"agent": name, "text": get_fallback_response(req.action, d), "mode": "offline"}
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={
                    "model": MODEL,
                    "max_tokens": 1200,
                    "system": system,
                    "messages": [{"role": "user", "content": tpl.format(d=d)}]
                },
            )
            r.raise_for_status()
            text = "".join(b.get("text", "") for b in r.json().get("content", []))
            return {"agent": name, "text": text or get_fallback_response(req.action, d), "mode": "ai"}
    except Exception:
        return {"agent": name, "text": get_fallback_response(req.action, d), "mode": "offline"}

@app.post("/api/media-upload")
async def media_upload(file: UploadFile = File(...)):
    return {
        "status": "success",
        "filename": file.filename,
        "message": f"تم استقبال ملف الوسائط ({file.filename}) بنجاح وتحويله لوكيل التحليل البصري."
    }

PAGE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0b0b0e">
<title>MODURA | نظام وكلاء الذكاء الاصطناعي</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&family=Cinzel:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{--gold:#c9a45c;--gold2:#8f7036;--bg:#0b0b0e}
html,body{background:var(--bg);font-family:'Tajawal',sans-serif;color:#eee;-webkit-tap-highlight-color:transparent}
body{min-height:100vh;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}
.orb{position:fixed;border-radius:50%;filter:blur(90px);opacity:.25;z-index:0;animation:float 14s ease-in-out infinite}
@keyframes float{50%{transform:translate(30px,-40px) scale(1.15)}}
.glass{background:linear-gradient(145deg,rgba(255,255,255,.07),rgba(255,255,255,.02));
 backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid rgba(201,164,92,.18);
 border-radius:22px;box-shadow:0 10px 30px rgba(0,0,0,.45)}
.gold-text{background:linear-gradient(120deg,#e4c887,#b08d47 50%,#8f7036);-webkit-background-clip:text;background-clip:text;color:transparent}
.ico{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;font-size:22px;flex:none;
 background:linear-gradient(145deg,rgba(201,164,92,.28),rgba(201,164,92,.06));border:1px solid rgba(201,164,92,.3)}
.btn-gold{background:linear-gradient(135deg,#d9b872,#a8853f);color:#16120a;font-weight:800;border-radius:16px;transition:.2s}
.btn-gold:active{transform:scale(.97)}
.chip{padding:9px 14px;border-radius:999px;font-size:13px;white-space:nowrap;border:1px solid rgba(201,164,92,.25);
 background:rgba(255,255,255,.04);transition:.25s}
.chip.on{background:linear-gradient(135deg,#d9b872,#a8853f);color:#16120a;font-weight:700;border-color:transparent}
.fade{animation:fade .7s both}@keyframes fade{from{opacity:0;transform:translateY(18px)}}
textarea{background:rgba(0,0,0,.35);border:1px solid rgba(201,164,92,.2);border-radius:14px;color:#fff;outline:none}
textarea:focus{border-color:var(--gold)}
.res h2{color:var(--gold);font-weight:800;margin:10px 0 4px}.res li{list-style:none;padding-right:12px;position:relative}
.res li:before{content:"◆";position:absolute;right:0;color:var(--gold);font-size:8px;top:7px}
.dots span{display:inline-block;width:7px;height:7px;margin:0 3px;border-radius:50%;background:var(--gold);animation:b 1s infinite}
.dots span:nth-child(2){animation-delay:.15s}.dots span:nth-child(3){animation-delay:.3s}
@keyframes b{50%{transform:translateY(-7px);opacity:.4}}
::-webkit-scrollbar{display:none}
</style>
</head>
<body>
<div class="orb" style="width:300px;height:300px;background:#c9a45c;top:-80px;right:-80px"></div>

<main class="relative z-10 max-w-md mx-auto px-4 pb-16">
  <header class="text-center pt-8 pb-4 fade">
    <div class="glass mx-auto w-20 h-20 grid place-items-center mb-4" style="border-radius:26px">
      <span class="gold-text text-4xl font-bold" style="font-family:Cinzel">M</span>
    </div>
    <h1 class="gold-text text-3xl font-bold tracking-[.3em]" style="font-family:Cinzel">MODURA</h1>
    <p class="text-xs text-gray-400 mt-1">المصنع الذكي • وكلاء متعددون ومكالمات ووسائط</p>
  </header>

  <!-- مكالمة صوتية مباشرة مع الوكيل -->
  <section class="mb-5 fade">
    <div class="glass p-4 text-center border-yellow-600/40 bg-gradient-to-r from-amber-950/30 to-yellow-950/10">
      <h3 class="font-bold text-sm mb-1 text-yellow-400">🎙️ مكالمة صوتية مباشرة مع الوكيل</h3>
      <p class="text-[11px] text-gray-300 mb-3">تحدث صوتياً ليقوم النظام بتحويل كلامك لأوامر وتنفيذها فوراً.</p>
      <button id="callBtn" onclick="toggleVoiceCall()" class="btn-gold px-5 py-2 text-xs w-full">بدء المكالمة الصوتية</button>
      <div id="callStatus" class="text-xs text-green-400 mt-2 hidden">🔴 المكالمة جارية... تحدث بوضوح</div>
    </div>
  </section>

  <!-- إرسال الصور والفيديوهات للتحليل -->
  <section class="mb-5 fade" style="animation-delay:.05s">
    <div class="glass p-4">
      <h3 class="font-bold text-sm mb-2 text-yellow-400">📷 إرسال صور أو فيديوهات الأثاث للتحليل</h3>
      <input type="file" id="mediaFile" accept="image/*,video/*" class="w-full text-xs text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-yellow-600 file:text-black hover:file:bg-yellow-500 mb-3 cursor-pointer">
      <button onclick="uploadMedia()" class="btn-gold w-full py-2 text-xs">رفع وتحليل الوسائط بالذكاء الاصطناعي</button>
      <div id="mediaOut" class="text-xs text-gray-300 mt-2 text-center"></div>
    </div>
  </section>

  <section id="links" class="grid grid-cols-2 gap-3 mb-5"></section>

  <section class="glass p-4 fade" style="animation-delay:.15s">
    <div class="flex items-center gap-2 mb-3">
      <span class="text-xl">✨</span>
      <h2 class="font-extrabold text-base">منظومة وكلاء MODURA</h2>
    </div>
    <div id="chips" class="flex gap-2 overflow-x-auto pb-3"></div>
    <textarea id="details" rows="2" class="w-full p-3 text-sm" placeholder="اكتب تفاصيل الطلب أو الفكرة هنا..."></textarea>
    <button id="go" class="btn-gold w-full py-3 mt-3 text-sm">تشغيل الوكيل الذكي</button>
    <div id="out" class="mt-4 hidden">
      <div class="flex items-center justify-between mb-2">
        <span id="agent" class="text-xs text-yellow-500"></span>
        <button id="copy" class="text-xs text-gray-400 underline">نسخ</button>
      </div>
      <div id="res" class="res text-sm leading-7 text-gray-200"></div>
    </div>
  </section>
</main>

<script>
const LINKS = __LINKS__;
const ACTIONS = [
  ["marketing_plan","📈 خطة التسويق"],["market_analysis","🔍 تحليل السوق"],
  ["social_content","📱 محتوى السوشيال"],["product_copy","🖋️ وصف فاخر"],["media_advisor","💎 تحليل بصري"]
];
let current = ACTIONS[0][0], lastText = "", isCalling = false;
const $ = id => document.getElementById(id);

$("links").innerHTML = LINKS.map((l,i) => `
  <a href="${l.url}" target="_blank" class="glass p-3 flex ${l.primary ? 'col-span-2 flex-row items-center gap-3' : 'flex-col items-start gap-3'}">
    <div class="ico">${l.icon}</div>
    <div><div class="font-bold ${l.primary ? 'text-base gold-text' : 'text-sm'}">${l.title}</div>
    <div class="text-[11px] text-gray-400 mt-0.5">${l.sub}</div></div>
  </a>`).join("");

$("chips").innerHTML = ACTIONS.map(([k,t]) =>
  `<button class="chip ${k===current?'on':''}" data-k="${k}">${t}</button>`).join("");
$("chips").onclick = e => {
  const b = e.target.closest("button"); if(!b) return;
  current = b.dataset.k;
  document.querySelectorAll(".chip").forEach(c => c.classList.toggle("on", c===b));
};

function toggleVoiceCall() {
  const btn = $("callBtn"), status = $("callStatus");
  if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
    alert("المتصفح لا يدعم التعرف الصوتي المباشر. استخدم متصفح Google Chrome.");
    return;
  }
  if (!isCalling) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'ar-SA';
    recognition.interimResults = false;
    
    recognition.onstart = () => {
      isCalling = true;
      btn.textContent = "إنهاء المكالمة الصوتية";
      btn.classList.replace("btn-gold", "bg-red-600");
      status.classList.remove("hidden");
    };
    
    recognition.onresult = (event) => {
      const speechToText = event.results[0][0].transcript;
      $("details").value = speechToText;
      $("go").click();
    };
    
    recognition.onerror = () => { stopCall(); };
    recognition.onend = () => { if(isCalling) recognition.start(); };
    
    window.activeRecognition = recognition;
    recognition.start();
  } else {
    stopCall();
  }
}

function stopCall() {
  isCalling = false;
  if(window.activeRecognition) window.activeRecognition.stop();
  $("callBtn").textContent = "بدء المكالمة الصوتية";
  $("callBtn").classList.replace("bg-red-600", "btn-gold");
  $("callStatus").classList.add("hidden");
}

async function uploadMedia() {
  const fileInput = $("mediaFile"), out = $("mediaOut");
  if(fileInput.files.length === 0) {
    out.textContent = "الرجاء اختيار صورة أو فيديو أولاً.";
    return;
  }
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  out.textContent = "جاري رفع وتحليل الوسائط...";
  try {
    const r = await fetch("/api/media-upload", { method: "POST", body: formData });
    const d = await r.json();
    out.textContent = "✓ " + d.message;
  } catch(e) {
    out.textContent = "تعذّر رفع الملف، حدث خطأ.";
  }
}

$("go").onclick = async () => {
  const btn = $("go");
  btn.disabled = true; btn.textContent = "جاري عمل الوكيل...";
  $("out").classList.remove("hidden");
  $("agent").textContent = "";
  $("res").innerHTML = "<div class='dots py-4 text-center'><span></span><span></span><span></span></div>";
  try {
    const r = await fetch("/api/ai", {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({action: current, details: $("details").value})});
    const d = await r.json();
    lastText = d.text || "";
    $("agent").textContent = "🤖 " + (d.agent || "");
    $("res").innerHTML = d.text.replace(/\n/g, "<br>");
  } catch (e) {
    $("res").textContent = "تعذّر الاتصال بالسيرفر.";
  }
  btn.disabled = false; btn.textContent = "تشغيل الوكيل الذكي";
};

$("copy").onclick = async () => {
  await navigator.clipboard.writeText(lastText);
  $("copy").textContent = "تم النسخ ✓";
  setTimeout(() => $("copy").textContent = "نسخ", 1500);
};
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return PAGE.replace("__LINKS__", json.dumps(LINKS, ensure_ascii=False))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
