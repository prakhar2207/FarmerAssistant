/**
 * useAntiGravity.js
 * React Hook integration for AntiGravityEngine with Automated Task Completion Reward Loop.
 * 
 * Usage in React components:
 * 
 * import { useAntiGravity } from './useAntiGravity';
 * 
 * function App() {
 *   const { 
 *     isAntiGravityActive, 
 *     toggleAntiGravity, 
 *     enableAntiGravity, 
 *     disableAntiGravity,
 *     triggerAntiGravityBurst 
 *   } = useAntiGravity({
 *     selector: '.floatable, [data-anti-gravity]',
 *     burstDurationMs: 3000,
 *     keyboardShortcut: true // Enable Shift + G shortcut
 *   });
 * 
 *   const handleTaskComplete = async () => {
 *     await performAsyncAction();
 *     triggerAntiGravityBurst({ reason: 'Task Solved!' });
 *   };
 * 
 *   return (
 *     <div>
 *       <button onClick={handleTaskComplete}>Finish Task</button>
 *       <div className="floatable card">Floating Card 1</div>
 *       <div className="floatable card">Floating Card 2</div>
 *     </div>
 *   );
 * }
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import AntiGravityEngine from './AntiGravity.js';

export function useAntiGravity(options = {}) {
  const [isActive, setIsActive] = useState(false);
  const [phase, setPhase] = useState('idle');
  const engineRef = useRef(null);

  useEffect(() => {
    // Instantiate AntiGravityEngine instance
    const engine = new AntiGravityEngine({
      ...options,
      onToggle: (active) => {
        setIsActive(active);
        setPhase(engine.phase || (active ? 'sustain' : 'idle'));
        if (typeof options.onToggle === 'function') {
          options.onToggle(active);
        }
      },
      onBurst: (data) => {
        setIsActive(true);
        setPhase('sustain');
        if (typeof options.onBurst === 'function') {
          options.onBurst(data);
        }
      },
      onSettle: () => {
        setPhase('settle');
        if (typeof options.onSettle === 'function') {
          options.onSettle();
        }
      }
    });

    engineRef.current = engine;

    // Optional keyboard shortcut listener (Shift + G or Alt + G)
    const handleKeyDown = (e) => {
      if (options.keyboardShortcut !== false) {
        if ((e.shiftKey && e.key.toLowerCase() === 'g') || (e.altKey && e.key.toLowerCase() === 'g')) {
          // Avoid triggering when user is typing in inputs or textareas
          const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : '';
          if (activeTag !== 'input' && activeTag !== 'textarea') {
            e.preventDefault();
            engine.toggle();
          }
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    // Cleanup on unmount
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (engineRef.current) {
        engineRef.current.disable();
      }
    };
  }, []);

  const enableAntiGravity = useCallback((burstOpts) => {
    if (engineRef.current) engineRef.current.enable(burstOpts);
  }, []);

  const disableAntiGravity = useCallback(() => {
    if (engineRef.current) engineRef.current.disable();
  }, []);

  const toggleAntiGravity = useCallback(() => {
    if (engineRef.current) return engineRef.current.toggle();
    return false;
  }, []);

  const triggerAntiGravityBurst = useCallback((burstOptions = {}) => {
    if (engineRef.current) {
      return engineRef.current.triggerBurst(burstOptions);
    }
  }, []);

  return {
    isAntiGravityActive: isActive,
    phase,
    enableAntiGravity,
    disableAntiGravity,
    toggleAntiGravity,
    triggerBurst: triggerAntiGravityBurst,
    triggerAntiGravityBurst,
    engine: engineRef.current
  };
}

export default useAntiGravity;
