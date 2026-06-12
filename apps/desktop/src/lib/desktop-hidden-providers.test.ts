import { describe, expect, it } from 'vitest'

import {
  filterDesktopModelOptions,
  filterDesktopModelProviders,
  filterDesktopOAuthProviders
} from './desktop-hidden-providers'

describe('desktop-hidden-providers', () => {
  it('filters Nous Portal from OAuth provider lists', () => {
    const providers = [
      { id: 'nous', name: 'Nous Portal' },
      { id: 'anthropic', name: 'Anthropic' }
    ]

    expect(filterDesktopOAuthProviders(providers)).toEqual([{ id: 'anthropic', name: 'Anthropic' }])
  })

  it('filters Nous Portal from model provider lists', () => {
    const providers = [
      { slug: 'nous', name: 'Nous Portal', models: ['hermes-4'] },
      { slug: 'openrouter', name: 'OpenRouter', models: ['anthropic/claude-sonnet-4'] }
    ]

    expect(filterDesktopModelProviders(providers)).toEqual([
      { slug: 'openrouter', name: 'OpenRouter', models: ['anthropic/claude-sonnet-4'] }
    ])
  })

  it('filters model.options payloads', () => {
    expect(
      filterDesktopModelOptions({
        provider: 'nous',
        model: 'hermes-4',
        providers: [
          { slug: 'nous', name: 'Nous Portal', models: ['hermes-4'] },
          { slug: 'deepseek', name: 'DeepSeek', models: ['deepseek-chat'] }
        ]
      })
    ).toEqual({
      provider: 'nous',
      model: 'hermes-4',
      providers: [{ slug: 'deepseek', name: 'DeepSeek', models: ['deepseek-chat'] }]
    })
  })
})
