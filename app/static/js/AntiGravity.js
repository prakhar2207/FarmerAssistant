/**
 * AntiGravityEngine.js
 * High-performance, zero-dependency interactive Zero-Gravity / Floating UI Physics Engine.
 * 
 * Features:
 * - Automated Reward Burst Loop on Task Completion (Impulse -> Sustain -> Auto-Dock -> Ready State).
 * - 60 FPS requestAnimationFrame physics loop using GPU-accelerated translate3d transforms.
 * - Zero layout shifts: Caches DOM positions (getBoundingClientRect()) for clean layout reset.
 * - Additive impulse & queue/debounce protection for rapid consecutive triggers.
 * - Accessibility override respecting `prefers-reduced-motion: reduce`.
 * - Micro-gravity upward drift, space friction damping, and Brownian motion.
 * - Soft viewport boundary bounce collisions.
 * - Pointer force repulsion (hover impulse) and shockwave click pulse.
 * - Interactive Drag & Throw with residual release momentum.
 * - Smooth cubic-bezier spring reset returning elements cleanly to original coordinates.
 */

(function (global, factory) {
  if (typeof module === 'object' && typeof module.exports === 'object') {
    module.exports = factory();
  } else if (typeof define === 'function' && define.amd) {
    define(factory);
  } else {
    global.AntiGravityEngine = factory();
  }
}(typeof window !== 'undefined' ? window : this, function () {
  'use strict';

  class AntiGravityEngine {
    constructor(options = {}) {
      this.options = Object.assign({
        selector: '.floatable, [data-anti-gravity]',
        gravity: -0.08,             // Upward drift acceleration (px/frame^2)
        damping: 0.988,             // Air resistance friction
        rotDamping: 0.96,          // Rotational velocity friction
        elasticity: 0.8,            // Viewport boundary bounce coefficient
        repulsionRadius: 190,       // Distance in px for mouse hover repulsion force
        repulsionStrength: 500,     // Repulsion force magnitude
        clickImpulseStrength: 14,   // Shockwave force on click
        enableDrag: true,           // Allow drag and throw interactivity
        autoResize: true,           // Recalculate anchors on window resize
        respectReducedMotion: true, // Respect prefers-reduced-motion: reduce
        burstDurationMs: 3000,      // Default sustain duration for task completion burst
        impulseMultiplier: 1.0,     // Scaling multiplier for impulse force
        onToggle: null,             // Callback function(isActive)
        onBurst: null,              // Callback function({ reason, durationMs })
        onSettle: null              // Callback function()
      }, options);

      this.isActive = false;
      this.phase = 'idle';          // 'idle' | 'impulse' | 'sustain' | 'settle'
      this.bodies = [];
      this.pointer = { x: -9999, y: -9999, isDown: false, downTarget: null };
      this.activeDragBody = null;
      this.animFrameId = null;
      this.burstTimer = null;
      this.settleTimer = null;
      this.spaceCanvas = null;
      this.spaceCtx = null;
      this.particles = [];

      // Bound methods
      this.step = this.step.bind(this);
      this.handlePointerMove = this.handlePointerMove.bind(this);
      this.handlePointerDown = this.handlePointerDown.bind(this);
      this.handlePointerUp = this.handlePointerUp.bind(this);
      this.handleClick = this.handleClick.bind(this);
      this.handleResize = this.handleResize.bind(this);
      this.triggerBurst = this.triggerBurst.bind(this);

      // Register global custom event listeners for lifecycle triggers
      if (typeof window !== 'undefined') {
        window.addEventListener('antigravity:burst', (e) => {
          this.triggerBurst(e.detail || {});
        });
        window.addEventListener('task:completed', (e) => {
          this.triggerBurst({
            reason: (e.detail && e.detail.task) || 'Task Completed',
            durationMs: (e.detail && e.detail.durationMs) || this.options.burstDurationMs
          });
        });

        // Global convenience dispatcher
        window.triggerAntiGravityBurst = (opts) => this.triggerBurst(opts);
      }
    }

    /**
     * Check if user prefers reduced motion.
     */
    _prefersReducedMotion() {
      if (!this.options.respectReducedMotion) return false;
      if (typeof window === 'undefined' || !window.matchMedia) return false;
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    /**
     * Trigger an automated Anti-Gravity Burst Reward Loop.
     * Execution Sequence: Phase 1 (Impulse) -> Phase 2 (Sustain) -> Phase 3 (Auto-Dock) -> Phase 4 (Ready State).
     * Includes Queue & Debounce protection with additive impulse.
     *
     * @param {Object} options
     * @param {number} [options.durationMs=3000] Sustain duration in ms
     * @param {number} [options.impulseMultiplier=1.0] Multiplier for burst velocities
     * @param {string} [options.reason='Task Completed'] Human-readable task trigger reason
     */
    triggerBurst(options = {}) {
      const durationMs = options.durationMs || this.options.burstDurationMs || 3000;
      const impulseMult = options.impulseMultiplier || this.options.impulseMultiplier || 1.0;
      const reason = options.reason || 'Task Completed';

      // Accessibility Override: prefers-reduced-motion
      if (this._prefersReducedMotion()) {
        this._triggerReducedMotionFeedback(reason);
        return;
      }

      // ==========================================
      // Queue & Debounce Protection
      // ==========================================
      if (this.isActive) {
        // If currently in Auto-Dock / Settle phase, interrupt settle immediately without jump!
        if (this.phase === 'settle') {
          if (this.settleTimer) {
            clearTimeout(this.settleTimer);
            this.settleTimer = null;
          }

          // Capture current in-flight positions and disable CSS transitions
          this.bodies.forEach(body => {
            const computed = window.getComputedStyle(body.element);
            const transform = computed.transform;
            if (transform && transform !== 'none') {
              const match = transform.match(/matrix(?:3d)?\((.+)\)/);
              if (match) {
                const values = match[1].split(',').map(parseFloat);
                if (values.length === 6) {
                  body.x = values[4];
                  body.y = values[5];
                } else if (values.length === 16) {
                  body.x = values[12];
                  body.y = values[13];
                }
              }
            }
            body.element.style.transition = 'none';
            body.element.classList.remove('ag-settling');
            body.element.classList.add('ag-floating-body');
          });

          // Resume physics loop if cancelled
          if (!this.animFrameId) {
            this.animFrameId = requestAnimationFrame(this.step);
          }
        }

        // Apply additive upward & angular impulses to existing floating bodies
        this.bodies.forEach(body => {
          body.vy -= (Math.random() * 3.8 + 3.2) * impulseMult; // Additive upward kick
          body.vx += (Math.random() - 0.5) * 5.0 * impulseMult;
          body.vRot += (Math.random() - 0.5) * 4.5 * impulseMult;
        });

        // Reset sustain timer (Debounce/Queue protection: extends sustain window)
        if (this.burstTimer) clearTimeout(this.burstTimer);
        this.phase = 'sustain';
        this._showBurstRewardBanner(reason, durationMs);
        this._triggerParticleBurst();

        this.burstTimer = setTimeout(() => {
          this._autoDockAndSettle();
        }, durationMs);

        return;
      }

      // ==========================================
      // Phase 1 (Impulse): Fresh activation
      // ==========================================
      this.phase = 'impulse';
      this.enable({ initialBurst: true, impulseMultiplier: impulseMult });
      this.phase = 'sustain';

      this._showBurstRewardBanner(reason, durationMs);
      this._triggerParticleBurst();

      if (typeof this.options.onBurst === 'function') {
        this.options.onBurst({ reason, durationMs });
      }

      // ==========================================
      // Phase 2 (Sustain): Drift for durationMs
      // ==========================================
      if (this.burstTimer) clearTimeout(this.burstTimer);
      this.burstTimer = setTimeout(() => {
        this._autoDockAndSettle();
      }, durationMs);
    }

    /**
     * Phase 3 (Auto-Dock / Settle) & Phase 4 (Ready State)
     * Interpolate elements smoothly back to resting positions and clean up DOM overrides.
     */
    _autoDockAndSettle() {
      if (!this.isActive) return;
      this.phase = 'settle';

      // Stop physics step loop from overriding CSS transforms
      if (this.animFrameId) {
        cancelAnimationFrame(this.animFrameId);
        this.animFrameId = null;
      }

      if (this.burstTimer) {
        clearTimeout(this.burstTimer);
        this.burstTimer = null;
      }

      // Phase 3: Auto-Dock / Settle with smooth spring-easing transition
      this.bodies.forEach(body => {
        const el = body.element;
        // High-fidelity spring easing curve back to (0,0,0)
        el.style.transition = 'transform 0.78s cubic-bezier(0.22, 1, 0.36, 1)';
        el.style.transform = el.dataset.agOrigTransform || 'translate3d(0px, 0px, 0px) rotate(0deg)';
        el.classList.remove('ag-floating-body', 'ag-dragging');
        el.classList.add('ag-settling');
      });

      this._hideBurstRewardBanner();

      if (typeof this.options.onSettle === 'function') {
        this.options.onSettle();
      }

      // Phase 4: Ready State
      // Once CSS transition completes (~780ms), release DOM overrides and resume normal interaction
      this.settleTimer = setTimeout(() => {
        this._releaseDOMOverrides();
        this.phase = 'idle';
        this.isActive = false;
        this.settleTimer = null;

        if (typeof this.options.onToggle === 'function') {
          this.options.onToggle(false);
        }
      }, 800);
    }

    /**
     * Phase 4 Cleanup: Purge inline overrides, event listeners, and background canvas.
     */
    _releaseDOMOverrides() {
      window.removeEventListener('pointermove', this.handlePointerMove);
      window.removeEventListener('pointerdown', this.handlePointerDown);
      window.removeEventListener('pointerup', this.handlePointerUp);
      window.removeEventListener('click', this.handleClick);
      window.removeEventListener('resize', this.handleResize);

      document.body.classList.remove('antigravity-active');
      this._removeSpaceCanvas();

      this.bodies.forEach(body => {
        const el = body.element;
        el.style.transition = el.dataset.agOrigTransition || '';
        el.style.willChange = el.dataset.agOrigWillChange || '';
        el.style.zIndex = el.dataset.agOrigZIndex || '';
        el.classList.remove('ag-floating-body', 'ag-dragging', 'ag-settling');
        delete el.dataset.agOrigTransform;
        delete el.dataset.agOrigTransition;
        delete el.dataset.agOrigZIndex;
        delete el.dataset.agOrigWillChange;
      });
      this.bodies = [];
    }

    /**
     * Enable Anti-Gravity mode manually or via burst.
     */
    enable(burstOpts = null) {
      if (this.isActive && !burstOpts) return;
      this.isActive = true;

      if (this.settleTimer) {
        clearTimeout(this.settleTimer);
        this.settleTimer = null;
      }

      // Query elements
      let elements = Array.from(document.querySelectorAll(this.options.selector));
      
      // Fallback selector if none found explicitly
      if (elements.length === 0) {
        elements = Array.from(document.querySelectorAll(
          '.starter-card, .tool-link-btn, .pill-btn, .weather-pill, .model-badge, .user-profile-widget, .new-chat-btn, .modal-dialog, .assistant-bubble'
        ));
      }

      // Filter out hidden or non-visible elements
      elements = elements.filter(el => {
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).display !== 'none';
      });

      if (elements.length === 0) {
        console.warn('AntiGravityEngine: No floatable elements found on page.');
      }

      // Build physics bodies with cached layout positions
      const isBurst = burstOpts && burstOpts.initialBurst;
      const mult = (burstOpts && burstOpts.impulseMultiplier) || 1.0;

      this.bodies = elements.map((el, index) => {
        const rect = el.getBoundingClientRect();
        
        // Save initial inline styles to restore cleanly later
        el.dataset.agOrigTransform = el.style.transform || '';
        el.dataset.agOrigTransition = el.style.transition || '';
        el.dataset.agOrigZIndex = el.style.zIndex || '';
        el.dataset.agOrigWillChange = el.style.willChange || '';

        // Prepare element for hardware acceleration
        el.style.willChange = 'transform';
        el.style.transition = 'none';
        el.classList.add('ag-floating-body');

        // Phase 1 (Impulse): Upward + random angular velocity impulse
        let initialVx, initialVy, initialVRot, initialRot;
        if (isBurst) {
          initialVx = (Math.random() - 0.5) * 6.5 * mult;
          initialVy = -(Math.random() * 4.5 + 4.5) * mult; // Strong upward impulse
          initialVRot = (Math.random() - 0.5) * 5.5 * mult;
          initialRot = (Math.random() - 0.5) * 8;
        } else {
          const angle = Math.random() * Math.PI * 2;
          const initialSpeed = 0.5 + Math.random() * 1.5;
          initialVx = Math.cos(angle) * initialSpeed;
          initialVy = Math.sin(angle) * initialSpeed - 1.2;
          initialVRot = (Math.random() - 0.5) * 0.6;
          initialRot = (Math.random() - 0.5) * 4;
        }

        return {
          id: index,
          element: el,
          origRect: {
            left: rect.left,
            top: rect.top,
            width: rect.width,
            height: rect.height,
            centerX: rect.left + rect.width / 2,
            centerY: rect.top + rect.height / 2
          },
          x: 0,
          y: 0,
          vx: initialVx,
          vy: initialVy,
          rotation: initialRot,
          vRot: initialVRot,
          mass: Math.max(1, (rect.width * rect.height) / 10000),
          isDragging: false,
          dragOffsetX: 0,
          dragOffsetY: 0,
          lastPointerX: 0,
          lastPointerY: 0,
          lastPointerTime: 0
        };
      });

      // Add space background effect
      this._initSpaceCanvas();

      // Attach event listeners
      window.addEventListener('pointermove', this.handlePointerMove, { passive: true });
      window.addEventListener('pointerdown', this.handlePointerDown);
      window.addEventListener('pointerup', this.handlePointerUp);
      window.addEventListener('click', this.handleClick);
      if (this.options.autoResize) {
        window.addEventListener('resize', this.handleResize);
      }

      document.body.classList.add('antigravity-active');

      // Start physics loop
      this.animFrameId = requestAnimationFrame(this.step);

      if (typeof this.options.onToggle === 'function') {
        this.options.onToggle(true);
      }
    }

    /**
     * Disable Anti-Gravity mode & cleanly reset elements to original grid layout.
     */
    disable() {
      if (!this.isActive) return;
      if (this.burstTimer) {
        clearTimeout(this.burstTimer);
        this.burstTimer = null;
      }
      this._autoDockAndSettle();
    }

    /**
     * Toggle Zero-Gravity state.
     */
    toggle() {
      if (this.isActive) {
        this.disable();
      } else {
        this.enable();
      }
      return this.isActive;
    }

    /**
     * Main Physics Simulation Loop (60 FPS).
     */
    step(timestamp) {
      if (!this.isActive) return;

      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;

      // Update background space particles
      this._updateSpaceCanvas(viewportWidth, viewportHeight);

      // Physics calculation for each floating body
      const numBodies = this.bodies.length;

      for (let i = 0; i < numBodies; i++) {
        const body = this.bodies[i];

        if (body.isDragging) {
          // Direct tracking during user drag
          const targetX = this.pointer.x - body.origRect.left - body.dragOffsetX;
          const targetY = this.pointer.y - body.origRect.top - body.dragOffsetY;

          const now = performance.now();
          const dt = Math.max(1, now - body.lastPointerTime);

          // Smooth velocity estimation for throw release
          body.vx = ((targetX - body.x) / dt) * 16.6;
          body.vy = ((targetY - body.y) / dt) * 16.6;
          body.vRot = body.vx * 0.05;

          body.x = targetX;
          body.y = targetY;

          body.lastPointerTime = now;
        } else {
          // 1. Upward Micro-Gravity & Brownian Float
          body.vy += this.options.gravity / body.mass;
          body.vx += (Math.random() - 0.5) * 0.08;
          body.vy += (Math.random() - 0.5) * 0.08;
          body.vRot += (Math.random() - 0.5) * 0.03;

          // 2. Mouse Pointer Repulsion Force (Hover Impulse)
          const currentCenterX = body.origRect.left + body.x + body.origRect.width / 2;
          const currentCenterY = body.origRect.top + body.y + body.origRect.height / 2;

          const dx = currentCenterX - this.pointer.x;
          const dy = currentCenterY - this.pointer.y;
          const dist = Math.hypot(dx, dy);

          if (dist < this.options.repulsionRadius && dist > 1) {
            const forceNorm = (1 - dist / this.options.repulsionRadius);
            const force = (forceNorm * forceNorm * this.options.repulsionStrength) / (dist + 30);
            
            const ax = (dx / dist) * force;
            const ay = (dy / dist) * force;

            body.vx += ax / body.mass;
            body.vy += ay / body.mass;
            body.vRot += (dx > 0 ? 0.3 : -0.3) * forceNorm;
          }

          // 3. Body-to-Body Soft Repulsion (Prevents stacking/clumping)
          for (let j = i + 1; j < numBodies; j++) {
            const other = this.bodies[j];
            if (other.isDragging) continue;

            const oCenterX = other.origRect.left + other.x + other.origRect.width / 2;
            const oCenterY = other.origRect.top + other.y + other.origRect.height / 2;

            const bDx = currentCenterX - oCenterX;
            const bDy = currentCenterY - oCenterY;
            const bDist = Math.hypot(bDx, bDy);
            const minDist = (Math.max(body.origRect.width, body.origRect.height) + Math.max(other.origRect.width, other.origRect.height)) * 0.45;

            if (bDist < minDist && bDist > 1) {
              const rep = (minDist - bDist) * 0.03;
              const rX = (bDx / bDist) * rep;
              const rY = (bDy / bDist) * rep;

              body.vx += rX;
              body.vy += rY;
              other.vx -= rX;
              other.vy -= rY;
            }
          }

          // 4. Update Position & Rotation
          body.x += body.vx;
          body.y += body.vy;
          body.rotation += body.vRot;

          // 5. Air Resistance / Friction Damping
          body.vx *= this.options.damping;
          body.vy *= this.options.damping;
          body.vRot *= this.options.rotDamping;

          // 6. Viewport Boundary Collisions & Elastic Bouncing
          const bodyLeft = body.origRect.left + body.x;
          const bodyRight = bodyLeft + body.origRect.width;
          const bodyTop = body.origRect.top + body.y;
          const bodyBottom = bodyTop + body.origRect.height;
          const elasticity = this.options.elasticity;

          // Left Wall
          if (bodyLeft < 10) {
            body.x = 10 - body.origRect.left;
            body.vx = Math.abs(body.vx) * elasticity + 0.5;
            body.vRot += body.vy * 0.08;
          }
          // Right Wall
          else if (bodyRight > viewportWidth - 10) {
            body.x = (viewportWidth - 10) - body.origRect.left - body.origRect.width;
            body.vx = -Math.abs(body.vx) * elasticity - 0.5;
            body.vRot -= body.vy * 0.08;
          }

          // Top Wall
          if (bodyTop < 10) {
            body.y = 10 - body.origRect.top;
            body.vy = Math.abs(body.vy) * elasticity + 0.5;
            body.vRot += body.vx * 0.08;
          }
          // Bottom Wall
          else if (bodyBottom > viewportHeight - 10) {
            body.y = (viewportHeight - 10) - body.origRect.top - body.origRect.height;
            body.vy = -Math.abs(body.vy) * elasticity - 0.5;
            body.vRot -= body.vy * 0.08;
          }
        }

        // Render CSS transform
        const transformStr = `translate3d(${body.x.toFixed(2)}px, ${body.y.toFixed(2)}px, 0px) rotate(${body.rotation.toFixed(2)}deg)`;
        body.element.style.transform = transformStr;
        body.element.style.zIndex = body.isDragging ? '9999' : '1000';
      }

      this.animFrameId = requestAnimationFrame(this.step);
    }

    /* ----------------------------------------------------
     * Event Handlers (Pointer & Drag-and-Throw)
     * ---------------------------------------------------- */
    handlePointerMove(e) {
      this.pointer.x = e.clientX;
      this.pointer.y = e.clientY;
    }

    handlePointerDown(e) {
      if (!this.isActive || !this.options.enableDrag) return;
      this.pointer.x = e.clientX;
      this.pointer.y = e.clientY;

      // Find if pointer is down on a floating body
      const target = e.target.closest('.ag-floating-body');
      if (!target) return;

      const body = this.bodies.find(b => b.element === target);
      if (body) {
        body.isDragging = true;
        body.element.classList.add('ag-dragging');
        this.activeDragBody = body;

        // Calculate offset between click position and element top-left
        const currentLeft = body.origRect.left + body.x;
        const currentTop = body.origRect.top + body.y;
        body.dragOffsetX = e.clientX - currentLeft;
        body.dragOffsetY = e.clientY - currentTop;
        body.lastPointerTime = performance.now();
      }
    }

    handlePointerUp(e) {
      if (this.activeDragBody) {
        this.activeDragBody.isDragging = false;
        this.activeDragBody.element.classList.remove('ag-dragging');
        
        // Apply extra throw boost on release
        this.activeDragBody.vx = Math.max(-25, Math.min(25, this.activeDragBody.vx * 1.2));
        this.activeDragBody.vy = Math.max(-25, Math.min(25, this.activeDragBody.vy * 1.2));

        this.activeDragBody = null;
      }
    }

    handleClick(e) {
      if (!this.isActive) return;
      
      // If user clicked empty space, trigger shockwave pulse
      if (!e.target.closest('.ag-floating-body')) {
        const clickX = e.clientX;
        const clickY = e.clientY;
        const pulseStrength = this.options.clickImpulseStrength;

        this.bodies.forEach(body => {
          const centerX = body.origRect.left + body.x + body.origRect.width / 2;
          const centerY = body.origRect.top + body.y + body.origRect.height / 2;

          const dx = centerX - clickX;
          const dy = centerY - clickY;
          const dist = Math.hypot(dx, dy);

          if (dist < 400 && dist > 1) {
            const impulse = (1 - dist / 400) * pulseStrength;
            body.vx += (dx / dist) * impulse;
            body.vy += (dy / dist) * impulse;
            body.vRot += (Math.random() - 0.5) * impulse;
          }
        });
      }
    }

    handleResize() {
      if (!this.isActive) return;
      // Recalculate original rects on window resize
      this.bodies.forEach(body => {
        const rect = body.element.getBoundingClientRect();
        body.origRect.width = rect.width;
        body.origRect.height = rect.height;
      });
    }

    /* ----------------------------------------------------
     * Celebratory Reward Burst Banner & Status
     * ---------------------------------------------------- */
    _showBurstRewardBanner(reason = 'Task Complete', durationMs = 3000) {
      const banner = document.getElementById('zero-g-status-banner');
      if (!banner) return;

      const statusText = document.getElementById('zero-g-status-text');
      if (statusText) {
        statusText.innerHTML = `✨ <strong>${this._escapeHtml(reason)}</strong> — Zero-G Reward Active! (Auto-docking in ${(durationMs / 1000).toFixed(1)}s)`;
      }
      banner.classList.add('visible', 'ag-reward-burst');
    }

    _hideBurstRewardBanner() {
      const banner = document.getElementById('zero-g-status-banner');
      if (!banner) return;
      banner.classList.remove('ag-reward-burst');
      // If user didn't manually toggle persistent zero-g, hide banner
      if (!this.isActive || this.phase === 'settle') {
        banner.classList.remove('visible');
      }
    }

    /* ----------------------------------------------------
     * Accessibility Override (prefers-reduced-motion)
     * ---------------------------------------------------- */
    _triggerReducedMotionFeedback(reason = 'Task Complete') {
      window.dispatchEvent(new CustomEvent('antigravity:reduced-motion', { detail: { reason } }));

      // Create or update accessible reward toast
      let toast = document.getElementById('ag-reduced-motion-toast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'ag-reduced-motion-toast';
        toast.className = 'ag-reduced-motion-toast';
        document.body.appendChild(toast);
      }

      toast.innerHTML = `
        <span class="toast-icon">✨</span>
        <span class="toast-text">${this._escapeHtml(reason)} — <strong>Success!</strong></span>
      `;
      toast.classList.add('visible');

      // Subtle accessible micro-animation pulse
      const targets = document.querySelectorAll(this.options.selector);
      targets.forEach(el => {
        el.classList.remove('ag-reduced-pulse');
        void el.offsetWidth; // Force reflow
        el.classList.add('ag-reduced-pulse');
      });

      setTimeout(() => {
        if (toast) toast.classList.remove('visible');
        targets.forEach(el => el.classList.remove('ag-reduced-pulse'));
      }, 2800);
    }

    _escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.innerText = text;
      return div.innerHTML;
    }

    /* ----------------------------------------------------
     * Background Space Canvas & Micro-Particle Stars
     * ---------------------------------------------------- */
    _initSpaceCanvas() {
      let canvas = document.getElementById('ag-space-canvas');
      if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = 'ag-space-canvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '999';
        canvas.style.opacity = '0';
        canvas.style.transition = 'opacity 0.8s ease';
        document.body.appendChild(canvas);
      }

      this.spaceCanvas = canvas;
      this.spaceCtx = canvas.getContext('2d');

      const w = window.innerWidth;
      const h = window.innerHeight;
      canvas.width = w;
      canvas.height = h;

      // Spawn subtle cosmic floating particles
      this.particles = [];
      for (let i = 0; i < 45; i++) {
        this.particles.push({
          x: Math.random() * w,
          y: Math.random() * h,
          radius: Math.random() * 2 + 0.8,
          alpha: Math.random() * 0.6 + 0.2,
          vx: (Math.random() - 0.5) * 0.3,
          vy: -Math.random() * 0.4 - 0.1,
          color: '#10a37f',
          isBurst: false
        });
      }

      requestAnimationFrame(() => {
        if (this.spaceCanvas) this.spaceCanvas.style.opacity = '1';
      });
    }

    _triggerParticleBurst() {
      if (!this.spaceCanvas || !this.particles) return;
      const w = window.innerWidth;
      const h = window.innerHeight;
      const centerX = w / 2;
      const centerY = h * 0.4;
      const colors = ['#10a37f', '#a78bfa', '#38bdf8', '#f59e0b', '#34d399', '#ec4899'];

      for (let i = 0; i < 40; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 7 + 3;
        this.particles.push({
          x: centerX + (Math.random() - 0.5) * 120,
          y: centerY + (Math.random() - 0.5) * 120,
          radius: Math.random() * 2.8 + 1.2,
          alpha: 1.0,
          decay: 0.015 + Math.random() * 0.02,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed - 2.5,
          color: colors[Math.floor(Math.random() * colors.length)],
          isBurst: true
        });
      }
    }

    _updateSpaceCanvas(width, height) {
      if (!this.spaceCtx || !this.spaceCanvas) return;

      if (this.spaceCanvas.width !== width || this.spaceCanvas.height !== height) {
        this.spaceCanvas.width = width;
        this.spaceCanvas.height = height;
      }

      const ctx = this.spaceCtx;
      ctx.clearRect(0, 0, width, height);

      for (let i = this.particles.length - 1; i >= 0; i--) {
        const p = this.particles[i];
        p.x += p.vx;
        p.y += p.vy;

        if (p.isBurst) {
          p.vx *= 0.96;
          p.vy *= 0.96;
          p.alpha -= p.decay;
          if (p.alpha <= 0) {
            this.particles.splice(i, 1);
            continue;
          }
        } else {
          if (p.y < -10) p.y = height + 10;
          if (p.x < -10) p.x = width + 10;
          if (p.x > width + 10) p.x = -10;
        }

        ctx.fillStyle = p.color || '#10a37f';
        ctx.globalAlpha = Math.max(0, Math.min(1, p.alpha));
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1.0;
    }

    _removeSpaceCanvas() {
      if (this.spaceCanvas) {
        this.spaceCanvas.style.opacity = '0';
        setTimeout(() => {
          if (this.spaceCanvas && this.spaceCanvas.parentNode) {
            this.spaceCanvas.parentNode.removeChild(this.spaceCanvas);
          }
          this.spaceCanvas = null;
          this.spaceCtx = null;
        }, 800);
      }
    }
  }

  return AntiGravityEngine;
}));
