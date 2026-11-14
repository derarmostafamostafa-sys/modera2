"""
MODURA Luxury Furniture - Mobile Web App (FastAPI)

التثبيت:   pip install fastapi uvicorn httpx
التشغيل:   uvicorn app:app --host 0.0.0.0 --port 8000
الذكاء الاصطناعي (اختياري): export ANTHROPIC_API_KEY="sk-ant-..."
بدون مفتاح يعمل التطبيق بوضع احتياطي (قوالب جاهزة) دون أي أخطاء.
"""
import os
import json
from urllib.parse import quote

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="MODURA Luxury App")

API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("MODURA_MODEL", "claude-sonnet-5-5")

WA_TEXT = "مرحباً، أهتم بالتواصل مع إدارة مصنع MODURA للأثاث الفاخر"

LINKS = [
    {"id": "wa", "title": "واتساب مباشر", "sub": "تواصل فوري مع الإدارة", "icon": "💬", "primary": True,
     "url": "https://wa.me/972512787057?text=" + quote(WA_TEXT)},
    {"id": "site", "title": "المتجر الرسمي", "sub": "تصفح المجموعات الفاخرة", "icon": "🛋️", "primary": True,
     "url": "https://modurat.vercel.app/"},
    {"id": "admin", "title": "لوحة التحكم", "sub": "الإدارة والطلبات", "icon": "⚙️", "primary": False,
     "url": "https://modurat.vercel.app/admin"},
    {"id": "ig", "title": "إنستغرام", "sub": "@modura_luxury", "icon": "📸", "primary": False,
     "url": "https://www.instagram.com/modura_luxury?srtk=MTVjNDV4N2h3bzNhYg%3D%3D&utm_source=qr"},
    {"id": "fb", "title": "فيسبوك", "sub": "صفحتنا الرسمية", "icon": "👥", "primary": False,
     "url": "https://www.facebook.com/share/18kbmbBspW/?mibextid=wwXIfr"},
    {"id": "tt", "title": "تيك توك", "sub": "@modura.luxury", "icon": "🎬", "primary": False,
     "url": "https://www.tiktok.com/@modura.luxury?_r=1&_t=ZN-9BP7b5zLdoM"},
    {"id": "pin", "title": "بينترست", "sub": "إلهام التصاميم", "icon": "📌", "primary": False,
     "url": "https://pin.it/7AlQdc4tS"},
]

BASE = ("أنت جزء من فريق وكلاء ذكاء اصطناعي لمصنع أثاث فاخر اسمه MODURA. "
        "أجب بالعربية الفصحى المبسطة، بتنسيق منظم (عناوين ## ونقاط -)، عملي وموجز، دون مقدمات.")

AGENTS = {
    "marketing_plan": ("وكيل الاستراتيجية",
        BASE + " دورك: خبير استراتيجية تسويق للأثاث الفاخر.",
        "ضع خطة تسويق لمدة 30 يوماً لمصنع MODURA. تفاصيل إضافية: {d}\n"
        "تشمل: الجمهور المستهدف، القنوات، جدول أسبوعي، ميزانية تقريبية، مؤشرات النجاح."),
    "market_analysis": ("وكيل تحليل السوق",
        BASE + " دورك: محلل سوق أثاث فاخر.",
        "حلّل سوق الأثاث الفاخر لمصنع MODURA. تفاصيل: {d}\n"
        "تشمل: الشرائح، المنافسون، الفرص، المخاطر، نقاط التميّز المقترحة."),
    "social_content": ("وكيل المحتوى",
        BASE + " دورك: كاتب محتوى سوشيال ميديا فاخر.",
        "اكتب 5 أفكار منشورات/فيديوهات لإنستغرام وتيك توك وبينترست مع نص جذاب وهاشتاقات. تفاصيل: {d}"),
    "product_copy": ("وكيل الوصف الفاخر",
        BASE + " دورك: كاتب إعلانات فاخرة.",
        "اكتب وصفاً تسويقياً فاخراً (80 كلمة) وشعاراً قصيراً للمنتج التالي: {d}"),
    "pricing": ("وكيل التسعير",
        BASE + " دورك: خبير تسعير وعروض.",
        "اقترح استراتيجية تسعير وعروض موسمية راقية لا تضر بصورة العلامة. تفاصيل: {d}"),
}


class AIRequest(BaseModel):
    action: str = Field(..., max_length=40)
    details: str = Field("", max_length=1500)


def fallback(action: str, d: str) -> str:
    extra = f"\n\n> ملاحظة السياق: {d}" if d else ""
    plans = {
        "marketing_plan": "## خطة 30 يوماً\n- **الأسبوع 1:** تصوير سينمائي للمنتجات الأكثر مبيعاً ونشر قصة العلامة.\n"
        "- **الأسبوع 2:** فيديوهات «خلف الكواليس» من المصنع على تيك توك وإنستغرام.\n"
        "- **الأسبوع 3:** لوحات إلهام على بينترست مع روابط مباشرة للمتجر.\n"
        "- **الأسبوع 4:** عرض حصري للمتابعين عبر واتساب.\n## المؤشرات\n- رسائل واتساب، زيارات المتجر، التفاعل.",
        "market_analysis": "## تحليل مختصر\n- **الجمهور:** ملاك الفلل والمصممون الداخليون.\n"
        "- **الفرص:** التفصيل حسب الطلب، الخامات الفاخرة، المحتوى المرئي.\n"
        "- **المخاطر:** المنافسة السعرية، طول مدة التسليم.\n- **التميّز:** الحرفية + الخدمة الشخصية عبر واتساب.",
        "social_content": "## أفكار المحتوى\n- فيديو: من الخشب الخام إلى القطعة الفاخرة.\n- كاروسيل: ركن المعيشة المثالي.\n"
        "- ريل: قبل/بعد تجديد غرفة.\n- لوحة بينترست: ألوان الذهب والمخمل.\n- #MODURA #أثاث_فاخر",
        "product_copy": "## الوصف\nقطعة تجمع بين الأناقة الصامتة والحرفية الراقية، صُنعت لتمنح مساحتك حضوراً لا يُنسى.\n"
        "**الشعار:** MODURA — حيث يلتقي الفخامة بالراحة.",
        "pricing": "## استراتيجية التسعير\n- تسعير قيمة (Value-Based) يبرز الخامة والتصنيع.\n"
        "- باقات غرف كاملة بدل خصومات مباشرة.\n- عروض موسمية محدودة العدد لصناعة الندرة.",
    }
    return plans.get(action, plans["marketing_plan"]) + extra


@app.post("/api/ai")
async def ai(req: AIRequest):
    if req.action not in AGENTS:
        return JSONResponse({"error": "إجراء غير معروف"}, status_code=400)
    name, system, tpl = AGENTS[req.action]
    d = req.details.strip() or "لا توجد"
    if not API_KEY:
        return {"agent": name, "text": fallback(req.action, req.details.strip()), "mode": "offline"}
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": MODEL, "max_tokens": 1200, "system": system,
                      "messages": [{"role": "user", "content": tpl.format(d=d)}]},
            )
            r.raise_for_status()
            text = "".join(b.get("text", "") for b in r.json().get("content", []))
            return {"agent": name, "text": text or fallback(req.action, d), "mode": "ai"}
    except Exception:
        return {"agent": name, "text": fallback(req.action, req.details.strip()), "mode": "offline"}


@app.get("/health")
async def health():
    return {"status": "ok"}


PAGE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0b0b0e">
<title>MODURA | أثاث فاخر</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&family=Cinzel:wght@500;700&display=swap" rel="stylesheet">
<style>
:root{--gold:#c9a45c;--gold2:#8f7036;--bg:#0b0b0e}
html,body{background:var(--bg);font-family:'Tajawal',sans-serif;color:#eee;-webkit-tap-highlight-color:transparent}
body{min-height:100vh;padding:env(safe-area-inset-top) 0 env(safe-area-inset-bottom)}
.orb{position:fixed;border-radius:50%;filter:blur(90px);opacity:.28;z-index:0;animation:float 14s ease-in-out infinite}
@keyframes float{50%{transform:translate(30px,-40px) scale(1.15)}}
.glass{background:linear-gradient(145deg,rgba(255,255,255,.08),rgba(255,255,255,.02));
 backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid rgba(201,164,92,.18);
 border-radius:22px;box-shadow:0 10px 30px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.07);
 transition:transform .35s cubic-bezier(.2,.8,.2,1),border-color .3s,box-shadow .3s}
a.glass:hover,button.glass:hover{border-color:rgba(201,164,92,.55);box-shadow:0 14px 36px rgba(201,164,92,.12)}
a.glass:active,button.glass:active{transform:scale(.96)}
.gold-text{background:linear-gradient(120deg,#e4c887,#b08d47 50%,#8f7036);-webkit-background-clip:text;background-clip:text;color:transparent}
.ico{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;font-size:22px;flex:none;
 background:linear-gradient(145deg,rgba(201,164,92,.28),rgba(201,164,92,.06));border:1px solid rgba(201,164,92,.3)}
.btn-gold{background:linear-gradient(135deg,#d9b872,#a8853f);color:#16120a;font-weight:800;border-radius:16px;
 transition:transform .2s,opacity .2s}
.btn-gold:active{transform:scale(.97)}.btn-gold:disabled{opacity:.5}
.chip{padding:9px 14px;border-radius:999px;font-size:13px;white-space:nowrap;border:1px solid rgba(201,164,92,.25);
 background:rgba(255,255,255,.04);transition:.25s}
.chip.on{background:linear-gradient(135deg,#d9b872,#a8853f);color:#16120a;font-weight:700;border-color:transparent}
.fade{animation:fade .7s both}@keyframes fade{from{opacity:0;transform:translateY(18px)}}
textarea{background:rgba(0,0,0,.35);border:1px solid rgba(201,164,92,.2);border-radius:14px;color:#fff;outline:none}
textarea:focus{border-color:var(--gold)}
.res h2{color:var(--gold);font-weight:800;margin:10px 0 4px}.res li{margin:4px 0;list-style:none;padding-right:14px;position:relative}
.res li:before{content:"◆";position:absolute;right:0;color:var(--gold);font-size:8px;top:7px}
.dots span{display:inline-block;width:7px;height:7px;margin:0 3px;border-radius:50%;background:var(--gold);animation:b 1s infinite}
.dots span:nth-child(2){animation-delay:.15s}.dots span:nth-child(3){animation-delay:.3s}
@keyframes b{50%{transform:translateY(-7px);opacity:.4}}
::-webkit-scrollbar{display:none}
</style>
</head>
<body>
<div class="orb" style="width:300px;height:300px;background:#c9a45c;top:-80px;right:-80px"></div>
<div class="orb" style="width:260px;height:260px;background:#5b3f1a;bottom:10%;left:-90px;animation-delay:-6s"></div>

<main class="relative z-10 max-w-md mx-auto px-4 pb-16">
  <header class="text-center pt-10 pb-6 fade">
    <div class="glass mx-auto w-20 h-20 grid place-items-center mb-4" style="border-radius:26px">
      <span class="gold-text text-4xl font-bold" style="font-family:Cinzel">M</span>
    </div>
    <h1 class="gold-text text-4xl font-bold tracking-[.3em]" style="font-family:Cinzel">MODURA</h1>
    <p class="text-sm text-gray-400 mt-2 tracking-wide">مصنع الأثاث الفاخر • حيث تلتقي الأناقة بالحرفة</p>
  </header>

  <section id="links" class="grid grid-cols-2 gap-3"></section>

  <section class="mt-8 fade" style="animation-delay:.3s">
    <div class="flex items-center gap-2 mb-3 px-1">
      <span class="text-xl">✨</span>
      <h2 class="font-extrabold text-lg">مساعد MODURA الذكي</h2>
      <span class="text-[11px] px-2 py-0.5 rounded-full border border-yellow-700/40 text-yellow-500">Multi-Agent</span>
    </div>
    <div class="glass p-4">
      <div id="chips" class="flex gap-2 overflow-x-auto pb-3"></div>
      <textarea id="details" rows="3" class="w-full p-3 text-sm"
        placeholder="أضف تفاصيل (اختياري): نوع المنتج، الميزانية، المدينة، الجمهور..."></textarea>
      <button id="go" class="btn-gold w-full py-3.5 mt-3 text-base">توليد الآن</button>
      <div id="out" class="mt-4 hidden">
        <div class="flex items-center justify-between mb-2">
          <span id="agent" class="text-xs text-yellow-500"></span>
          <button id="copy" class="text-xs text-gray-400 underline">نسخ</button>
        </div>
        <div id="res" class="res text-sm leading-7 text-gray-200"></div>
      </div>
    </div>
  </section>

  <footer class="text-center text-xs text-gray-600 mt-10">© MODURA Luxury Furniture</footer>
</main>

<script>
const LINKS = __LINKS__;
const ACTIONS = [
  ["marketing_plan","📈 خطة تسويق"],["market_analysis","🔍 تحليل السوق"],
  ["social_content","📱 محتوى سوشيال"],["product_copy","🖋️ وصف فاخر"],["pricing","💎 التسعير"]
];
let current = ACTIONS[0][0], lastText = "";
const $ = id => document.getElementById(id);

$("links").innerHTML = LINKS.map((l,i) => `
  <a href="${l.url}" target="_blank" rel="noopener noreferrer"
     class="glass fade p-4 flex ${l.primary ? 'col-span-2 flex-row items-center gap-3' : 'flex-col items-start gap-3'}"
     style="animation-delay:${i*70}ms">
    <div class="ico">${l.icon}</div>
    <div><div class="font-bold ${l.primary ? 'text-lg gold-text' : 'text-[15px]'}">${l.title}</div>
    <div class="text-xs text-gray-400 mt-0.5" dir="auto">${l.sub}</div></div>
  </a>`).join("");

$("chips").innerHTML = ACTIONS.map(([k,t]) =>
  `<button class="chip ${k===current?'on':''}" data-k="${k}">${t}</button>`).join("");
$("chips").addEventListener("click", e => {
  const b = e.target.closest("button"); if(!b) return;
  current = b.dataset.k;
  document.querySelectorAll(".chip").forEach(c => c.classList.toggle("on", c===b));
});

const esc = s => s.replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
function md(t){
  return esc(t).split("\n").map(l => {
    l = l.replace(/\*\*(.+?)\*\*/g,"<b class='text-white'>$1</b>");
    if (/^#{1,3} /.test(l)) return "<h2>"+l.replace(/^#+ /,"")+"</h2>";
    if (/^\s*[-*] /.test(l)) return "<li>"+l.replace(/^\s*[-*] /,"")+"</li>";
    if (/^&gt; /.test(l)) return "<p class='text-gray-400 text-xs'>"+l.slice(5)+"</p>";
    return l.trim() ? "<p>"+l+"</p>" : "";
  }).join("");
}

$("go").onclick = async () => {
  const btn = $("go");
  btn.disabled = true; btn.textContent = "جاري التفكير...";
  $("out").classList.remove("hidden");
  $("agent").textContent = "";
  $("res").innerHTML = "<div class='dots py-4 text-center'><span></span><span></span><span></span></div>";
  try {
    const r = await fetch("/api/ai", {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({action: current, details: $("details").value})});
    const d = await r.json();
    lastText = d.text || d.error || "";
    $("agent").textContent = "🤖 " + (d.agent || "");
    $("res").innerHTML = md(lastText);
  } catch (e) {
    $("res").textContent = "تعذّر الاتصال، حاول مرة أخرى.";
  }
  btn.disabled = false; btn.textContent = "توليد الآن";
};

$("copy").onclick = async () => {
  try { await navigator.clipboard.writeText(lastText); $("copy").textContent = "تم النسخ ✓"; }
  catch(e) { $("copy").textContent = "تعذّر النسخ"; }
  setTimeout(() => $("copy").textContent = "نسخ", 1800);
};
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return PAGE.replace("__LINKS__", json.dumps(LINKS, ensure_ascii=False))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
