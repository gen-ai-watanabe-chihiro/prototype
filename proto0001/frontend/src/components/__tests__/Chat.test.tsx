/*
 * -------------------------------------------------
 * ・ファイル名：Chat.test.tsx
 * ・ファイル内容：チャットコンポーネントの単体テスト
 * ・作成日時：2025/07/07 12:01:00  Claude Code
 * -------------------------------------------------
 */

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Chat from '../Chat';
import { AuthProvider } from '../../contexts/AuthContext';

// axiosのモック
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

const MockedChat = () => (
  <BrowserRouter>
    <AuthProvider>
      <Chat />
    </AuthProvider>
  </BrowserRouter>
);

describe('Chat Component', () => {
  beforeEach(() => {
    // チャット履歴のモック
    mockedAxios.get.mockResolvedValue({
      data: {
        history: [
          {
            id: 1,
            user_message: 'テストメッセージ',
            assistant_message: 'テスト応答',
            created_at: '2025-07-07T12:00:00.000Z'
          }
        ]
      }
    });

    // チャット送信のモック
    mockedAxios.post.mockResolvedValue({
      data: {
        message: 'AIからの応答です',
        timestamp: '2025-07-07T12:00:00.000Z'
      }
    });

    // 履歴削除のモック
    mockedAxios.delete.mockResolvedValue({
      data: {
        message: 'チャット履歴が削除されました'
      }
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('チャット画面が正しく表示される', async () => {
    render(<MockedChat />);
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'AIチャット' })).toBeInTheDocument();
      expect(screen.getByPlaceholderText('メッセージを入力してください...')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: '送信' })).toBeInTheDocument();
    });
  });

  test('ウェルカムメッセージが表示される', async () => {
    render(<MockedChat />);
    
    await waitFor(() => {
      expect(screen.getByText('Azure OpenAI チャットへようこそ！')).toBeInTheDocument();
      expect(screen.getByText('何でもお気軽にご質問ください。')).toBeInTheDocument();
    });
  });

  test('チャット履歴が表示される', async () => {
    render(<MockedChat />);
    
    await waitFor(() => {
      expect(screen.getByText('チャット履歴')).toBeInTheDocument();
      expect(screen.getByText('テストメッセージ')).toBeInTheDocument();
    });
  });

  test('メッセージを送信できる', async () => {
    render(<MockedChat />);
    
    const textarea = screen.getByPlaceholderText('メッセージを入力してください...');
    const sendButton = screen.getByRole('button', { name: '送信' });

    // メッセージを入力
    fireEvent.change(textarea, { target: { value: 'こんにちは' } });
    
    // 送信ボタンをクリック
    fireEvent.click(sendButton);

    // 送信されることを確認
    expect(mockedAxios.post).toHaveBeenCalledWith('http://localhost:8000/chat', expect.objectContaining({
      messages: expect.arrayContaining([
        expect.objectContaining({
          role: 'user',
          content: 'こんにちは'
        })
      ])
    }));
  });

  test('Enterキーでメッセージを送信できる', async () => {
    render(<MockedChat />);
    
    const textarea = screen.getByPlaceholderText('メッセージを入力してください...');

    // メッセージを入力
    fireEvent.change(textarea, { target: { value: 'テストメッセージ' } });
    
    // Enterキーを押す
    fireEvent.keyPress(textarea, { key: 'Enter', code: 'Enter' });

    // 送信されることを確認
    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalled();
    });
  });

  test('チャットクリアボタンが機能する', async () => {
    render(<MockedChat />);
    
    await waitFor(() => {
      const clearButton = screen.getByRole('button', { name: 'チャットクリア' });
      fireEvent.click(clearButton);
      
      // ウェルカムメッセージが再表示されることを確認
      expect(screen.getByText('Azure OpenAI チャットへようこそ！')).toBeInTheDocument();
    });
  });

  test('履歴削除ボタンが機能する', async () => {
    render(<MockedChat />);
    
    await waitFor(() => {
      const clearHistoryButton = screen.getByRole('button', { name: '履歴削除' });
      fireEvent.click(clearHistoryButton);
      
      // DELETE APIが呼ばれることを確認
      expect(mockedAxios.delete).toHaveBeenCalledWith('http://localhost:8000/chat/history');
    });
  });

  test('空のメッセージは送信できない', async () => {
    render(<MockedChat />);
    
    const sendButton = screen.getByRole('button', { name: '送信' });
    
    // 空の状態で送信ボタンが無効化されていることを確認
    expect(sendButton).toBeDisabled();
  });

  test('ログアウトボタンが表示される', async () => {
    render(<MockedChat />);
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'ログアウト' })).toBeInTheDocument();
    });
  });

  test('APIエラー時にエラーメッセージが表示される', async () => {
    mockedAxios.post.mockRejectedValue(new Error('API Error'));
    
    render(<MockedChat />);
    
    const textarea = screen.getByPlaceholderText('メッセージを入力してください...');
    const sendButton = screen.getByRole('button', { name: '送信' });

    // メッセージを入力して送信
    fireEvent.change(textarea, { target: { value: 'テストメッセージ' } });
    fireEvent.click(sendButton);

    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.getByText('メッセージの送信に失敗しました。もう一度お試しください。')).toBeInTheDocument();
    });
  });
});