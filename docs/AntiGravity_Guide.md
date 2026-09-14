# AntiGravity UI: Interactive Zero-Gravity Floating Physics Guide

An interactive, high-performance zero-gravity floating physics effect for web interfaces. This module allows UI elements (cards, buttons, chips, badges, dialogs) to float, bounce off viewport boundaries, react to cursor movement, support interactive drag-and-throw momentum, and act as an **automated reward/feedback loop on task completion**.

---

## 🌟 Key Features

- **Automated Task Reward Loop**: Triggers an exhilarating zero-gravity burst whenever a user or background task completes.
- **4-Phase Execution Sequence**:
  1. **Phase 1 (Impulse)**: Initial upward launch $+ (vy \approx -7\text{px/f})$ with random angular rotation impulse and cosmic sparkle particles.
  2. **Phase 2 (Sustain)**: Micro-gravity drift, boundary bouncing, and pointer interaction for `durationMs` (default: 3.0s).
  3. **Phase 3 (Auto-Dock / Settle)**: Smooth spring cubic-bezier interpolation (`cubic-bezier(0.22, 1, 0.36, 1)`) back to $(0,0,0)$ without layout snapping.
  4. **Phase 4 (Ready State)**: Physics loops cancel cleanly, and all DOM inline overrides are purged so normal interactions resume instantly.
- **Queue & Debounce Protection**: If new tasks finish while an effect is already active, an **additive impulse** is applied to existing bodies and the sustain timer resets without duplicating loops or freezing the DOM.
- **Accessibility Override**: Fully respects `prefers-reduced-motion: reduce` by bypassing the physics engine and showing a celebratory accessible toast & micro-pulse animation.
- **Zero Layout Shifts**: Caches original DOM coordinates (`getBoundingClientRect()`) prior to detaching so the UI resets cleanly to its exact layout coordinates.
- **60 FPS Hardware Acceleration**: Physics positioning is updated via GPU-accelerated CSS `transform: translate3d(...) rotate(...)` transforms.
- **Pointer Repulsion & Click Pulse**: Moving the cursor pushes elements away; clicking empty space emits an outward shockwave impulse.
- **Interactive Drag & Throw**: Users can grab floating elements, move them freely, and fling them across the viewport with momentum.

---

## 🚀 Automated Task Reward Loop

### 1. Programmatic Trigger API
Call `triggerBurst()` on the engine instance or global dispatcher:

```javascript
// Global shortcut
window.triggerAntiGravityBurst({
  durationMs: 3000,           // Sustain duration in ms (default: 3000)
  impulseMultiplier: 1.0,     // Velocity force scaling (default: 1.0)
  reason: 'Soil Report Ready!'// Displayed in celebratory banner
});

// Or via engine instance:
antigravity.triggerBurst({ durationMs: 3000, reason: 'Disease Diagnosed' });
```

### 2. Custom Event Lifecycle Listeners
Dispatch standard browser events anywhere in your app:

```javascript
// Trigger burst via custom event:
window.dispatchEvent(new CustomEvent('antigravity:burst', {
  detail: { durationMs: 3000, reason: 'AI Advice Generated' }
}));

// Or listen to generic task completion events:
window.dispatchEvent(new CustomEvent('task:completed', {
  detail: { task: 'Crop ML Recommendation Completed', durationMs: 2500 }
}));
```

---

## 🛠️ Step-by-Step Integration

### 1. Marking Floatable DOM Elements

To mark specific HTML elements that should float when Anti-Gravity mode activates, add `.floatable` or `data-anti-gravity`:

```html
<!-- Cards -->
<div class="card floatable">
  <h3>Fertilizer Recommendations</h3>
  <p>Balanced schedule for Urea, DAP, and Potash.</p>
</div>

<!-- Buttons & Badges -->
<button class="pill-btn" data-anti-gravity>
  📷 Leaf Health Check
</button>
<span class="badge floatable">Multimodal RAG</span>
```

---

### 2. Vanilla JavaScript Usage (`AntiGravity.js`)

```html
<script src="/js/AntiGravity.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', () => {
    // Instantiate Anti-Gravity Engine
    const ag = new AntiGravityEngine({
      selector: '.floatable, [data-anti-gravity]',
      gravity: -0.08,
      damping: 0.988,
      burstDurationMs: 3000,
      respectReducedMotion: true,
      onToggle: (isActive) => console.log('Zero-G Active:', isActive),
      onBurst: ({ reason, durationMs }) => console.log('Reward Burst:', reason),
      onSettle: () => console.log('Elements Docked')
    });

    window.antigravity = ag;

    // Keyboard shortcut (Shift + G)
    window.addEventListener('keydown', (e) => {
      if (e.shiftKey && e.key.toLowerCase() === 'g') ag.toggle();
    });
  });

  // Example: Hook an API call completion
  async function submitTask() {
    const res = await fetch('/api/task');
    const data = await res.json();
    if (data.success) {
      window.triggerAntiGravityBurst({ reason: 'Task Solved!' });
    }
  }
</script>
```

---

### 3. React Integration (`useAntiGravity` Hook)

```jsx
import React from 'react';
import { useAntiGravity } from './useAntiGravity';

export function Dashboard() {
  const { 
    isAntiGravityActive, 
    phase, 
    toggleAntiGravity, 
    triggerAntiGravityBurst 
  } = useAntiGravity({
    selector: '.floatable, [data-anti-gravity]',
    burstDurationMs: 3000,
    keyboardShortcut: true // Listens for Shift + G
  });

  const handleFinishTask = async () => {
    await performTask();
    triggerAntiGravityBurst({ reason: 'Mission Accomplished!' });
  };

  return (
    <div className="dashboard-container">
      <header>
        <button onClick={toggleAntiGravity}>
          {isAntiGravityActive ? '🛸 Landing Mode' : '🚀 Zero-G Mode'}
        </button>
        <button onClick={handleFinishTask}>
          ✨ Complete Task (Reward Burst)
        </button>
      </header>

      <div className="cards-grid">
        <div className="card floatable">
          <h3>Weather Advisory</h3>
          <p>Lucknow: 28°C ☀️ Rain probability: 10%</p>
        </div>
      </div>
    </div>
  );
}
```

---

## ⚙️ API Configuration Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `selector` | `string` | `'.floatable, [data-anti-gravity]'` | CSS selector of elements that should float |
| `gravity` | `number` | `-0.08` | Upward drift acceleration in px/frame² |
| `damping` | `number` | `0.988` | Air resistance friction multiplier (0 to 1) |
| `rotDamping` | `number` | `0.96` | Rotational friction multiplier |
| `elasticity` | `number` | `0.8` | Viewport boundary bounce coefficient |
| `repulsionRadius`| `number` | `190` | Pointer repulsion distance in pixels |
| `repulsionStrength`| `number`| `500` | Repulsion force magnitude multiplier |
| `clickImpulseStrength`| `number`| `14` | Shockwave force on empty space click |
| `enableDrag` | `boolean`| `true` | Enables click/drag and throw momentum |
| `autoResize` | `boolean`| `true` | Recalculates layout anchors on window resize |
| `burstDurationMs` | `number`| `3000` | Default sustain drift duration for reward bursts |
| `impulseMultiplier` | `number`| `1.0` | Multiplier for upward & angular launch velocity |
| `respectReducedMotion` | `boolean`| `true` | Replaces physics with subtle pulse for reduced-motion users |
| `onToggle` | `function`| `null` | Callback function `(isActive) => {}` |
| `onBurst` | `function`| `null` | Callback function `({ reason, durationMs }) => {}` |
| `onSettle` | `function`| `null` | Callback function `() => {}` when docking initiates |

---

## ♿ Accessibility (`prefers-reduced-motion`)

When users configure their operating system with `prefers-reduced-motion: reduce`:
1. The 3D translation & rotation physics loop is **bypassed**.
2. An accessible notification toast (`.ag-reduced-motion-toast`) renders at the top with the task success state.
3. A subtle scale/glow micro-pulse (`.ag-reduced-pulse`) highlights the cards without disorienting movement.
