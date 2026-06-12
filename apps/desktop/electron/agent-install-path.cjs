'use strict'

const fs = require('node:fs')
const path = require('node:path')

const PREFERRED_INSTALL_DIR = 'berdaya-agent'
const LEGACY_INSTALL_DIR = 'hermes-agent'

/** Checkout under Berdaya home — prefer berdaya-agent, fall back to legacy hermes-agent. */
function resolveAgentInstallRoot(hermesHome) {
  const preferred = path.join(hermesHome, PREFERRED_INSTALL_DIR)
  const legacy = path.join(hermesHome, LEGACY_INSTALL_DIR)
  try {
    if (fs.existsSync(preferred)) return preferred
    if (fs.existsSync(legacy)) return legacy
  } catch {
    // ignore fs errors — default to preferred for fresh installs
  }
  return preferred
}

module.exports = {
  LEGACY_INSTALL_DIR,
  PREFERRED_INSTALL_DIR,
  resolveAgentInstallRoot
}
