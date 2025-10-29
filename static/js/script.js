// Background Slider
class BackgroundSlider {
    constructor() {
        this.slides = document.querySelectorAll('.slide');
        this.currentSlide = 0;
        this.slideInterval = null;
        this.init();
    }

    init() {
        if (this.slides.length > 0) {
            this.showSlide(0);
            this.startSlider();
        }
    }

    showSlide(index) {
        this.slides.forEach(slide => slide.classList.remove('active'));
        this.slides[index].classList.add('active');
        this.currentSlide = index;
    }

    nextSlide() {
        let next = this.currentSlide + 1;
        if (next >= this.slides.length) {
            next = 0;
        }
        this.showSlide(next);
    }

    startSlider() {
        this.slideInterval = setInterval(() => {
            this.nextSlide();
        }, 5000); // 5 soniyada bir o'zgaradi
    }

    stopSlider() {
        if (this.slideInterval) {
            clearInterval(this.slideInterval);
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Background Slider
    new BackgroundSlider();

    // File upload functionality
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const emptyState = document.getElementById('emptyState');
    const previewState = document.getElementById('previewState');
    const loadingState = document.getElementById('loadingState');
    const resultState = document.getElementById('resultState');

    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', handleImageUpload);
    }

    // Modal functionality
    window.showInfo = showInfo;
    window.hideInfo = hideInfo;
    window.showGuide = showGuide;
    window.hideGuide = hideGuide;
    window.analyzeImage = analyzeImage;
    window.resetForm = resetForm;
});

function handleImageUpload(e) {
    const file = e.target.files[0];
    if (file) {
        // File size check (10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert('Fayl hajmi 10MB dan oshmasligi kerak!');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            showElement(previewState);
            hideElement(emptyState);
            hideElement(loadingState);
            hideElement(resultState);
            showElement(analyzeBtn);
        };
        reader.readAsDataURL(file);
    }
}

async function analyzeImage() {
    const file = imageInput.files[0];
    if (!file) {
        alert('Iltimos, avval rasm yuklang!');
        return;
    }
    
    hideElement(emptyState);
    hideElement(previewState);
    showElement(loadingState);
    hideElement(resultState);
    hideElement(analyzeBtn);
    
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Server xatosi: ' + response.status);
        }
        
        const result = await response.json();
        
        hideElement(loadingState);
        showElement(resultState);
        
        displayResults(result);
        
    } catch (error) {
        console.error('Tahlil xatosi:', error);
        hideElement(loadingState);
        showElement(resultState);
        displayError(error.message);
    }
}

function displayResults(result) {
    if (result.detected) {
        let predictionsHTML = '';
        result.predictions.forEach((pred, index) => {
            predictionsHTML += `
                <div class="prediction-item">
                    <div class="flex justify-between items-center mb-2">
                        <strong style="color: var(--error);">O'simta #${index + 1}</strong>
                        <span style="color: var(--text-primary); font-weight: 600;">${pred.class || 'tumor'}</span>
                    </div>
                    <div class="flex justify-between items-center mb-2">
                        <span style="color: var(--text-secondary);">Ishonch darajasi:</span>
                        <span style="color: var(--error); font-weight: 700; font-size: 1.1rem;">${pred.confidence}%</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${pred.confidence}%"></div>
                    </div>
                </div>
            `;
        });
        
        resultState.innerHTML = `
            <div class="card-header">
                <div class="card-icon">📊</div>
                <div>
                    <div class="card-title">Tahlil Natijasi</div>
                    <div class="card-subtitle">AI tomonidan aniqlangan miya o'simtalari</div>
                </div>
            </div>
            
            <div class="text-center mb-4">
                <img src="data:image/jpeg;base64,${result.image}" 
                     alt="Tahlil natijasi" 
                     style="max-width: 100%; max-height: 300px; border-radius: 12px; border: 2px solid var(--error);">
            </div>
            
            <div class="result-positive">
                <div class="text-center mb-4">
                    <div class="result-icon" style="color: var(--error);">⚠️</div>
                    <h3 style="color: var(--error); font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">
                        O'simta Aniqlandi!
                    </h3>
                    <div style="background: rgba(239, 68, 68, 0.2); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                        <p style="font-size: 1.2rem; color: var(--text-primary);">
                            Aniqlangan o'simtalar soni: <strong style="color: var(--error); font-size: 1.4rem;">${result.count}</strong>
                        </p>
                    </div>
                </div>
                
                ${predictionsHTML}
                
                <div style="background: rgba(239, 68, 68, 0.2); padding: 1rem; border-radius: 12px; margin-top: 1.5rem;">
                    <p style="color: var(--error); text-align: center; font-weight: 600;">
                        ⚕️ Zudlik bilan tibbiy mutaxassis bilan maslahatlashing!
                    </p>
                </div>
            </div>
            
            <div class="flex gap-3 mt-4" style="display: flex; gap: 1rem;">
                <button class="btn btn-secondary" onclick="showInfo()" style="flex: 1;">
                    ℹ️ Ma'lumot
                </button>
                <button class="btn btn-primary" onclick="resetForm()" style="flex: 1;">
                    🔄 Yangi Tahlil
                </button>
            </div>
        `;
    } else {
        resultState.innerHTML = `
            <div class="card-header">
                <div class="card-icon">📊</div>
                <div>
                    <div class="card-title">Tahlil Natijasi</div>
                    <div class="card-subtitle">AI tomonidan o'tkazilgan miya skaneri tahlili</div>
                </div>
            </div>
            
            <div class="text-center mb-4">
                <img src="data:image/jpeg;base64,${result.image}" 
                     alt="Tahlil natijasi" 
                     style="max-width: 100%; max-height: 300px; border-radius: 12px; border: 2px solid var(--success);">
            </div>
            
            <div class="result-negative">
                <div class="text-center">
                    <div class="result-icon" style="color: var(--success);">✅</div>
                    <h3 style="color: var(--success); font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">
                        O'simta Aniqlanmadi
                    </h3>
                    <p style="color: var(--text-secondary); margin-bottom: 1.5rem; line-height: 1.6;">
                        AI tahlil natijasiga ko'ra, rasmda miya o'simtasi belgilari topilmadi.
                    </p>
                    <div style="background: rgba(16, 185, 129, 0.2); padding: 1rem; border-radius: 12px;">
                        <p style="color: var(--success); font-size: 0.9rem;">
                            ℹ️ Bu natija faqat dastlabki tekshiruv. Aniq tashxis uchun shifokor bilan maslahatlashing.
                        </p>
                    </div>
                </div>
            </div>
            
            <button class="btn btn-primary w-100 mt-4" onclick="resetForm()" style="width: 100%;">
                🔄 Yangi Tahlil Boshlash
            </button>
        `;
    }
}

function displayError(message) {
    resultState.innerHTML = `
        <div class="text-center">
            <div style="font-size: 4rem; margin-bottom: 1rem;">❌</div>
            <h3 style="color: var(--error); margin-bottom: 1rem;">Xatolik Yuz Berdi</h3>
            <p style="color: var(--text-secondary); margin-bottom: 2rem;">${message}</p>
            <button class="btn btn-primary" onclick="resetForm()">
                🔄 Qayta Urinish
            </button>
        </div>
    `;
}

function resetForm() {
    if (imageInput) imageInput.value = '';
    showElement(emptyState);
    hideElement(previewState);
    hideElement(loadingState);
    hideElement(resultState);
    hideElement(analyzeBtn);
}

// Modal functions
function showInfo() {
    document.getElementById('infoModal').style.display = 'flex';
}

function hideInfo() {
    document.getElementById('infoModal').style.display = 'none';
}

function showGuide() {
    // Guide modal - agar kerak bo'lsa keyinroq qo'shishingiz mumkin
    showInfo(); // Hozircha info modalni ko'rsatamiz
}

function hideGuide() {
    hideInfo();
}

// Utility functions
function showElement(element) {
    if (element) element.classList.remove('hidden');
}

function hideElement(element) {
    if (element) element.classList.add('hidden');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}
// Auth form functionality
function initAuthForms() {
    const authForms = document.querySelectorAll('.auth-form');
    
    authForms.forEach(form => {
        const submitBtn = form.querySelector('.auth-btn');
        
        form.addEventListener('submit', function(e) {
            // Basic validation
            const inputs = form.querySelectorAll('.form-input[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    showInputError(input, 'Bu maydon to\'ldirilishi shart');
                } else {
                    clearInputError(input);
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                return;
            }
            
            // Show loading state
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
        
        // Input validation
        const inputs = form.querySelectorAll('.form-input');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            input.addEventListener('input', function() {
                clearInputError(this);
            });
        });
    });
}

function validateInput(input) {
    const value = input.value.trim();
    
    if (input.hasAttribute('required') && !value) {
        showInputError(input, 'Bu maydon to\'ldirilishi shart');
        return false;
    }
    
    if (input.type === 'password' && value.length < 6 && value.length > 0) {
        showInputError(input, 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak');
        return false;
    }
    
    clearInputError(input);
    return true;
}

function showInputError(input, message) {
    clearInputError(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'input-error';
    errorDiv.style.color = 'var(--error)';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '0.5rem';
    errorDiv.textContent = message;
    
    input.style.borderColor = 'var(--error)';
    input.parentElement.appendChild(errorDiv);
}

function clearInputError(input) {
    const errorDiv = input.parentElement.querySelector('.input-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    input.style.borderColor = '';
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initAuthForms();
    
    // Add focus effects to inputs
    const inputs = document.querySelectorAll('.form-input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Check if input has value on page load
        if (input.value) {
            input.parentElement.classList.add('focused');
        }
    });
});