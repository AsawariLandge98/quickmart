const VoiceCart = {
  recognition: null,
  isListening: false,
  csrfToken: null,

  init() {
    this.csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
      || document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    this.injectUI();
    this.setupRecognition();
    this.bindEvents();
  },

  injectUI() {
    if (document.getElementById('voice-cart-btn')) return;
    const btn = document.createElement('div');
    btn.id = 'voice-cart-btn';
    btn.innerHTML = '<div class="vc-pulse"></div><svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="9" y="2" width="6" height="11" rx="3" fill="white"/><path d="M5 10a7 7 0 0 0 14 0" stroke="white" stroke-width="2" stroke-linecap="round" fill="none"/><line x1="12" y1="17" x2="12" y2="21" stroke="white" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="21" x2="16" y2="21" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>';
    btn.title = 'Voice se cart mein add karo';
    document.body.appendChild(btn);

    const modal = document.createElement('div');
    modal.id = 'voice-cart-modal';
    modal.innerHTML = `
      <div class="vc-backdrop" id="vc-backdrop"></div>
      <div class="vc-panel">
        <div class="vc-header">
          <div class="vc-header-left">
            <div class="vc-logo"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="9" y="2" width="6" height="11" rx="3" fill="currentColor"/><path d="M5 10a7 7 0 0 0 14 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></div>
            <div><div class="vc-title">Voice Cart</div><div class="vc-subtitle">Hindi ya English mein boliye</div></div>
          </div>
          <button class="vc-close" id="vc-close">&#10005;</button>
        </div>
        <div class="vc-mic-area" id="vc-mic-area">
          <div class="vc-mic-ring" id="vc-mic-ring">
            <div class="vc-mic-inner" id="vc-mic-inner">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><rect x="9" y="2" width="6" height="11" rx="3" fill="currentColor"/><path d="M5 10a7 7 0 0 0 14 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="8" y1="21" x2="16" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            </div>
          </div>
          <div class="vc-status" id="vc-status">Mic button dabao aur boliye</div>
          <div class="vc-transcript" id="vc-transcript"></div>
        </div>
        <div class="vc-examples">
          <div class="vc-examples-title">Examples:</div>
          <div class="vc-chips">
            <span class="vc-chip" onclick="VoiceCart.tryExample(this.textContent)">Ek kilo aalu add karo</span>
            <span class="vc-chip" onclick="VoiceCart.tryExample(this.textContent)">Do doodh aur bread</span>
            <span class="vc-chip" onclick="VoiceCart.tryExample(this.textContent)">Teen anda chahiye</span>
            <span class="vc-chip" onclick="VoiceCart.tryExample(this.textContent)">2 kg rice</span>
          </div>
        </div>
        <div class="vc-results" id="vc-results"></div>
        <div class="vc-footer">
          <button class="vc-mic-btn" id="vc-mic-btn" onclick="VoiceCart.toggleMic()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="9" y="2" width="6" height="11" rx="3" fill="currentColor"/><path d="M5 10a7 7 0 0 0 14 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            Boliye
          </button>
        </div>
      </div>`;
    document.body.appendChild(modal);
    this.injectStyles();
  },

  injectStyles() {
    if (document.getElementById('vc-styles')) return;
    const style = document.createElement('style');
    style.id = 'vc-styles';
    style.textContent = `
      #voice-cart-btn{position:fixed;bottom:28px;right:28px;width:58px;height:58px;background:#ff5200;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:9998;box-shadow:0 4px 20px rgba(255,82,0,.4);transition:transform .2s,box-shadow .2s}
      #voice-cart-btn:hover{transform:scale(1.08);box-shadow:0 6px 28px rgba(255,82,0,.5)}
      #voice-cart-btn.listening{background:#e64700;animation:vc-bounce .6s ease-in-out infinite alternate}
      .vc-pulse{position:absolute;width:58px;height:58px;border-radius:50%;background:rgba(255,82,0,.3);animation:vc-pulse 2s ease-out infinite}
      @keyframes vc-pulse{0%{transform:scale(1);opacity:.6}100%{transform:scale(1.8);opacity:0}}
      @keyframes vc-bounce{from{transform:scale(1)}to{transform:scale(1.12)}}
      #voice-cart-modal{position:fixed;inset:0;z-index:9999;display:none;align-items:flex-end;justify-content:center}
      #voice-cart-modal.open{display:flex}
      .vc-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.5);backdrop-filter:blur(4px)}
      .vc-panel{position:relative;background:#fff;border-radius:24px 24px 0 0;width:100%;max-width:540px;max-height:90vh;overflow-y:auto;animation:vc-slide-up .3s cubic-bezier(.34,1.56,.64,1);z-index:1}
      @keyframes vc-slide-up{from{transform:translateY(100%)}to{transform:translateY(0)}}
      .vc-header{display:flex;align-items:center;justify-content:space-between;padding:20px 22px 16px;border-bottom:1px solid #f0f0f0}
      .vc-header-left{display:flex;align-items:center;gap:12px}
      .vc-logo{width:40px;height:40px;background:#ff5200;border-radius:12px;display:flex;align-items:center;justify-content:center;color:white}
      .vc-title{font-family:'Syne',sans-serif;font-size:18px;font-weight:700;color:#0d0d0d}
      .vc-subtitle{font-size:12px;color:#888;margin-top:1px}
      .vc-close{width:32px;height:32px;border-radius:50%;background:#f5f5f5;border:none;cursor:pointer;font-size:14px;color:#666;display:flex;align-items:center;justify-content:center;transition:background .15s}
      .vc-close:hover{background:#ebebeb}
      .vc-mic-area{padding:28px 22px 16px;text-align:center}
      .vc-mic-ring{width:100px;height:100px;border-radius:50%;background:#fff3ee;border:2px solid #ffd0be;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;transition:all .3s}
      .vc-mic-ring.listening{background:#ff5200;border-color:#ff5200;animation:vc-ring-pulse .8s ease-in-out infinite alternate;box-shadow:0 0 0 8px rgba(255,82,0,.15)}
      @keyframes vc-ring-pulse{from{box-shadow:0 0 0 6px rgba(255,82,0,.15)}to{box-shadow:0 0 0 18px rgba(255,82,0,.05)}}
      .vc-mic-inner{width:68px;height:68px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;color:#ff5200;transition:all .3s}
      .vc-mic-ring.listening .vc-mic-inner{background:rgba(255,255,255,.2);color:#fff}
      .vc-status{font-size:15px;color:#555;font-weight:500;margin-bottom:8px}
      .vc-transcript{font-size:14px;color:#ff5200;font-weight:600;min-height:22px;font-style:italic}
      .vc-examples{padding:0 22px 16px}
      .vc-examples-title{font-size:12px;color:#aaa;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}
      .vc-chips{display:flex;flex-wrap:wrap;gap:8px}
      .vc-chip{padding:6px 12px;background:#f5f5f5;border-radius:20px;font-size:12px;color:#444;cursor:pointer;transition:all .15s;border:1px solid #ebebeb}
      .vc-chip:hover{background:#fff3ee;border-color:#ffd0be;color:#ff5200}
      .vc-results{padding:0 22px}
      .vc-result-item{background:#fafafa;border-radius:14px;padding:14px;margin-bottom:12px;border:1px solid #f0f0f0}
      .vc-result-query{font-size:12px;color:#aaa;margin-bottom:10px}
      .vc-result-query span{color:#ff5200;font-weight:600}
      .vc-product-row{display:flex;align-items:center;gap:12px;padding:10px;background:#fff;border-radius:10px;margin-bottom:8px;border:1.5px solid transparent;cursor:pointer;transition:all .2s}
      .vc-product-row:hover{border-color:#ff5200;background:#fff8f5}
      .vc-product-row.adding{border-color:#10b981;background:#ecfdf5}
      .vc-product-img{width:48px;height:48px;background:#f5f5f5;border-radius:8px;object-fit:contain;padding:4px;flex-shrink:0}
      .vc-product-info{flex:1;min-width:0}
      .vc-product-name{font-size:13px;font-weight:500;color:#0d0d0d;margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
      .vc-product-meta{font-size:12px;color:#888}
      .vc-product-price{font-size:14px;font-weight:700;color:#0d0d0d}
      .vc-add-btn{width:32px;height:32px;background:#ff5200;color:#fff;border-radius:8px;border:none;font-size:20px;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .2s;flex-shrink:0;line-height:1}
      .vc-add-btn:hover{background:#e64700;transform:scale(1.1)}
      .vc-add-btn.added{background:#10b981;pointer-events:none}
      .vc-not-found{text-align:center;padding:12px;color:#aaa;font-size:13px}
      .vc-qty-badge{display:inline-block;background:#fff3ee;color:#ff5200;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:6px}
      .vc-footer{padding:14px 22px 24px;position:sticky;bottom:0;background:#fff;border-top:1px solid #f0f0f0}
      .vc-mic-btn{width:100%;padding:14px;background:#ff5200;color:#fff;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:all .2s;box-shadow:0 4px 16px rgba(255,82,0,.3)}
      .vc-mic-btn:hover{background:#e64700}
      .vc-mic-btn.listening{background:#e64700;animation:vc-btn-pulse .6s ease-in-out infinite alternate}
      @keyframes vc-btn-pulse{from{box-shadow:0 4px 16px rgba(255,82,0,.3)}to{box-shadow:0 4px 28px rgba(255,82,0,.6)}}
      .vc-loading{text-align:center;padding:20px;color:#ff5200;font-size:14px;font-weight:500}
      .vc-error{background:#fdecea;color:#e53935;border-radius:10px;padding:12px 16px;font-size:13px;margin-bottom:12px}
      .vc-success-toast{position:fixed;bottom:100px;left:50%;transform:translateX(-50%) translateY(20px);background:#0d0d0d;color:#fff;padding:10px 20px;border-radius:50px;font-size:14px;font-weight:500;opacity:0;transition:all .3s;z-index:10000;white-space:nowrap}
      .vc-success-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
      @media(max-width:480px){.vc-panel{border-radius:20px 20px 0 0}#voice-cart-btn{bottom:20px;right:16px;width:52px;height:52px}.vc-pulse{width:52px;height:52px}}
    `;
    document.head.appendChild(style);
  },

  setupRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    this.recognition = new SR();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'hi-IN';
    this.recognition.onstart = () => { this.isListening = true; this.setListeningUI(true); };
    this.recognition.onresult = (e) => {
      let interim = '', final = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) final += e.results[i][0].transcript;
        else interim += e.results[i][0].transcript;
      }
      const t = document.getElementById('vc-transcript');
      if (t) t.textContent = '"' + (final || interim) + '"';
      if (final) this.processVoice(final);
    };
    this.recognition.onerror = (e) => {
      this.isListening = false; this.setListeningUI(false);
      const s = document.getElementById('vc-status');
      if (s) s.textContent = e.error === 'not-allowed' ? 'Mic permission denied.' : 'Error. Dobara try karein.';
    };
    this.recognition.onend = () => { this.isListening = false; this.setListeningUI(false); };
  },

  bindEvents() {
    document.getElementById('voice-cart-btn')?.addEventListener('click', () => this.open());
    document.getElementById('vc-close')?.addEventListener('click', () => this.close());
    document.getElementById('vc-backdrop')?.addEventListener('click', () => this.close());
  },

  open() {
    document.getElementById('voice-cart-modal').classList.add('open');
    document.getElementById('vc-results').innerHTML = '';
    document.getElementById('vc-transcript').textContent = '';
    document.getElementById('vc-status').textContent = 'Mic button dabao aur boliye';
  },

  close() {
    document.getElementById('voice-cart-modal').classList.remove('open');
    if (this.isListening) this.recognition?.stop();
  },

  toggleMic() {
    if (!this.recognition) { alert('Chrome browser use karein voice ke liye.'); return; }
    if (this.isListening) { this.recognition.stop(); return; }
    document.getElementById('vc-results').innerHTML = '';
    document.getElementById('vc-transcript').textContent = '';
    try { this.recognition.start(); } catch(e) { this.setupRecognition(); setTimeout(() => this.recognition?.start(), 300); }
  },

  setListeningUI(on) {
    document.getElementById('vc-mic-ring')?.classList.toggle('listening', on);
    document.getElementById('vc-mic-btn')?.classList.toggle('listening', on);
    document.getElementById('voice-cart-btn')?.classList.toggle('listening', on);
    const btn = document.getElementById('vc-mic-btn');
    const status = document.getElementById('vc-status');
    if (on) {
      if (btn) btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/></svg> Sun raha hoon...';
      if (status) status.textContent = 'Sun raha hoon... boliye';
    } else {
      if (btn) btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none"><rect x="9" y="2" width="6" height="11" rx="3" fill="currentColor"/><path d="M5 10a7 7 0 0 0 14 0" stroke="currentColor" stroke-width="2" stroke-linecap="round" fill="none"/><line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg> Boliye';
      if (status) status.textContent = 'Mic button dabao aur boliye';
    }
  },

  tryExample(text) {
    text = text.replace(/["""]/g, '').trim();
    document.getElementById('vc-transcript').textContent = '"' + text + '"';
    document.getElementById('vc-status').textContent = 'Processing...';
    this.processVoice(text);
  },

  async processVoice(text) { this.open();
    const el = document.getElementById('vc-results');
    el.innerHTML = '<div class="vc-loading">Products dhoondh raha hoon...</div>';
    try {
      const res = await fetch('/cart/voice-search/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      if (!data.success) { el.innerHTML = '<div class="vc-error">' + (data.error || 'Kuch gadbad ho gayi') + '</div>'; return; }
      this.renderResults(data.items);
    } catch(e) { el.innerHTML = '<div class="vc-error">Network error. Please try again.</div>'; }
  },

  renderResults(items) {
    const el = document.getElementById('vc-results');
    if (!items?.length) { el.innerHTML = '<div class="vc-not-found">Koi product nahi mila</div>'; return; }
    let html = '';
    for (const item of items) {
      html += '<div class="vc-result-item"><div class="vc-result-query">Aapne kaha: <span>"' + item.query + '"</span><span class="vc-qty-badge">x' + item.quantity + '</span></div>';
      if (!item.found || !item.products.length) {
        html += '<div class="vc-not-found">"' + item.product_name + '" nahi mila</div>';
      } else {
        for (const p of item.products) {
          const img = p.image ? '<img class="vc-product-img" src="' + p.image + '" alt="' + p.name + '">' : '<div class="vc-product-img" style="display:flex;align-items:center;justify-content:center;font-size:24px;">&#128722;</div>';
          html += '<div class="vc-product-row">' + img + '<div class="vc-product-info"><div class="vc-product-name">' + p.name + '</div><div class="vc-product-meta">' + p.variant_name + ' &bull; ' + p.category + '</div></div><div class="vc-product-price">&#8377;' + p.price + '</div><button class="vc-add-btn" onclick="VoiceCart.addToCart(' + p.variant_id + ',' + item.quantity + ',\'' + p.name.replace(/'/g, '') + '\',this)">+</button></div>';
        }
      }
      html += '</div>';
    }
    el.innerHTML = html;
  },

  async addToCart(variantId, qty, name, btn) {
    btn.textContent = '...'; btn.disabled = true;
    try {
      const res = await fetch('/cart/voice-add/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this.csrfToken },
        body: JSON.stringify({ variant_id: variantId, quantity: qty }),
      });
      const data = await res.json();
      if (data.success) {
        btn.textContent = '✓'; btn.classList.add('added');
        btn.closest('.vc-product-row')?.classList.add('adding');
        const badge = document.getElementById('cartCountBadge');
        if (badge) badge.textContent = data.count;
        this.showToast(name + ' cart mein add ho gaya!');
      } else { btn.textContent = '+'; btn.disabled = false; }
    } catch(e) { btn.textContent = '+'; btn.disabled = false; }
  },

  showToast(msg) {
    let t = document.getElementById('vc-toast');
    if (!t) { t = document.createElement('div'); t.id = 'vc-toast'; t.className = 'vc-success-toast'; document.body.appendChild(t); }
    t.textContent = msg; t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
  },
};

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', () => VoiceCart.init());
else VoiceCart.init();

