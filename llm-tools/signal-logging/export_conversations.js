const os = require('os');
const fs = require('fs');
const path = require('path');
const SQL = require('@signalapp/better-sqlite3');

// Get the folder path containing Signal's configuration files
function getFolderPath() {
  return path.join(os.homedir(), '.config/Signal');
}

// Get the database path of Signal's message data
function getDBPath() {
  return path.join(getFolderPath(), 'sql/db.sqlite');
}

// Get the database key required to read Signal's encrypted database
function getDBKey() {
  const config = path.join(getFolderPath(), 'config.json');
  return JSON.parse(fs.readFileSync(config).toString())['key'];
}

const db = SQL(getDBPath(), { readonly: true });
db.pragma(`key = "x'${getDBKey()}'"`);

// Load existing conversation data from a file
function loadExistingConversation(conversationFile) {
  const existingConversationData = JSON.parse(fs.readFileSync(conversationFile).toString());
  return existingConversationData.conversation.map(line => {
    const timestamp = line.match(/\[(\d+)\]/)[1];
    const sender = line.match(/]\s(.*):\s/)[1];
    const body = line.slice(line.indexOf(sender) + sender.length + 2);
    return {
      Timestamp: parseInt(timestamp),
      Sender: sender,
      Body: body
    };
  });
}

// Merge new messages with existing messages, maintaining chronological order and avoiding duplicates
function mergeConversations(existingMessages, newMessages) {
  return [...existingMessages, ...newMessages]
    .sort((a, b) => a.Timestamp - b.Timestamp)
    .filter((msg, idx, self) => idx === 0 || (msg.Timestamp !== self[idx - 1].Timestamp || msg.Body !== self[idx - 1].Body));
}

// Convert the merged messages back to the original file format
function formatConversationData(mergedMessages) {
  return {
    "content-type": "conversation-v1",
    "conversation": mergedMessages.map(
      (message) => `[${message.Timestamp}] ${message.Sender}: ${message.Body}`
    ),
  };
}

// Save the formatted conversation data to a file
function saveConversationToFile(conversationFile, conversationData) {
  fs.writeFileSync(
    conversationFile,
    JSON.stringify(conversationData, null, 2)
  );
}

// Process the messages and output them to the 'conversations' folder
function outputConversations(messages) {
  const conversations = {};

  // Iterate through each message and sort by conversationId.
  messages.forEach((message) => {
    if (message.body !== null) {
      if (!conversations[message.conversationId]) {
        conversations[message.conversationId] = [];
      }

      const senderName =
        message.profileFullName || message.profileName || message.name || message.source || message.sourceUuid || "Taek";

      conversations[message.conversationId].push({
        Timestamp: Math.floor(message.sent_at / 1000), // Convert milliseconds to seconds
        Sender: senderName,
        Body: message.body,
      });
    }
  });

  const outputFolder = 'conversations';
  if (!fs.existsSync(outputFolder)) {
    fs.mkdirSync(outputFolder);
  }

  // Process each conversation
  Object.entries(conversations).forEach(([conversationId, newMessages]) => {
    if (newMessages.length > 0) {
      const conversationFile = path.join(outputFolder, `${conversationId}.json`);

      let existingMessages = [];
      // If a conversation file already exists, load the existing messages
      if (fs.existsSync(conversationFile)) {
        existingMessages = loadExistingConversation(conversationFile);
      }

      // Merge the new messages with existing messages, maintaining order and avoiding duplicates
      const mergedMessages = mergeConversations(existingMessages, newMessages);

      // Format the merged messages back to the original file structure
      const conversationData = formatConversationData(mergedMessages);

      // Save the formatted conversation data to the file
      saveConversationToFile(conversationFile, conversationData);
    }
  });
}

const messagesWithSenderInfo = db.prepare(`
  SELECT
    messages.rowid,
    messages.sent_at,
    messages.source,
    messages.sourceUuid,
    messages.body,
    messages.conversationId,
    conversations.name,
    conversations.profileName,
    conversations.profileFamilyName,
    conversations.profileFullName
  FROM messages
  LEFT JOIN conversations
    ON (messages.source = conversations.e164 OR messages.sourceUuid = conversations.uuid)
  ORDER BY messages.sent_at ASC
`).all();

outputConversations(messagesWithSenderInfo);

module.exports = {
  loadExistingConversation,
  mergeConversations,
  formatConversationData,
};
