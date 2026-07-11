import { useEffect, useCallback } from 'react'

interface KeybindConfig {
  key: string
  metaOrCtrl?: boolean
  handler: () => void
  preventDefault?: boolean
}

/**
 * useKeybinds — Power user keyboard control hook
 * Supports Cmd (Mac) or Ctrl (Windows/Linux) combinations
 */
export function useKeybinds(bindings: KeybindConfig[]) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    for (const binding of bindings) {
      const modifierPressed = binding.metaOrCtrl
        ? (e.metaKey || e.ctrlKey)
        : true

      if (
        e.key.toLowerCase() === binding.key.toLowerCase() &&
        modifierPressed
      ) {
        if (binding.preventDefault !== false) e.preventDefault()
        binding.handler()
        break
      }
    }
  }, [bindings])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}