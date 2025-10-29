const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const analyzeBtn = document.getElementById('analyzeBtn');
const emptyState = document.getElementById('emptyState');
const previewState = document.getElementById('previewState');
const loadingState = document.getElementById('loadingState');
const resultState = document.getElementById('resultState');

if (imageInput) {
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                emptyState.classList.add('hidden');
                previewState.classList.remove('hidden');
                loadingState.classList.add('hidden');
                resultState.classList.add('hidden');
                analyzeBtn.classList.remove('hidden');
            };
            reader.readAsDataURL(file);
        }
    });
}

async function analyzeImage() {
    const file = imageInput.files[0];
    if (!file) return;
    
    emptyState.classList.add('hidden');
    previewState.classList.add('hidden');
    loadingState.classList.remove('hidden');
    resultState.classList.add('hidden');
    analyzeBtn.classList.add('hidden');
    
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        loadingState.classList.add('hidden');
        resultState.classList.remove('hidden');
        
        if (result.detected) {
            let predictionsHTML = '';
            result.predictions.forEach((pred, index) => {
                predictionsHTML += `
                    <div class="prediction-item">
                        <p style="font-weight:bold;margin-bottom:10px;">
                            <span style="color:#fca5a5;">O'simta #${index + 1}:</span> ${pred.class || 'tumor'}
                        </p>
                        <p style="color:#fca5a5;margin-bottom:10px;">
                            Ishonch: <span style="font-weight:bold;font-size:18px;">${pred.confidence}%</span>
                        </p>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width:${pred.confidence}%;"></div>
                        </div>
                    </div>
                `;
            });
            
            resultState.innerHTML = `
                <div class="card-title">
                    <span class="icon">📊</span> Tahlil natijasi
                </div>
                <div class="preview-container">
                    <img src="data:image/jpeg;base64,${result.image}" style="max-width:100%;max-height:300px;border-radius:15px;border:2px solid rgba(6,182,212,0.5);margin:20px 0;">
                </div>
                <div class="result-box result-detected">
                    <div class="icon-detected">❌</div>
                    <div class="result-title" style="font-size:32px;font-weight:900;margin-bottom:20px;color:#fca5a5;">
                        ⚠️ O'simta aniqlandi!
                    </div>
                    <div style="background:rgba(239,68,68,0.3);padding:15px;border-radius:10px;margin:20px 0;">
                        <p style="font-size:20px;">Soni: <span style="font-weight:900;font-size:28px;">${result.count}</span></p>
                    </div>
                    ${predictionsHTML}
                    <div style="background:rgba(239,68,68,0.3);padding:15px;border-radius:10px;margin-top:20px;">
                        <p style="font-size:14px;">⚕️ Zudlik bilan tibbiy mutaxassis bilan maslahatlashing</p>
                    </div>
                </div>
                <button class="btn btn-info" onclick="showInfo()" style="width:100%;margin-top:20px;padding:15px;background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(255,255,255,0.2);border-radius:12px;font-weight:bold;">
                    Tezkor Tahlil
                </button>
                <button class="btn btn-secondary" onclick="resetForm()" style="margin-top:20px;background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(255,255,255,0.2);padding:12px;border-radius:12px;width:100%;">
                    Yangi tahlil boshlash
                </button>
            `;
        } else {
            resultState.innerHTML = `
                <div class="card-title">
                    <span class="icon">📊</span> Tahlil natijasi
                </div>
                <div class="preview-container">
                    <img src="data:image/jpeg;base64,${result.image}" style="max-width:100%;max-height:300px;border-radius:15px;border:2px solid rgba(6,182,212,0.5);margin:20px 0;">
                </div>
                <div class="result-box result-clean">
                    <div class="icon-clean">✅</div>
                    <div class="result-title" style="font-size:32px;font-weight:900;margin-bottom:20px;color:#86efac;">
                        ✅ O'simta aniqlanmadi
                    </div>
                    <p style="font-size:18px;margin:20px 0;color:#d1fae5;">
                        AI tahlil natijasiga ko'ra, rasmda o'simta belgisi topilmadi.
                    </p>
                    <div style="background:rgba(34,197,94,0.3);padding:15px;border-radius:10px;">
                        <p style="font-size:14px;color:#d1fae5;">
                            ℹ️ Bu natija dastlabki tekshiruv. Aniq tashxis uchun shifokor bilan maslahatlashing.
                        </p>
                    </div>
                </div>
                <button class="btn btn-secondary" onclick="resetForm()" style="margin-top:20px;background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(255,255,255,0.2);padding:12px;border-radius:12px;width:100%;">
                    Yangi tahlil boshlash
                </button>
            `;
        }
    } catch (error) {
        loadingState.classList.add('hidden');
        resultState.classList.remove('hidden');
        resultState.innerHTML = `
            <div style="background:rgba(239,68,68,0.2);border:2px solid rgba(239,68,68,0.5);border-radius:20px;padding:30px;">
                <div style="font-size:48px;margin-bottom:20px;">⚠️</div>
                <h3 style="color:#fca5a5;font-size:24px;margin-bottom:10px;">Xatolik yuz berdi</h3>
                <p style="color:#fca5a5;">${error.message}</p>
            </div>
            <button class="btn btn-secondary" onclick="resetForm()" style="margin-top:20px;background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(255,255,255,0.2);padding:12px;border-radius:12px;width:100%;">
                Qayta urinish
            </button>
        `;
    }
}

function resetForm() {
    if (imageInput) imageInput.value = '';
    if (emptyState) emptyState.classList.remove('hidden');
    if (previewState) previewState.classList.add('hidden');
    if (loadingState) loadingState.classList.add('hidden');
    if (resultState) resultState.classList.add('hidden');
    if (analyzeBtn) analyzeBtn.classList.add('hidden');
}

function showInfo() {
    document.getElementById('infoModal').style.display = 'flex';
}

function hideInfo() {
    document.getElementById('infoModal').style.display = 'none';
}

function showGuide() {
    document.getElementById('guideModal').style.display = 'flex';
}

function hideGuide() {
    document.getElementById('guideModal').style.display = 'none';
}

// Modalni tashqariga bosganda yopish
window.onclick = function(event) {
    const infoModal = document.getElementById('infoModal');
    const guideModal = document.getElementById('guideModal');
    
    if (event.target == infoModal) {
        hideInfo();
    }
    if (event.target == guideModal) {
        hideGuide();
    }
}