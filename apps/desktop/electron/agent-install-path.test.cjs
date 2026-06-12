'use strict'

const assert = require('node:assert/strict')
const test = require('node:test')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')

const {
  PREFERRED_INSTALL_DIR,
  LEGACY_INSTALL_DIR,
  resolveAgentInstallRoot
} = require('./agent-install-path.cjs')

function mkTmpHome() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'berdaya-install-path-'))
}

test('resolveAgentInstallRoot defaults to berdaya-agent for fresh installs', () => {
  const home = mkTmpHome()
  try {
    assert.equal(resolveAgentInstallRoot(home), path.join(home, PREFERRED_INSTALL_DIR))
  } finally {
    fs.rmSync(home, { recursive: true, force: true })
  }
})

test('resolveAgentInstallRoot prefers berdaya-agent when both exist', () => {
  const home = mkTmpHome()
  try {
    fs.mkdirSync(path.join(home, LEGACY_INSTALL_DIR))
    fs.mkdirSync(path.join(home, PREFERRED_INSTALL_DIR))
    assert.equal(resolveAgentInstallRoot(home), path.join(home, PREFERRED_INSTALL_DIR))
  } finally {
    fs.rmSync(home, { recursive: true, force: true })
  }
})

test('resolveAgentInstallRoot falls back to legacy hermes-agent', () => {
  const home = mkTmpHome()
  try {
    fs.mkdirSync(path.join(home, LEGACY_INSTALL_DIR))
    assert.equal(resolveAgentInstallRoot(home), path.join(home, LEGACY_INSTALL_DIR))
  } finally {
    fs.rmSync(home, { recursive: true, force: true })
  }
})
