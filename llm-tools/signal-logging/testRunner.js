// A simple test runner that takes an object containing test functions as input
// and runs each test, logging the results to the console.
function testRunner(tests) {
  let passed = 0;
  let failed = 0;

  for (const testName in tests) {
    try {
      tests[testName]();
      console.log(`✔️  ${testName}`);
      passed++;
    } catch (error) {
      console.error(`❌ ${testName}\n   ${error.message}`);
      failed++;
    }
  }

  console.log('\n====================');
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log('====================\n');
}

module.exports = testRunner;
