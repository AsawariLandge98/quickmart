/* QuickMart — main.js */

// ── CART AJAX ──
function addToCart(variantId, btn) {
  const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
  fetch('/cart/add/', {
    method: 'POST',
    headers: {'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest'},
    body: `variant_id=${variantId}&quantity=1&csrfmiddlewaretoken=${csrf}`
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      updateCartBadge(data.count);
      showToast(data.message, 'success');
      if (btn) {
        const wrap = btn.closest('.product-footer');
        if (wrap) {
          btn.style.display = 'none';
          const qc = document.createElement('div');
          qc.className = 'qty-ctrl';
          qc.innerHTML = `<button class="qty-btn" onclick="updateQty(this, ${variantId}, -1)">−</button><span class="qty-num">1</span><button class="qty-btn" onclick="updateQty(this, ${variantId}, 1)">+</button>`;
          wrap.appendChild(qc);
        }
      }
    }
  })
  .catch(() => showToast('Error adding to cart', 'error'));
}

function updateQty(el, variantId, delta) {
  const wrap = el.closest('.qty-ctrl');
  const numEl = wrap?.querySelector('.qty-num');
  if (!numEl) return;
  const current = parseInt(numEl.textContent);
  const newQty = current + delta;
  const csrf = getCookie('csrftoken');
  const action = delta > 0 ? 'increase' : 'decrease';
  // Find item id from data attribute if available
  const itemId = wrap.dataset.itemId;
  if (!itemId) {
    if (newQty <= 0) { wrap.remove(); return; }
    numEl.textContent = newQty;
    return;
  }
  fetch(`/cart/update/${itemId}/`, {
    method: 'POST',
    headers: {'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest'},
    body: `action=${action}&csrfmiddlewaretoken=${csrf}`
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      updateCartBadge(data.count);
      if (newQty <= 0) wrap.remove();
      else numEl.textContent = newQty;
      updateCartTotals(data);
    }
  });
}

function updateCartTotals(data) {
  const sub = document.getElementById('cartSubtotal');
  const del = document.getElementById('cartDelivery');
  const dis = document.getElementById('cartDiscount');
  const tot = document.getElementById('cartTotal');
  if (sub) sub.textContent = '₹' + data.subtotal.toFixed(0);
  if (del) del.textContent = data.delivery == 0 ? 'FREE' : '₹' + data.delivery.toFixed(0);
  if (dis) dis.textContent = '₹' + data.discount.toFixed(0);
  if (tot) tot.textContent = '₹' + data.total.toFixed(0);
}

function updateCartBadge(count) {
  const badges = document.querySelectorAll('.cart-count, #cartCountBadge');
  badges.forEach(b => { b.textContent = count; });
}

// ── WISHLIST ──
function toggleWishlist(productId, btn) {
  const csrf = getCookie('csrftoken');
  fetch(`/users/wishlist/toggle/${productId}/`, {
    method: 'POST',
    headers: {'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest'},
    body: `csrfmiddlewaretoken=${csrf}`
  })
  .then(r => r.json())
  .then(data => {
    showToast(data.message, data.status === 'added' ? 'success' : 'info');
    if (btn) {
      if (data.status === 'added') { btn.textContent = '❤️'; btn.classList.add('active'); }
      else { btn.textContent = '🤍'; btn.classList.remove('active'); }
    }
  });
}

// ── SEARCH AUTOCOMPLETE ──
let searchTimer;
const searchInput = document.getElementById('navSearchInput');
const acBox = document.getElementById('autocompleteBox');

if (searchInput) {
  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimer);
    const q = this.value.trim();
    if (q.length < 2) { acBox.classList.remove('open'); return; }
    searchTimer = setTimeout(() => {
      fetch(`/api/autocomplete/?q=${encodeURIComponent(q)}`)
        .then(r => r.json())
        .then(data => {
          if (!data.results.length && !data.categories.length) { acBox.classList.remove('open'); return; }
          let html = '';
          data.categories?.forEach(c => {
            html += `<a class="ac-item" href="/category/${c.slug}/"><div class="ac-icon">📂</div><div><strong>${c.name}</strong><br><small style="color:var(--mid)">Category</small></div></a>`;
          });
          data.results?.forEach(p => {
            html += `<a class="ac-item" href="/products/${p.slug}/"><div class="ac-icon">🔍</div><div>${p.name}</div></a>`;
          });
          acBox.innerHTML = html;
          acBox.classList.add('open');
        });
    }, 250);
  });
  document.addEventListener('click', e => {
    if (!searchInput.contains(e.target)) acBox.classList.remove('open');
  });
}

// ── MOBILE MENU ──
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => mobileMenu.classList.toggle('open'));
}

// ── COUNTDOWN ──
function startCountdown(h, m, s) {
  const cdH = document.getElementById('cdH');
  const cdM = document.getElementById('cdM');
  const cdS = document.getElementById('cdS');
  if (!cdH) return;
  let total = h*3600 + m*60 + s;
  setInterval(() => {
    if (total <= 0) return;
    total--;
    const hh = Math.floor(total/3600);
    const mm = Math.floor((total%3600)/60);
    const ss = total%60;
    cdH.textContent = String(hh).padStart(2,'0');
    cdM.textContent = String(mm).padStart(2,'0');
    cdS.textContent = String(ss).padStart(2,'0');
  }, 1000);
}
startCountdown(2, 47, 13);

// ── COUPON (CART) ──
function applyCoupon() {
  const input = document.getElementById('couponInput');
  const code = input?.value?.trim();
  if (!code) return;
  const csrf = getCookie('csrftoken');
  fetch('/cart/coupon/apply/', {
    method: 'POST',
    headers: {'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest'},
    body: `code=${code}&csrfmiddlewaretoken=${csrf}`
  })
  .then(r => r.json())
  .then(data => {
    showToast(data.message, data.success ? 'success' : 'error');
    if (data.success) updateCartTotals(data);
  });
}

// ── TOAST ──
function showToast(msg, type='info') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:8px;max-width:360px;';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  const colors = {success:'#00a651',error:'#e53935',info:'#1565c0',warning:'#f5a623'};
  toast.style.cssText = `background:${colors[type]||colors.info};color:#fff;padding:12px 18px;border-radius:10px;font-size:14px;box-shadow:0 8px 32px rgba(0,0,0,.15);animation:slideIn .3s ease;display:flex;align-items:center;gap:10px;font-family:'DM Sans',sans-serif;`;
  toast.innerHTML = msg;
  container.appendChild(toast);
  setTimeout(() => { toast.style.animation='slideIn .3s ease reverse'; setTimeout(()=>toast.remove(),300); }, 3000);
}

// ── STAR RATING ──
const starRating = document.querySelector('.star-rating');
if (starRating) {
  const stars = starRating.querySelectorAll('span');
  const ratingInput = document.getElementById('ratingInput');
  stars.forEach((star, i) => {
    star.addEventListener('mouseover', () => stars.forEach((s,j) => s.style.color = j<=i ? 'var(--yellow)' : 'var(--border)'));
    star.addEventListener('click', () => {
      stars.forEach((s,j) => { s.classList.toggle('active', j<=i); s.style.color = j<=i ? 'var(--yellow)' : 'var(--border)'; });
      if (ratingInput) ratingInput.value = i+1;
    });
  });
  starRating.addEventListener('mouseleave', () => {
    const val = parseInt(ratingInput?.value||0);
    stars.forEach((s,j) => s.style.color = j<val ? 'var(--yellow)' : 'var(--border)');
  });
}

// ── PRODUCT IMAGE GALLERY ──
function changeMainImage(src, thumb) {
  const main = document.getElementById('mainProductImg');
  if (main) main.src = src;
  document.querySelectorAll('.detail-thumb').forEach(t => t.classList.remove('active'));
  if (thumb) thumb.classList.add('active');
}

// ── VARIANT SELECT ──
function selectVariant(el, variantId, price, mrp) {
  document.querySelectorAll('.variant-opt').forEach(v => v.classList.remove('active'));
  el.classList.add('active');
  const priceEl = document.getElementById('variantPrice');
  const mrpEl = document.getElementById('variantMrp');
  const addBtn = document.getElementById('addToCartBtn');
  if (priceEl) priceEl.textContent = '₹' + price;
  if (mrpEl) mrpEl.textContent = mrp > price ? '₹' + mrp : '';
  if (addBtn) addBtn.dataset.variantId = variantId;
}

// ── ADDRESS SELECT (CHECKOUT) ──
function selectAddress(id) {
  document.querySelectorAll('.address-opt').forEach(a => a.classList.remove('selected'));
  document.querySelector(`[data-addr="${id}"]`)?.classList.add('selected');
  const inp = document.getElementById('selectedAddress');
  if (inp) inp.value = id;
}

function selectPayment(method) {
  document.querySelectorAll('.pay-opt').forEach(p => p.classList.remove('selected'));
  document.querySelector(`[data-method="${method}"]`)?.classList.add('selected');
  const inp = document.getElementById('selectedPayment');
  if (inp) inp.value = method;
}

// ── ADMIN STOCK UPDATE ──
function updateStock(variantId, currentStock) {
  const newStock = prompt(`Update stock for variant ${variantId}:`, currentStock);
  if (newStock === null || isNaN(newStock)) return;
  const csrf = getCookie('csrftoken');
  fetch(`/admin-panel/inventory/${variantId}/stock/`, {
    method: 'POST',
    headers: {'Content-Type':'application/x-www-form-urlencoded'},
    body: `stock=${newStock}&csrfmiddlewaretoken=${csrf}`
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      showToast(`Stock updated to ${data.stock}`, 'success');
      const el = document.getElementById(`stock-${variantId}`);
      if (el) { el.textContent = data.stock; el.className = data.stock <= 10 ? 'stock-low' : 'stock-ok'; }
    }
  });
}

function toggleUserActive(userId, btn) {
  const csrf = getCookie('csrftoken');
  fetch(`/admin-panel/users/${userId}/toggle/`, {
    method: 'POST',
    headers: {'Content-Type':'application/x-www-form-urlencoded'},
    body: `csrfmiddlewaretoken=${csrf}`
  })
  .then(r => r.json())
  .then(data => {
    const badge = document.getElementById(`user-status-${userId}`);
    if (badge) { badge.className = data.active ? 'badge-active' : 'badge-inactive'; badge.textContent = data.active ? 'Active' : 'Inactive'; }
    showToast(data.active ? 'User activated' : 'User deactivated', 'info');
  });
}

// ── SPIN WHEEL ──
let spinCanvas, spinCtx, currentAngle = 0, isSpinning = false;
const prizes = [
  {label:'10% OFF',color:'#ff4d00'},{label:'₹50 Cash',color:'#1a1a1a'},
  {label:'Free Del',color:'#00a651'},{label:'Try Again',color:'#888'},
  {label:'20% OFF',color:'#7b2d8b'},{label:'100 Coins',color:'#f5a623'},
  {label:'₹30 Back',color:'#1565c0'},{label:'Try Again',color:'#888'},
];

function drawWheel(angle) {
  spinCanvas = spinCanvas || document.getElementById('spinCanvas');
  if (!spinCanvas) return;
  spinCtx = spinCtx || spinCanvas.getContext('2d');
  const cx = 150, cy = 150, r = 140;
  const arc = (Math.PI * 2) / prizes.length;
  spinCtx.clearRect(0, 0, 300, 300);
  prizes.forEach((p, i) => {
    const start = i * arc + angle;
    const end = start + arc;
    spinCtx.beginPath(); spinCtx.moveTo(cx, cy);
    spinCtx.arc(cx, cy, r, start, end);
    spinCtx.closePath();
    spinCtx.fillStyle = p.color; spinCtx.fill();
    spinCtx.strokeStyle = '#fff'; spinCtx.lineWidth = 2; spinCtx.stroke();
    spinCtx.save(); spinCtx.translate(cx, cy);
    spinCtx.rotate(start + arc / 2);
    spinCtx.textAlign = 'right'; spinCtx.fillStyle = '#fff';
    spinCtx.font = 'bold 12px Syne,sans-serif';
    spinCtx.fillText(p.label, r - 10, 4);
    spinCtx.restore();
  });
  spinCtx.beginPath(); spinCtx.arc(cx, cy, 22, 0, Math.PI*2);
  spinCtx.fillStyle = '#fff'; spinCtx.fill();
  spinCtx.fillStyle = '#0d0d0d'; spinCtx.textAlign = 'center';
  spinCtx.font = 'bold 10px Syne,sans-serif'; spinCtx.fillText('SPIN', cx, cy + 3);
}

function doSpin() {
  if (isSpinning) return;
  const btn = document.getElementById('spinTrigger');
  const csrf = getCookie('csrftoken');
  fetch('/users/spin/', {method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':'XMLHttpRequest'},body:`csrfmiddlewaretoken=${csrf}`})
  .then(r => r.json())
  .then(data => {
    if (!data.success) { showToast(data.message, 'error'); return; }
    isSpinning = true;
    if (btn) btn.disabled = true;
    const extra = Math.floor(Math.random() * 360) + 1440;
    const targetAngle = currentAngle + extra * (Math.PI / 180);
    const startAngle = currentAngle;
    const duration = 4000;
    let startTime = null;
    function animate(ts) {
      if (!startTime) startTime = ts;
      const prog = Math.min((ts - startTime) / duration, 1);
      const ease = 1 - Math.pow(1 - prog, 4);
      const angle = startAngle + (targetAngle - startAngle) * ease;
      drawWheel(angle);
      if (prog < 1) { requestAnimationFrame(animate); }
      else {
        currentAngle = targetAngle;
        const resultEl = document.getElementById('spinResult');
        if (resultEl) resultEl.textContent = `🎉 You won: ${data.prize.label}!`;
        const coinsEl = document.getElementById('spinCoinsDisplay');
        if (coinsEl) coinsEl.textContent = data.coins + ' coins';
        showToast(`🎉 ${data.prize.label}!`, 'success');
        isSpinning = false;
        if (btn) btn.disabled = false;
      }
    }
    requestAnimationFrame(animate);
  });
}

if (document.getElementById('spinCanvas')) { drawWheel(0); }

// ── HELPERS ──
function getCookie(name) {
  const val = `; ${document.cookie}`;
  const parts = val.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

// Auto-dismiss alerts
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(a => {
    a.style.animation = 'slideIn .3s ease reverse';
    setTimeout(() => a.remove(), 300);
  });
}, 4000);

// ── TRACKING PAGE ANIMATION ──
const trackingDots = document.querySelectorAll('.ts-step.active .ts-dot');
trackingDots.forEach(dot => {
  setInterval(() => dot.style.boxShadow = dot.style.boxShadow ? '' : '0 0 0 6px rgba(255,77,0,.2)', 800);
});

// ── ADMIN CHART ANIMATION ──
document.querySelectorAll('.chart-bar').forEach(bar => {
  const h = bar.dataset.height;
  if (h) { bar.style.height = '0'; setTimeout(() => bar.style.height = h + 'px', 100); }
});

// ── CONFIRM DIALOGS ──
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

console.log('%c⚡ QuickMart Ready', 'color:#ff4d00;font-family:Syne;font-size:16px;font-weight:800');
