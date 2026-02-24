#!/usr/bin/env node
/**
 * Frontend test runner script
 * Runs all frontend tests and generates coverage reports
 */

import { spawn } from 'child_process'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)
const projectRoot = join(__dirname, '../..')

function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'inherit',
      cwd: projectRoot,
      ...options
    })

    child.on('close', (code) => {
      if (code === 0) {
        resolve()
      } else {
        reject(new Error(`Command failed with exit code ${code}`))
      }
    })
  })
}

async function runTests() {
  console.log('🧪 Running Frontend Tests')
  console.log('=' .repeat(50))

  try {
    // Install dependencies if needed
    console.log('📦 Installing dependencies...')
    await runCommand('npm', ['install'])

    // Run tests
    console.log('\n🔬 Running tests...')
    await runCommand('npm', ['run', 'test', '--', '--run'])

    console.log('\n✅ All tests passed!')
    
    // Generate coverage report
    console.log('\n📊 Generating coverage report...')
    await runCommand('npm', ['run', 'test:coverage', '--', '--run'])
    
    console.log('📊 Coverage report generated in coverage/index.html')

  } catch (error) {
    console.error('\n❌ Tests failed!')
    console.error(error.message)
    process.exit(1)
  }
}

async function runSpecificTest(testPath) {
  console.log(`🧪 Running specific test: ${testPath}`)
  
  try {
    await runCommand('npm', ['run', 'test', '--', testPath, '--run'])
    console.log('\n✅ Test passed!')
  } catch (error) {
    console.error('\n❌ Test failed!')
    console.error(error.message)
    process.exit(1)
  }
}

// Main execution
const testPath = process.argv[2]
if (testPath) {
  runSpecificTest(testPath)
} else {
  runTests()
}