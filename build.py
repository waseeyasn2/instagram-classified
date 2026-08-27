import os, base64
from pathlib import Path

FOLDER = Path(__file__).parent
CATEGORIES = {
    "outdoor": "戶外自然",
    "city": "城市街道",
    "studio": "室內攝影棚",
    "wedding": "婚禮會場",
    "church": "教堂 儀式"
}

def get_photos(cat_folder):
    if not cat_folder.is_dir():
        return []
    return sorted([f for f in cat_folder.iterdir()
                   if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.gif')])

def img_to_base64(path):
    ext = path.suffix.lower()
    mime = {"jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png","webp":"image/webp","gif":"image/gif"}
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime.get(ext[1:],'image/jpeg')};base64,{data}"

# Build category sections HTML
sections_html = ""
for cat_folder, cat_label in CATEGORIES.items():
    files = get_photos(FOLDER / cat_folder)
    print(f"{cat_label}: {len(files)} photos")
    imgs = ""
    for f in files:
        b64 = img_to_base64(f)
        imgs += f'<img src="{b64}" alt="{f.name}" loading="lazy">\n'
    sections_html += f'<div class="cat-section" data-cat="{cat_folder}">\n{imgs}</div>\n'

html = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Instagram 照片集</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#000;color:#fff;-webkit-tap-highlight-color:transparent;overflow-x:hidden}
.header{position:sticky;top:0;z-index:100;background:#111;border-bottom:1px solid #333;padding:12px 0 0 0}
.header h1{text-align:center;font-size:18px;font-weight:600;padding-bottom:10px;letter-spacing:1px}
.tabs{display:flex;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;padding:0 8px 10px 8px;gap:6px}
.tabs::-webkit-scrollbar{display:none}
.tab{flex-shrink:0;padding:6px 14px;border-radius:20px;background:#222;color:#aaa;font-size:13px;font-weight:500;border:1px solid #333;cursor:pointer;transition:all .2s;white-space:nowrap}
.tab.active{background:#fff;color:#000;border-color:#fff}
.tab .count{font-size:11px;opacity:.6;margin-left:4px}
.cat-section{display:none}
.cat-section.active{display:block}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;padding:2px}
.grid .cat-section.active{display:block}
.cat-section img{width:100%;aspect-ratio:1;object-fit:cover;display:block;cursor:pointer;transition:opacity .15s;background:#1a1a1a}
.cat-section img:active{opacity:.7}
.lightbox{display:none;position:fixed;inset:0;z-index:200;background:#000;flex-direction:column}
.lightbox.open{display:flex}
.lightbox-header{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:#111;flex-shrink:0}
.lightbox-header .cat-label{font-size:14px;font-weight:500}
.lightbox-header .photo-count{font-size:13px;color:#888}
.lightbox-close{background:none;border:none;color:#fff;font-size:28px;cursor:pointer;padding:0 4px;line-height:1}
.lightbox-body{flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative;touch-action:pan-y}
.lightbox-body img{max-width:100%;max-height:100%;object-fit:contain;user-select:none;-webkit-user-select:none}
.nav-btn{position:absolute;top:50%;transform:translateY(-50%);background:rgba(0,0,0,.45);color:#fff;border:none;font-size:30px;width:44px;height:44px;border-radius:50%;cursor:pointer;z-index:10;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}
.nav-btn:active{background:rgba(0,0,0,.7)}
.nav-prev{left:10px}.nav-next{right:10px}
.lightbox-footer{display:flex;align-items:center;justify-content:center;gap:10px;padding:10px 16px;background:#111;flex-shrink:0}
.dots{display:flex;gap:6px;align-items:center}
.dot{width:6px;height:6px;border-radius:50%;background:#444;transition:all .2s}
.dot.active{background:#fff;width:8px;height:8px}
.dot.near{background:#888}
@media(min-width:600px){.grid{grid-template-columns:repeat(4,1fr)}}
</style>
</head>
<body>
<div class="header">
  <h1>Instagram Photo Gallery</h1>
  <div class="tabs" id="tabs"></div>
</div>
<div class="grid" id="grid">
''' + sections_html + '''
</div>
<div class="lightbox" id="lightbox">
  <div class="lightbox-header">
    <span class="cat-label" id="catLabel"></span>
    <span class="photo-count" id="photoCount"></span>
    <button class="lightbox-close" id="closeBtn">&times;</button>
  </div>
  <div class="lightbox-body" id="lightboxBody">
    <button class="nav-btn nav-prev" id="prevBtn">&#8249;</button>
    <img id="lbImg" src="" alt="">
    <button class="nav-btn nav-next" id="nextBtn">&#8250;</button>
  </div>
  <div class="lightbox-footer"><div class="dots" id="dots"></div></div>
</div>
<script>
const labels=''' + str({v:k for k,v in CATEGORIES.items()}).replace("'",'"') + ''';
const catNames=[''' + ','.join(f'"{v}"' for v in CATEGORIES.values()) + '''];
const catKeys=[''' + ','.join(f'"{k}"' for k in CATEGORIES.keys()) + '''];
let currentIdx=0, currentImgIdx=0;
const sections=document.querySelectorAll('.cat-section');
const lightbox=document.getElementById('lightbox');
const lbImg=document.getElementById('lbImg');
const catLabel=document.getElementById('catLabel');
const photoCount=document.getElementById('photoCount');
const dotsEl=document.getElementById('dots');

function switchCat(idx){
  currentIdx=idx;
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('active',i===idx));
  sections.forEach((s,i)=>s.classList.toggle('active',i===idx));
}

function buildTabs(){
  const tabsEl=document.getElementById('tabs');
  tabsEl.innerHTML='';
  catNames.forEach((name,i)=>{
    const btn=document.createElement('button');
    btn.className='tab'+(i===currentIdx?' active':'');
    const count=sections[i].querySelectorAll('img').length;
    btn.innerHTML=name+'<span class="count">'+count+'</span>';
    btn.onclick=()=>switchCat(i);
    tabsEl.appendChild(btn);
  });
}

function openLightbox(imgEl){
  const sec=sections[currentIdx];
  const imgs=Array.from(sec.querySelectorAll('img'));
  currentImgIdx=imgs.indexOf(imgEl);
  updateLightbox();
  lightbox.classList.add('open');
  document.body.style.overflow='hidden';
}

function closeLightbox(){
  lightbox.classList.remove('open');
  document.body.style.overflow='';
}

function updateLightbox(){
  const sec=sections[currentIdx];
  const imgs=sec.querySelectorAll('img');
  lbImg.src=imgs[currentImgIdx].src;
  catLabel.textContent=catNames[currentIdx];
  photoCount.textContent=(currentImgIdx+1)+' / '+imgs.length;
  buildDots(imgs.length);
}

function buildDots(total){
  dotsEl.innerHTML='';
  if(total<=30){
    for(let i=0;i<total;i++){
      const d=document.createElement('div');
      d.className='dot'+(i===currentImgIdx?' active':(Math.abs(i-currentImgIdx)===1?' near':''));
      dotsEl.appendChild(d);
    }
  }else{
    for(let i=0;i<total;i++){
      if(i===0||i===total-1||(i>=currentImgIdx-3&&i<=currentImgIdx+3)){
        const d=document.createElement('div');
        d.className='dot'+(i===currentImgIdx?' active':(Math.abs(i-currentImgIdx)<=1?' near':''));
        dotsEl.appendChild(d);
      }else if(!dotsEl.lastChild||dotsEl.lastChild.className!=='skip'){
        const s=document.createElement('span');
        s.className='skip';s.textContent='...';s.style.cssText='color:#555;font-size:10px';
        dotsEl.appendChild(s);
      }
    }
  }
}

function prevPhoto(){
  const total=sections[currentIdx].querySelectorAll('img').length;
  currentImgIdx=(currentImgIdx-1+total)%total;
  updateLightbox();
}
function nextPhoto(){
  const total=sections[currentIdx].querySelectorAll('img').length;
  currentImgIdx=(currentImgIdx+1)%total;
  updateLightbox();
}

document.getElementById('closeBtn').onclick=closeLightbox;
document.getElementById('prevBtn').onclick=e=>{e.stopPropagation();prevPhoto()};
document.getElementById('nextBtn').onclick=e=>{e.stopPropagation();nextPhoto()};
lightbox.addEventListener('click',e=>{if(e.target===document.getElementById('lightboxBody'))closeLightbox()});
document.addEventListener('keydown',e=>{
  if(!lightbox.classList.contains('open'))return;
  if(e.key==='Escape')closeLightbox();
  if(e.key==='ArrowLeft')prevPhoto();
  if(e.key==='ArrowRight')nextPhoto();
});
let touchStartX=0,touchStartY=0;
document.getElementById('lightboxBody').addEventListener('touchstart',e=>{touchStartX=e.touches[0].clientX;touchStartY=e.touches[0].clientY},{passive:true});
document.getElementById('lightboxBody').addEventListener('touchend',e=>{
  const dx=e.changedTouches[0].clientX-touchStartX,dy=e.changedTouches[0].clientY-touchStartY;
  if(Math.abs(dx)>Math.abs(dy)&&Math.abs(dx)>50){dx<0?nextPhoto():prevPhoto()}
},{passive:true});

document.querySelectorAll('.cat-section img').forEach(img=>{
  img.addEventListener('click',()=>openLightbox(img));
});

buildTabs();
switchCat(0);
</script>
</body>
</html>'''

out = FOLDER / "gallery.html"
out.write_text(html, encoding="utf-8")
size_mb = out.stat().st_size / 1024 / 1024
print(f"\nDone: {out} ({size_mb:.1f} MB)")
