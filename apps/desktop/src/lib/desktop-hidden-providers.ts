import type { ModelOptionsResponse } from '@/types/hermes'

/** OAuth + model providers the Berdaya desktop app does not surface. */
export const HIDDEN_DESKTOP_PROVIDER_IDS = new Set(['nous'])

export function filterDesktopOAuthProviders<T extends { id: string }>(providers: readonly T[]): T[] {
  return providers.filter(provider => !HIDDEN_DESKTOP_PROVIDER_IDS.has(provider.id))
}

export function filterDesktopModelProviders<T extends { slug: string }>(providers: readonly T[]): T[] {
  return providers.filter(provider => !HIDDEN_DESKTOP_PROVIDER_IDS.has(provider.slug))
}

export function filterDesktopModelOptions(options: ModelOptionsResponse): ModelOptionsResponse {
  if (!options.providers?.length) {
    return options
  }

  return {
    ...options,
    providers: filterDesktopModelProviders(options.providers)
  }
}
