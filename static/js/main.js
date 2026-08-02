// ===================== ANIMATED BACKGROUND =====================
(function createBackground() {
    var canvas = document.getElementById('bg-canvas');
    if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = 'bg-canvas';
        document.body.prepend(canvas);
    }
    
    var ctx = canvas.getContext('2d');
    var width, height, particles = [];
    var mouseX = 0, mouseY = 0;

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function Particle() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.size = Math.random() * 3 + 1;
        this.speedX = (Math.random() - 0.5) * 0.5;
        this.speedY = (Math.random() - 0.5) * 0.5;
        this.opacity = Math.random() * 0.3 + 0.1;
        this.color = ['#6C63FF', '#FF6584', '#00D4FF', '#00E676', '#FFD740'][Math.floor(Math.random() * 5)];
    }

    Particle.prototype.update = function() {
        this.x += this.speedX;
        this.y += this.speedY;
        
        var dx = this.x - mouseX;
        var dy = this.y - mouseY;
        var dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 150) {
            var force = (150 - dist) / 150 * 0.5;
            this.x += (dx / dist) * force;
            this.y += (dy / dist) * force;
        }
        
        if (this.x > width) this.x = 0;
        if (this.x < 0) this.x = width;
        if (this.y > height) this.y = 0;
        if (this.y < 0) this.y = height;
    };

    Particle.prototype.draw = function() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color;
        ctx.globalAlpha = this.opacity;
        ctx.fill();
        ctx.globalAlpha = 1;
    };

    for (var i = 0; i < 80; i++) {
        particles.push(new Particle());
    }

    function drawConnections() {
        for (var i = 0; i < particles.length; i++) {
            for (var j = i + 1; j < particles.length; j++) {
                var dx = particles[i].x - particles[j].x;
                var dy = particles[i].y - particles[j].y;
                var dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = 'rgba(108, 99, 255, 0.05)';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        
        for (var i = 0; i < particles.length; i++) {
            particles[i].update();
            particles[i].draw();
        }
        
        drawConnections();
        requestAnimationFrame(animate);
    }

    animate();
})();

// ===================== TOAST =====================
function showToast(msg, type) {
    type = type || 'info';
    var existing = document.querySelectorAll('.toast-pro');
    existing.forEach(function(el) { el.remove(); });

    var container = document.createElement('div');
    container.className = 'toast-pro';
    container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;background:rgba(16,20,30,0.95);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);color:#fff;padding:14px 24px;border-radius:12px;border:1px solid rgba(255,255,255,0.06);box-shadow:0 8px 32px rgba(0,0,0,0.5);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:0.9rem;max-width:420px;';
    
    var colors = {
        success: 'rgba(0,230,118,0.15)',
        danger: 'rgba(255,82,82,0.15)',
        warning: 'rgba(255,215,64,0.15)',
        info: 'rgba(0,212,255,0.15)'
    };
    var borderColors = {
        success: 'rgba(0,230,118,0.2)',
        danger: 'rgba(255,82,82,0.2)',
        warning: 'rgba(255,215,64,0.2)',
        info: 'rgba(0,212,255,0.2)'
    };
    
    container.style.background = colors[type] || colors.info;
    container.style.borderColor = borderColors[type] || borderColors.info;
    container.textContent = msg;
    document.body.appendChild(container);

    setTimeout(function() {
        if (container.parentElement) {
            container.style.transition = 'all 0.3s ease';
            container.style.transform = 'translateX(100px)';
            container.style.opacity = '0';
            setTimeout(function() {
                if (container.parentElement) container.remove();
            }, 300);
        }
    }, 3000);
}

// ===================== COPY =====================
function copyText(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('✓ Copied to clipboard', 'success');
        }).catch(function() {
            fallbackCopy(text);
        });
    } else {
        fallbackCopy(text);
    }
}

function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try {
        document.execCommand('copy');
        showToast('✓ Copied to clipboard', 'success');
    } catch(e) {
        showToast('✗ Failed to copy', 'danger');
    }
    document.body.removeChild(ta);
}

window.showToast = showToast;
window.copyText = copyText;