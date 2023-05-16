const fs = require('fs');
const path = require('path');
const {
  loadExistingConversation,
  mergeConversations,
  formatConversationData,
} = require('./export_conversations');
const testRunner = require('./testRunner');

// Test if the loadExistingConversation function correctly loads conversation data from a file
function testLoadExistingConversation() {
  // Prepare a temporary test file
  const tempFilePath = path.join(__dirname, 'temp_test_conversation.json');
  const testData = {
    'content-type': 'conversation-v1',
    'conversation': [
      '[1612211200] Alice: Hi!',
      '[1612211201] Bob: Hello!',
    ],
  };

  fs.writeFileSync(tempFilePath, JSON.stringify(testData, null, 2));

  // Load the conversation from the temporary file
  const conversationData = loadExistingConversation(tempFilePath);

  // Remove the temporary test file
  fs.unlinkSync(tempFilePath);

  // Expected data structure after loading the conversation
  const expectedData = [
    {
      Timestamp: 1612211200,
      Sender: 'Alice',
      Body: 'Hi!',
    },
    {
      Timestamp: 1612211201,
      Sender: 'Bob',
      Body: 'Hello!',
    },
  ];

  if (JSON.stringify(conversationData) !== JSON.stringify(expectedData)) {
    console.log(JSON.stringify(conversationData))
    console.log(JSON.stringify(expectedData))
    throw new Error('Loaded conversation data does not match the expected data');
  }
}

// Test if the mergeConversations function correctly merges two sets of messages,
// maintaining chronological order and avoiding duplicates
function testMergeConversations() {
  // Prepare existing messages and new messages to be merged
  const existingMessages = [
    {
      Timestamp: 1612211200,
      Sender: 'Alice',
      Body: 'Hi!',
    },
    {
      Timestamp: 1612211201,
      Sender: 'Bob',
      Body: 'Hello!',
    },
  ];

  const newMessages = [
    {
      Timestamp: 1612211202,
      Sender: 'Alice',
      Body: 'How are you?',
    },
    {
      Timestamp: 1612211201,
      Sender: 'Bob',
      Body: 'Hello!',
    },
  ];

  // Call the function and check if the merged messages match the expected merged messages
  const mergedMessages = mergeConversations(existingMessages, newMessages);

  const expectedMergedMessages = [
    {
      Timestamp: 1612211200, // Timestamp in seconds
      Sender: 'Alice',
      Body: 'Hi!',
    },
    {
      Timestamp: 1612211201, // Timestamp in seconds
      Sender: 'Bob',
      Body: 'Hello!',
    },
    {
      Timestamp: 1612211202, // Timestamp in seconds
      Sender: 'Alice',
      Body: 'How are you?',
    },
  ];
  
  if (JSON.stringify(mergedMessages) !== JSON.stringify(expectedMergedMessages)) {
    throw new Error('Merged messages do not match the expected merged messages');
  }
}

// Test if the formatConversationData function correctly formats the merged messages
// back to the original file structure
function testFormatConversationData() {
  // Prepare merged messages for formatting
  const mergedMessages = [
    {
      Timestamp: 1612211200,
      Sender: 'Alice',
      Body: 'Hi!',
    },
    {
      Timestamp: 1612211201,
      Sender: 'Bob',
      Body: 'Hello!',
    },
  ];

  // Call the function and check if the formatted data matches the expected data
  const conversationData = formatConversationData(mergedMessages);

  const expectedData = {
    'content-type': 'conversation-v1',
    'conversation': [
      '[1612211200] Alice: Hi!',
      '[1612211201] Bob: Hello!',
    ],
  };

  if (JSON.stringify(conversationData) !== JSON.stringify(expectedData)) {
    throw new Error('Formatted conversation data does not match the expected data');
  }
}

// Define all tests to run
const tests = {
  'loadExistingConversation should load conversation data from file': testLoadExistingConversation,
  'mergeConversations should merge conversations while maintaining order and avoiding duplicates': testMergeConversations,
  'formatConversationData should format merged messages back to the original file structure': testFormatConversationData,
};

// Run the tests using the test runner
testRunner(tests);
