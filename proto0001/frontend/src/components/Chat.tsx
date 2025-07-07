/*
 * -------------------------------------------------
 * ・ファイル名：Chat.tsx
 * ・ファイル内容：Azure OpenAI チャット画面コンポーネント
 * ・作成日時：2025/07/07 11:58:00  Claude Code
 * -------------------------------------------------
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import './Chat.css';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

interface ChatHistory {
  id: number;
  user_message: string;
  assistant_message: string;
  created_at: string;
}

const Chat: React.FC = () => {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get<{history: ChatHistory[]}>('http://localhost:8000/chat/history');
      setChatHistory(response.data.history);
    } catch (error) {
      console.error('チャット履歴の読み込みエラー:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post<{message: string, timestamp: string}>('http://localhost:8000/chat', {
        messages: [...messages, userMessage],
        max_tokens: 1000,
        temperature: 0.7
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.message,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
      loadChatHistory(); // 履歴を更新
    } catch (error) {
      console.error('チャット送信エラー:', error);
      setError('メッセージの送信に失敗しました。もう一度お試しください。');
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setError('');
  };

  const clearHistory = async () => {
    try {
      await axios.delete('http://localhost:8000/chat/history');
      setChatHistory([]);
      clearChat();
    } catch (error) {
      console.error('履歴削除エラー:', error);
      setError('履歴の削除に失敗しました。');
    }
  };

  const loadHistoryToChat = (history: ChatHistory) => {
    const userMessage: ChatMessage = {
      role: 'user',
      content: history.user_message,
      timestamp: history.created_at
    };
    
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: history.assistant_message,
      timestamp: history.created_at
    };

    setMessages([userMessage, assistantMessage]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('ja-JP');
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>AIチャット</h1>
        <div className="chat-header-buttons">
          <button onClick={clearChat} className="clear-button">
            チャットクリア
          </button>
          <button onClick={clearHistory} className="clear-history-button">
            履歴削除
          </button>
          <button onClick={logout} className="logout-button">
            ログアウト
          </button>
        </div>
      </div>

      <div className="chat-content">
        <div className="chat-sidebar">
          <h3>チャット履歴</h3>
          <div className="history-list">
            {chatHistory.map((history) => (
              <div
                key={history.id}
                className="history-item"
                onClick={() => loadHistoryToChat(history)}
              >
                <div className="history-message">
                  {history.user_message.length > 50 
                    ? `${history.user_message.substring(0, 50)}...` 
                    : history.user_message}
                </div>
                <div className="history-date">
                  {formatTimestamp(history.created_at)}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="chat-main">
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                <h3>Azure OpenAI チャットへようこそ！</h3>
                <p>何でもお気軽にご質問ください。</p>
              </div>
            )}

            {messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  {message.timestamp && (
                    <div className="message-timestamp">
                      {formatTimestamp(message.timestamp)}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="chat-input">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="メッセージを入力してください..."
              disabled={isLoading}
              rows={3}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="send-button"
            >
              {isLoading ? '送信中...' : '送信'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;